import cv2
import threading
import time
import logging
import os
import platform
from typing import List, Dict, Optional, Tuple, Union
import numpy as np
from sqlalchemy.orm import Session
from threading import RLock, Condition
from dataclasses import dataclass
from threading import Event

logger = logging.getLogger(__name__)

# Set environment variable for macOS to handle camera authorization correctly
if platform.system() == 'Darwin':  # Check if running on macOS
    os.environ['OPENCV_AVFOUNDATION_SKIP_AUTH'] = '1'
    print("Running on macOS: Set OPENCV_AVFOUNDATION_SKIP_AUTH=1 for camera access")

@dataclass
class CameraInfo:
    """摄像头信息的数据类"""
    device_id: Union[int, str]
    cap: cv2.VideoCapture
    is_streaming: bool = False
    thread: Optional[threading.Thread] = None
    last_frame: Optional[bytes] = None
    last_error: Optional[str] = None
    clients: int = 0
    status: str = 'online'
    source_type: str = 'local'

class ProcessedStream:
    """处理流的封装类，用于管理处理流的状态和资源"""
    def __init__(self, camera_id: str, operation_id: int, operation_type: str, db: Session):
        self.camera_id = camera_id
        self.operation_id = operation_id
        self.operation_type = operation_type
        self.is_streaming = True
        self.last_frame = None
        self.last_error = None
        self._clients = 0
        self._clients_lock = threading.Lock()
        self.db_session = db
        self.start_time = time.time()
        self.frame_count = 0
        self._frame_lock = threading.Lock()
        self.last_frame_time = time.time()
        self._stop_event = Event()

    def increment_clients(self) -> int:
        """增加客户端计数，返回新的计数值"""
        with self._clients_lock:
            self._clients += 1
            return self._clients

    def decrement_clients(self) -> int:
        """减少客户端计数，返回新的计数值"""
        with self._clients_lock:
            self._clients = max(0, self._clients - 1)
            return self._clients

    @property
    def clients(self) -> int:
        """获取当前客户端数量"""
        with self._clients_lock:
            return self._clients

    def update_frame(self, frame: bytes):
        """更新最后处理的帧"""
        with self._frame_lock:
            self.last_frame = frame
            self.frame_count += 1
            self.last_frame_time = time.time()

    def get_stats(self):
        """获取流统计信息"""
        current_time = time.time()
        with self._frame_lock:
            duration = current_time - self.start_time
            fps = self.frame_count / duration if duration > 0 else 0
            return {
                'clients': self.clients,
                'frame_count': self.frame_count,
                'fps': fps,
                'duration': duration,
                'last_frame_age': current_time - self.last_frame_time
            }

    def cleanup(self):
        """清理资源"""
        self._stop_event.set()
        if self.db_session:
            try:
                self.db_session.close()
            except Exception as e:
                logger.error(f"Error closing db session: {str(e)}")
        self.is_streaming = False

class FrameProcessor:
    """帧处理器类，用于处理图像操作和转换"""
    
    def __init__(self, db: Session):
        self.db = db
        self._cv_operation_service = None
        self._pipeline_service = None
        
    @property
    def cv_operation_service(self):
        """懒加载CV操作服务"""
        if self._cv_operation_service is None:
            from .cv_operation import CVOperationService
            self._cv_operation_service = CVOperationService(self.db)
        return self._cv_operation_service
        
    @property
    def pipeline_service(self):
        """懒加载Pipeline服务"""
        if self._pipeline_service is None:
            from .pipeline import PipelineService
            self._pipeline_service = PipelineService(self.db)
        return self._pipeline_service

    def decode_frame(self, frame_data: bytes) -> Optional[np.ndarray]:
        """将JPEG帧数据解码为numpy数组"""
        if not frame_data or len(frame_data) == 0:
            logger.error("解码帧失败: 空的帧数据")
            return None
            
        try:
            img_array = np.frombuffer(frame_data, dtype=np.uint8)
            if img_array.size == 0:
                logger.error("解码帧失败: 帧数据为空数组")
                return None
                
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            if img is None:
                logger.error(f"无法解码输入图像，数据大小: {len(frame_data)} 字节")
                return None
                
            logger.debug(f"成功解码图像，尺寸: {img.shape}")
            return img
        except ValueError as e:
            logger.error(f"解码帧值错误: {str(e)}")
            return None
        except TypeError as e:
            logger.error(f"解码帧类型错误: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"解码帧未知错误: {str(e)}")
            return None

    def encode_frame(self, frame: np.ndarray, quality: int = 95) -> Optional[bytes]:
        """将numpy数组编码为JPEG字节数据"""
        try:
            # 添加一个适当的保护机制，确保frame是有效的可编码输入
            if frame is None:
                logger.error("编码帧失败: 输入为None")
                return None
                
            # 尝试编码帧
            try:
                _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, quality])
                return buffer.tobytes()
            except TypeError as e:
                # 可能的类型错误 - 尝试一些常见的转换
                logger.warning(f"编码帧类型错误: {str(e)}, 尝试转换")
                
                if isinstance(frame, bytes):
                    # 如果已经是字节，可能是JPEG数据，直接返回
                    logger.info("输入已经是字节类型，直接返回")
                    return frame
                    
                if hasattr(frame, 'tobytes') and callable(getattr(frame, 'tobytes')):
                    # 如果有tobytes方法(如某些numpy数组)，尝试使用
                    logger.info("使用tobytes方法转换输入")
                    return frame.tobytes()
                    
                # 其他情况，作为错误处理
                raise
                
        except Exception as e:
            logger.error(f"编码帧失败: {str(e)}")
            return None

    def get_image_param_name(self, params: List[Dict], default: str = 'image') -> str:
        """从参数列表中获取图像参数名"""
        for param in params:
            if param.get('type') == 'image':
                return param['name']
        return params[0]['name'] if params else default

    def process_operation(self, img: np.ndarray, operation_id: int) -> Optional[np.ndarray]:
        """处理单个CV操作"""
        try:
            operation = self.cv_operation_service.get_operation(operation_id)
            if not operation:
                logger.error(f"未找到操作 {operation_id}")
                return None

            input_param_name = self.get_image_param_name(operation.input_params)
            result = self.cv_operation_service.apply_operation(operation_id, {input_param_name: img})

            # 查找输出图像
            if operation.output_params:
                output_param_name = self.get_image_param_name(operation.output_params)
                if output_param_name in result:
                    return result[output_param_name]

            # 回退到查找第一个numpy数组
            for value in result.values():
                if isinstance(value, np.ndarray):
                    return value

            return None
        except Exception as e:
            logger.error(f"处理操作失败: {str(e)}")
            return None

    def process_pipeline(self, img: np.ndarray, pipeline_id: int) -> Optional[np.ndarray]:
        """处理Pipeline操作"""
        try:
            pipeline = self.pipeline_service.get_pipeline(pipeline_id)
            if not pipeline:
                logger.error(f"未找到Pipeline {pipeline_id}")
                return None

            input_param_name = self.get_image_param_name(pipeline.input_params)
            result = self.pipeline_service.apply_pipeline(pipeline_id, {input_param_name: img})

            output_params = result.get('outputParams', {})
            if pipeline.output_params:
                output_param_name = self.get_image_param_name(pipeline.output_params)
                if output_param_name in output_params:
                    return output_params[output_param_name]

            # 回退到查找第一个numpy数组
            for value in output_params.values():
                if isinstance(value, np.ndarray):
                    return value

            return None
        except Exception as e:
            logger.error(f"处理Pipeline失败: {str(e)}")
            return None

    def process_frame(self, frame_data: bytes, operation_id: int, operation_type: str) -> bytes:
        """处理单帧并返回处理后的JPEG数据"""
        try:
            # 解码输入帧
            img = self.decode_frame(frame_data)
            if img is None:
                logger.warning(f"无法解码输入帧，返回原始帧数据")
                return frame_data

            # 根据操作类型处理图像
            processed_img = None
            try:
                if operation_type == 'operation':
                    logger.debug(f"应用操作 {operation_id} 到帧")
                    processed_img = self.process_operation(img, operation_id)
                    if processed_img is None:
                        logger.warning(f"操作 {operation_id} 处理返回空结果，回退到原始帧")
                elif operation_type == 'pipeline':
                    logger.debug(f"应用流水线 {operation_id} 到帧")
                    processed_img = self.process_pipeline(img, operation_id)
                    if processed_img is None:
                        logger.warning(f"流水线 {operation_id} 处理返回空结果，回退到原始帧")
                else:
                    logger.warning(f"未知的操作类型: {operation_type}，回退到原始帧")
            except Exception as e:
                logger.error(f"处理帧时发生错误: {str(e)}，回退到原始帧")
                return frame_data

            # 如果处理成功，编码并返回结果
            if processed_img is not None:
                try:
                    result = self.encode_frame(processed_img)
                    if result is not None:
                        logger.debug(f"成功处理并编码帧 ({len(result)} 字节)")
                        return result
                    else:
                        logger.warning("编码处理后的帧失败，回退到原始帧")
                except Exception as e:
                    logger.error(f"编码处理后的帧时发生错误: {str(e)}，回退到原始帧")

            # 处理失败时返回原始帧
            logger.debug("处理流程未产生有效结果，返回原始帧")
            return frame_data
        except Exception as e:
            logger.exception(f"处理帧失败: {str(e)}")
            # 确保在任何错误情况下都返回原始帧
            return frame_data

class FrameBuffer:
    """帧缓存管理器，用于优化帧的存储和访问"""
    
    def __init__(self, max_size: int = 30):
        self.max_size = max_size
        self._frames: Dict[str, Dict] = {}  # camera_id -> {'frame': bytes, 'timestamp': float}
        self._processed_frames: Dict[str, Dict] = {}  # stream_key -> {'frame': bytes, 'timestamp': float}
        self._frames_lock = RLock()  # 保护原始帧字典
        self._processed_frames_lock = RLock()  # 保护处理后帧字典
        self._cleanup_event = Event()
        self._start_cleanup_thread()

    def _start_cleanup_thread(self):
        """启动清理线程"""
        def cleanup():
            while not self._cleanup_event.is_set():
                try:
                    self._cleanup_old_frames()
                except Exception as e:
                    logger.error(f"Frame buffer cleanup error: {str(e)}")
                time.sleep(5)  # 每5秒清理一次

        thread = threading.Thread(target=cleanup, daemon=True)
        thread.start()

    def _cleanup_old_frames(self):
        """清理过期的帧"""
        current_time = time.time()
        
        # 清理原始帧
        with self._frames_lock:
            for camera_id in list(self._frames.keys()):
                if current_time - self._frames[camera_id]['timestamp'] > 1.0:  # 1秒过期
                    del self._frames[camera_id]
        
        # 清理处理后的帧
        with self._processed_frames_lock:
            for stream_key in list(self._processed_frames.keys()):
                if current_time - self._processed_frames[stream_key]['timestamp'] > 1.0:
                    del self._processed_frames[stream_key]

    def update_frame(self, camera_id: str, frame: bytes) -> None:
        """更新摄像头原始帧"""
        with self._frames_lock:
            self._frames[camera_id] = {
                'frame': frame,
                'timestamp': time.time()
            }

    def get_frame(self, camera_id: str) -> Tuple[bool, bytes]:
        """获取摄像头原始帧"""
        with self._frames_lock:
            frame_data = self._frames.get(camera_id)
            if frame_data and time.time() - frame_data['timestamp'] <= 1.0:
                return True, frame_data['frame']
        return False, b''

    def update_processed_frame(self, stream_key: str, frame: bytes) -> None:
        """更新处理后的帧"""
        with self._processed_frames_lock:
            self._processed_frames[stream_key] = {
                'frame': frame,
                'timestamp': time.time()
            }

    def get_processed_frame(self, stream_key: str) -> Tuple[bool, bytes]:
        """获取处理后的帧"""
        with self._processed_frames_lock:
            frame_data = self._processed_frames.get(stream_key)
            if frame_data and time.time() - frame_data['timestamp'] <= 1.0:
                return True, frame_data['frame']
        return False, b''

    def cleanup(self):
        """清理资源"""
        self._cleanup_event.set()
        with self._frames_lock:
            self._frames.clear()
        with self._processed_frames_lock:
            self._processed_frames.clear()

class CameraService:
    def __init__(self):
        # 细粒度锁
        self._cameras_lock = RLock()  # 用于保护cameras字典
        self._streams_lock = RLock()  # 用于保护processed_streams字典
        self._processors_lock = RLock()  # 用于保护frame_processors字典
        
        # 条件变量，用于帧更新通知
        self._frame_condition = Condition()
        
        # 受保护的资源
        self._cameras: Dict[str, CameraInfo] = {}
        self._processed_streams: Dict[str, ProcessedStream] = {}
        self._frame_processors: Dict[int, 'FrameProcessor'] = {}
        
        # 帧缓冲
        self.frame_buffer = FrameBuffer()
        
        # 启动清理线程
        self._cleanup_event = Event()
        self._start_cleanup_thread()

    def _start_cleanup_thread(self):
        """启动清理线程，定期检查和清理无效的流和资源"""
        def cleanup():
            while True:
                try:
                    self._cleanup_resources()
                except Exception as e:
                    logger.error(f"Resource cleanup error: {str(e)}")
                time.sleep(5)  # 每5秒清理一次

        thread = threading.Thread(target=cleanup, daemon=True)
        thread.start()

    def _cleanup_resources(self):
        """清理无效的摄像头和处理流"""
        with self._cameras_lock:
            # 清理无效的摄像头
            for camera_id in list(self._cameras.keys()):
                try:
                    camera = self._cameras[camera_id]
                    if not camera.cap.isOpened():
                        logger.warning(f"Found dead camera {camera_id}, cleaning up")
                        self._force_cleanup_camera(camera_id)
                except Exception as e:
                    logger.error(f"Error checking camera {camera_id}: {str(e)}")
                    self._force_cleanup_camera(camera_id)

            # 清理无效的处理流
            for stream_key in list(self._processed_streams.keys()):
                try:
                    stream = self._processed_streams[stream_key]
                    if not stream.is_streaming or stream.clients <= 0:
                        logger.warning(f"Found dead stream {stream_key}, cleaning up")
                        self._force_cleanup_stream(stream_key)
                except Exception as e:
                    logger.error(f"Error checking stream {stream_key}: {str(e)}")
                    self._force_cleanup_stream(stream_key)

            # 清理过期的帧处理器
            current_time = time.time()
            for db_id in list(self._frame_processors.keys()):
                processor = self._frame_processors[db_id]
                if not hasattr(processor, 'last_used'):
                    processor.last_used = current_time
                elif current_time - processor.last_used > 300:  # 5分钟未使用
                    del self._frame_processors[db_id]

    def _force_cleanup_camera(self, camera_id: str):
        """强制清理摄像头资源"""
        try:
            with self._cameras_lock:
                if camera_id in self._cameras:
                    camera = self._cameras[camera_id]
                    if camera.is_streaming:
                        camera.is_streaming = False
                    if camera.thread and camera.thread.is_alive():
                        camera.thread.join(timeout=0.5)
                    camera.cap.release()
                    del self._cameras[camera_id]
        except Exception as e:
            logger.error(f"Error during force cleanup of camera {camera_id}: {str(e)}")
        finally:
            if camera_id in self._cameras:
                del self._cameras[camera_id]

    def _force_cleanup_stream(self, stream_key: str):
        """强制清理处理流资源"""
        try:
            logger.info(f"开始强制清理处理流: {stream_key}")
            
            with self._streams_lock:
                if stream_key in self._processed_streams:
                    try:
                        # 获取流信息并记录
                        stream = self._processed_streams[stream_key]
                        camera_id = stream.camera_id
                        operation_id = stream.operation_id
                        operation_type = stream.operation_type
                        
                        logger.info(f"清理处理流: camera={camera_id}, operation_id={operation_id}, type={operation_type}")
                        
                        # 清理流资源
                        stream.is_streaming = False
                        
                        # 关闭数据库会话
                        try:
                            if hasattr(stream, 'db_session') and stream.db_session:
                                stream.db_session.close()
                                logger.info(f"已关闭流 {stream_key} 的数据库会话")
                        except Exception as e:
                            logger.error(f"关闭流 {stream_key} 的数据库会话时出错: {str(e)}")
                        
                        # 清理其它资源
                        stream.cleanup()
                        
                        # 从字典中删除
                        del self._processed_streams[stream_key]
                        logger.info(f"已完成处理流 {stream_key} 的强制清理")
                    except Exception as e:
                        logger.error(f"清理流 {stream_key} 的资源时出错: {str(e)}")
                        # 即使遇到错误，也要确保从字典中删除
                        if stream_key in self._processed_streams:
                            del self._processed_streams[stream_key]
                else:
                    logger.warning(f"找不到要清理的处理流: {stream_key}")
            
            # 清理相关的帧缓存
            try:
                # 使用正确的锁来清理处理流的帧缓存
                with self.frame_buffer._processed_frames_lock:
                    if stream_key in self.frame_buffer._processed_frames:
                        del self.frame_buffer._processed_frames[stream_key]
                        logger.info(f"已清理处理流 {stream_key} 的帧缓存")
            except Exception as e:
                logger.error(f"清理流 {stream_key} 的帧缓存时出错: {str(e)}")
                
        except Exception as e:
            logger.error(f"强制清理处理流 {stream_key} 时发生错误: {str(e)}")
            # 最后尝试删除，确保不留残余
            try:
                if stream_key in self._processed_streams:
                    del self._processed_streams[stream_key]
            except:
                pass

    def detect_cameras(self) -> List[Dict]:
        """
        检测系统中可用的摄像头
        """
        detected_cameras = []
        
        # 尝试使用OpenCV检测摄像头
        for i in range(1):  # 检查前10个索引
            try:
                # On macOS, be more careful with camera initialization
                print(f"Attempting to detect camera at index {i}...")
                cap = cv2.VideoCapture(i)
                
                # Give it a moment to initialize
                time.sleep(0.5)
                
                if cap.isOpened():
                    print(f"Camera {i} detected and opened successfully")
                    # 获取摄像头信息
                    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    fps = int(cap.get(cv2.CAP_PROP_FPS))
                    
                    # 读取一帧以确认摄像头工作正常
                    ret, frame = cap.read()
                    if ret:
                        print(f"Successfully read frame from camera {i}")
                        detected_cameras.append({
                            'device_id': i,
                            'name': f'Camera {i}',
                            'type': 'camera',
                            'model': 'USB Camera',
                            'status': 'online',
                            'config': {
                                'resolution': f'{width}x{height}',
                                'fps': fps,
                                'format': 'MJPEG',
                                'source': f'device:{i}'
                            }
                        })
                    else:
                        print(f"Failed to read frame from camera {i}")
                else:
                    print(f"Camera {i} couldn't be opened")
                
                # Properly release the camera
                cap.release()
                time.sleep(0.5)  # Give it time to properly close
                
            except Exception as e:
                logger.error(f"Error detecting camera at index {i}: {str(e)}")
                print(f"Exception while detecting camera {i}: {str(e)}")
                
        # If no cameras detected, try with direct system commands on macOS
        if not detected_cameras and platform.system() == 'Darwin':
            try:
                import subprocess
                result = subprocess.run(['system_profiler', 'SPCameraDataType'], capture_output=True, text=True)
                if 'Camera' in result.stdout:
                    print("System detected camera via system_profiler, but OpenCV couldn't access it")
                    # Add a placeholder camera - the user will need to grant permissions
                    detected_cameras.append({
                        'device_id': 0,
                        'name': 'System Camera (Needs Permission)',
                        'type': 'camera',
                        'model': 'Built-in Camera',
                        'status': 'offline',
                        'config': {
                            'resolution': '1280x720',
                            'fps': 30,
                            'format': 'MJPEG',
                            'source': 'device:0'
                        }
                    })
            except Exception as e:
                print(f"Error checking system cameras: {str(e)}")
                
        return detected_cameras
    
    def open_camera(self, camera_id: str, device_id: Union[int, str]) -> bool:
        """
        打开摄像头
        camera_id: 系统内部摄像头ID
        device_id: 设备ID（可以是本地摄像头索引或URL字符串）
        """
        logger.info(f"尝试打开摄像头: {camera_id}, 设备ID: {device_id}, 系统: {platform.system()}")
        
        with self._cameras_lock:
            if camera_id in self._cameras:
                # 检查现有摄像头是否仍然可用
                cap = self._cameras[camera_id].cap
                if cap.isOpened():
                    logger.info(f"摄像头 {camera_id} 已经打开")
                    return True
                else:
                    # 尝试重新打开
                    logger.warning(f"摄像头 {camera_id} 连接已断开，尝试重新连接")
                    # 确保关闭现有实例
                    try:
                        cap.release()
                    except Exception as e:
                        logger.error(f"关闭现有摄像头时出错: {str(e)}")
                    
            try:
                logger.info(f"尝试打开摄像头 {device_id}")
                
                # 处理不同类型的设备ID
                if isinstance(device_id, int) or (isinstance(device_id, str) and device_id.isdigit()):
                    # 本地摄像头
                    numeric_id = int(device_id)
                    
                    # 在macOS上，添加额外的摄像头初始化参数
                    if platform.system() == 'Darwin':
                        logger.info(f"在macOS上打开摄像头: {numeric_id}")
                        # 确保环境变量设置正确
                        os.environ['OPENCV_AVFOUNDATION_SKIP_AUTH'] = '1'
                        
                        # 先清除可能存在的相同索引摄像头实例
                        try:
                            dummy_cap = cv2.VideoCapture(numeric_id, cv2.CAP_AVFOUNDATION)
                            dummy_cap.release()
                            time.sleep(0.5)  # 给系统一些时间释放资源
                        except Exception as e:
                            logger.warning(f"预清理摄像头时出错: {str(e)}")
                            
                        # 使用明确的后端
                        cap = cv2.VideoCapture(numeric_id, cv2.CAP_AVFOUNDATION)
                        source_type = "local"
                        
                        # 增加初始化延迟
                        time.sleep(1.5)  # 在macOS上等待更长时间
                    else:
                        cap = cv2.VideoCapture(numeric_id)
                        source_type = "local"
                        time.sleep(0.5)
                elif isinstance(device_id, str):
                    # URL类型摄像头
                    if device_id.startswith(("rtsp://", "http://", "https://")):
                        logger.info(f"打开网络摄像头: {device_id}")
                        cap = cv2.VideoCapture(device_id)
                        source_type = "external"
                        time.sleep(0.5)
                    else:
                        # 尝试作为本地摄像头索引
                        try:
                            numeric_id = int(device_id)
                            logger.info(f"将字符串 {device_id} 转换为数字索引: {numeric_id}")
                            
                            if platform.system() == 'Darwin':
                                cap = cv2.VideoCapture(numeric_id, cv2.CAP_AVFOUNDATION)
                                time.sleep(1.5)
                            else:
                                cap = cv2.VideoCapture(numeric_id)
                                time.sleep(0.5)
                            source_type = "local"
                        except ValueError:
                            raise ValueError(f"无效的设备ID格式: {device_id}")
                else:
                    raise ValueError(f"无效的设备ID类型: {type(device_id)}")
                
                # 检查摄像头是否打开
                if not cap.isOpened():
                    logger.error(f"无法打开摄像头 {device_id}")
                    
                    # 在macOS上尝试特殊方法
                    if platform.system() == 'Darwin' and (isinstance(device_id, int) or 
                                                        (isinstance(device_id, str) and device_id.isdigit())):
                        logger.info("在macOS上尝试交替的摄像头初始化方法")
                        try:
                            # 尝试不同的捕获标志
                            cap = cv2.VideoCapture(int(device_id))  # 不带特殊标志
                            time.sleep(1.0)
                            if not cap.isOpened():
                                logger.warning("尝试默认后端失败，尝试其他后端")
                                cap = cv2.VideoCapture(int(device_id), cv2.CAP_ANY)
                                time.sleep(1.0)
                        except Exception as e:
                            logger.error(f"交替初始化方法出错: {str(e)}")
                    
                    if not cap.isOpened():
                        return False
                
                # 设置摄像头参数
                logger.info(f"摄像头 {device_id} 已打开，配置参数")
                
                # 尝试设置各种属性
                try:
                    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # 减少缓冲区大小
                except Exception as e:
                    logger.warning(f"设置缓冲区大小失败: {str(e)}")
                    
                try:
                    cap.set(cv2.CAP_PROP_FPS, 30)  # 设置帧率
                except Exception as e:
                    logger.warning(f"设置帧率失败: {str(e)}")
                    
                # 尝试设置分辨率
                try:
                    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                except Exception as e:
                    logger.warning(f"设置分辨率失败: {str(e)}")
                
                # 读取一帧以确认摄像头工作正常
                retry_count = 0
                max_retries = 5  # 增加重试次数
                while retry_count < max_retries:
                    logger.info(f"尝试从摄像头 {device_id} 读取测试帧 ({retry_count+1}/{max_retries})")
                    ret, _ = cap.read()
                    if ret:
                        logger.info(f"成功从摄像头 {device_id} 读取测试帧")
                        break
                    retry_count += 1
                    time.sleep(0.2)  # 增加重试间隔
                
                if not ret:
                    logger.error(f"摄像头 {device_id} 无法读取帧，最后尝试重置")
                    # 最后尝试重置
                    try:
                        cap.release()
                        time.sleep(1.0)
                        if platform.system() == 'Darwin':
                            cap = cv2.VideoCapture(int(device_id) if isinstance(device_id, str) and device_id.isdigit() else device_id, 
                                                 cv2.CAP_AVFOUNDATION)
                        else:
                            cap = cv2.VideoCapture(int(device_id) if isinstance(device_id, str) and device_id.isdigit() else device_id)
                        time.sleep(1.0)
                        ret, _ = cap.read()
                        if not ret:
                            logger.error(f"重置后仍然无法读取帧，放弃尝试")
                            cap.release()
                            return False
                    except Exception as e:
                        logger.error(f"最后重置尝试失败: {str(e)}")
                        return False
                    
                logger.info(f"成功打开摄像头 {device_id}")
                self._cameras[camera_id] = CameraInfo(device_id, cap, source_type=source_type)
                
                # 尝试更新对应设备的状态
                try:
                    from .settings import SettingsService
                    from ..models.base import SessionLocal
                    db = SessionLocal()
                    settings_service = SettingsService(db)
                    
                    # 查找设备ID
                    devices = settings_service.get_devices()
                    for device in devices:
                        if device.type == 'camera':
                            source = device.config.get('source') if device.config else None
                            if source:
                                if (source == f'device:{device_id}' or 
                                    (source.startswith(('rtsp://', 'http://')) and source == device_id)):
                                    settings_service.update_device_status(device.id, 'online')
                                    logger.info(f"已更新设备ID {device.id} ({device.name}) 状态为online")
                                    break
                    
                    db.close()
                except Exception as e:
                    logger.error(f"尝试更新设备状态时出错: {str(e)}")
                
                return True
            except Exception as e:
                logger.exception(f"打开摄像头 {device_id} 出错: {str(e)}")
                return False
    
    def close_camera(self, camera_id: str) -> bool:
        """
        关闭指定ID的摄像头
        """
        with self._cameras_lock:
            if camera_id not in self._cameras:
                return False
                
            if self._cameras[camera_id].is_streaming:
                self.stop_stream(camera_id)
                
            try:
                cap = self._cameras[camera_id].cap
                cap.release()
                del self._cameras[camera_id]
                return True
            except Exception as e:
                logger.error(f"Error closing camera {camera_id}: {str(e)}")
                return False
    
    def start_stream(self, camera_id: str) -> bool:
        """
        启动摄像头流
        """
        with self._cameras_lock:
            if camera_id not in self._cameras:
                return False
                
            camera = self._cameras[camera_id]
            if camera.is_streaming:
                return True
                
            camera.is_streaming = True
            camera.thread = threading.Thread(
                target=self._stream_thread, 
                args=(camera_id,),
                daemon=True
            )
            camera.thread.start()
            return True
    
    def stop_stream(self, camera_id: str) -> bool:
        """
        停止摄像头流
        """
        with self._cameras_lock:
            if camera_id not in self._cameras:
                return False
                
            camera = self._cameras[camera_id]
            if not camera.is_streaming:
                return True
                
            camera.is_streaming = False
            if camera.thread:
                camera.thread.join(timeout=1.0)
                camera.thread = None
            return True
    
    def is_frame_valid(self, frame_data: bytes) -> bool:
        """检查帧数据是否有效"""
        if not frame_data or len(frame_data) < 100:  # 一个有效的JPEG至少应该有100字节
            logger.warning(f"帧数据太小或为空: {len(frame_data) if frame_data else 0} 字节")
            return False
            
        # 检查是否为有效的JPEG头部
        if not frame_data.startswith(b'\xff\xd8'):
            logger.warning("帧数据不是有效的JPEG格式 (缺少JPEG头部标记)")
            return False
            
        # 检查是否有JPEG尾部标记
        if not frame_data.endswith(b'\xff\xd9'):
            logger.warning("帧数据可能不完整 (缺少JPEG尾部标记)")
            # 这可能不是致命错误，有些编码器可能不添加尾部标记
            
        # 尝试解码看是否成功
        try:
            img_array = np.frombuffer(frame_data, dtype=np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            if img is None or img.size == 0:
                logger.warning("无法解码帧数据为有效图像")
                return False
                
            # 检查图像尺寸是否合理
            if img.shape[0] < 10 or img.shape[1] < 10:
                logger.warning(f"图像尺寸异常小: {img.shape}")
                return False
                
            # 检查图像是否全黑或全白
            mean_value = np.mean(img)
            if mean_value < 5 or mean_value > 250:
                logger.warning(f"图像可能是全黑或全白 (平均值: {mean_value})")
                # 这可能不是致命错误，只是一个警告
                
            return True
        except Exception as e:
            logger.error(f"验证帧有效性时出错: {str(e)}")
            return False
            
    def get_frame(self, camera_id: str) -> Tuple[bool, bytes]:
        """
        获取摄像头的当前帧
        """
        # 首先尝试从缓存获取
        success, frame = self.frame_buffer.get_frame(camera_id)
        if success and self.is_frame_valid(frame):
            return True, frame

        # 如果缓存中没有或缓存帧无效，检查摄像头状态
        with self._cameras_lock:
            if camera_id not in self._cameras:
                return False, b''
            
            camera_info = self._cameras[camera_id]
            if camera_info.last_error:
                return False, b''
            
            # 如果摄像头正常但缓存中没有找到帧，尝试直接读取一帧
            try:
                if camera_info.cap.isOpened():
                    # 直接从摄像头读取一帧
                    ret, frame = camera_info.cap.read()
                    if ret and frame is not None:
                        # 编码为JPEG
                        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                        jpg_bytes = buffer.tobytes()
                        
                        # 验证编码后的帧
                        if not self.is_frame_valid(jpg_bytes):
                            logger.warning(f"从摄像头 {camera_id} 直接读取的帧无效")
                            return False, b''
                        
                        # 更新帧缓存
                        self.frame_buffer.update_frame(camera_id, jpg_bytes)
                        
                        logger.info(f"直接从摄像头读取帧作为应急措施: {camera_id}")
                        return True, jpg_bytes
            except Exception as e:
                logger.error(f"直接读取摄像头帧出错: {str(e)}")

        return False, b''
    
    def _stream_thread(self, camera_id: str):
        """
        后台线程，持续从摄像头读取帧
        """
        try:
            logger.info(f"摄像头 {camera_id} 流线程已启动")
            consecutive_errors = 0
            max_consecutive_errors = 5
            last_success_time = time.time()
            
            while True:
                # 检查是否应该停止流
                camera_info = None
                with self._cameras_lock:
                    if camera_id not in self._cameras or not self._cameras[camera_id].is_streaming:
                        logger.info(f"摄像头 {camera_id} 流线程停止")
                        break
                    camera_info = self._cameras[camera_id]
                
                if camera_info:
                    try:
                        cap = camera_info.cap
                        
                        if not cap.isOpened():
                            logger.error(f"摄像头 {camera_id} 已断开连接")
                            with self._cameras_lock:
                                if camera_id in self._cameras:
                                    self._cameras[camera_id].last_error = "摄像头已断开连接"
                                    self._cameras[camera_id].is_streaming = False
                            break
                        
                        # 尝试多次读取帧以提高可靠性
                        ret, frame = False, None
                        retry_count = 0
                        while not ret and retry_count < 3:
                            ret, frame = cap.read()
                            if ret:
                                break
                            retry_count += 1
                            logger.warning(f"摄像头 {camera_id} 读取帧尝试 {retry_count}/3 失败")
                            time.sleep(0.05)  # 短暂等待后重试
                        
                        if not ret:
                            consecutive_errors += 1
                            current_time = time.time()
                            logger.error(f"摄像头 {camera_id} 无法读取帧 ({consecutive_errors}/{max_consecutive_errors}), 上次成功: {current_time - last_success_time:.1f}秒前")
                            
                            if consecutive_errors >= max_consecutive_errors:
                                logger.error(f"摄像头 {camera_id} 连续读取帧失败达到上限，尝试重置摄像头")
                                with self._cameras_lock:
                                    if camera_id in self._cameras:
                                        # 尝试重置摄像头
                                        device_id = self._cameras[camera_id].device_id
                                        source_type = self._cameras[camera_id].source_type
                                        self._force_cleanup_camera(camera_id)
                                        time.sleep(0.5)
                                        
                                        # 在macOS上可能需要额外延迟
                                        if platform.system() == 'Darwin':
                                            time.sleep(1.0)
                                            
                                        # 重新打开摄像头
                                        if self.open_camera(camera_id, device_id):
                                            logger.info(f"摄像头 {camera_id} 已重置并重新打开")
                                            self.start_stream(camera_id)
                                            return  # 退出当前线程，新的流线程会接管
                                        else:
                                            logger.error(f"摄像头 {camera_id} 无法重置")
                                            break
                            
                            with self._cameras_lock:
                                if camera_id in self._cameras:
                                    self._cameras[camera_id].last_error = "摄像头无法读取帧"
                            time.sleep(0.1)
                            continue
                        
                        # 成功读取帧，重置错误计数
                        consecutive_errors = 0
                        last_success_time = time.time()
                        
                        # 编码为JPEG
                        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                        jpg_bytes = buffer.tobytes()
                        
                        # 更新帧缓存
                        self.frame_buffer.update_frame(camera_id, jpg_bytes)
                        
                        # 更新摄像头状态
                        with self._cameras_lock:
                            if camera_id in self._cameras:
                                self._cameras[camera_id].last_error = None
                                
                    except Exception as e:
                        consecutive_errors += 1
                        logger.error(f"摄像头 {camera_id} 流线程错误 ({consecutive_errors}/{max_consecutive_errors}): {str(e)}")
                        
                        # 如果连续错误过多，尝试重置
                        if consecutive_errors >= max_consecutive_errors:
                            with self._cameras_lock:
                                if camera_id in self._cameras:
                                    logger.error(f"摄像头 {camera_id} 连续错误过多，重置流")
                                    device_id = self._cameras[camera_id].device_id
                                    self._force_cleanup_camera(camera_id)
                                    time.sleep(0.5)
                                    if self.open_camera(camera_id, device_id):
                                        self.start_stream(camera_id)
                                        return  # 退出当前线程，新的流线程会接管
                        
                        with self._cameras_lock:
                            if camera_id in self._cameras:
                                self._cameras[camera_id].last_error = str(e)
                        time.sleep(0.1)
                
                # 控制帧率 (约30FPS)
                time.sleep(0.03)
                
        except Exception as e:
            logger.exception(f"摄像头 {camera_id} 流线程崩溃: {str(e)}")
            with self._cameras_lock:
                if camera_id in self._cameras:
                    self._cameras[camera_id].is_streaming = False
                    self._cameras[camera_id].last_error = str(e)

    def get_mjpeg_frame_generator(self, camera_id: str):
        """
        返回MJPEG流的帧生成器
        """
        boundary = "frame"
        client_id = None
        
        # 增加客户端计数，使用短暂的锁
        try:
            with self._cameras_lock:
                if camera_id not in self._cameras:
                    yield (
                        f"--{boundary}\r\n"
                        "Content-Type: image/jpeg\r\n\r\n".encode() + b"Camera not found" + b"\r\n"
                    )
                    return
                
                # 生成唯一的客户端ID，用于跟踪
                client_id = f"client_{time.time()}_{id(threading.current_thread())}"
                logger.info(f"New stream client {client_id} for camera {camera_id}")
                
                self._cameras[camera_id].clients += 1
                
                # 如果摄像头尚未流式传输，则启动流
                if not self._cameras[camera_id].is_streaming:
                    if not self.start_stream(camera_id):
                        yield (
                            f"--{boundary}\r\n"
                            "Content-Type: image/jpeg\r\n\r\n".encode() + b"Failed to start stream" + b"\r\n"
                        )
                        return
        except Exception as e:
            logger.error(f"Error when starting stream for camera {camera_id}: {str(e)}")
            yield (
                f"--{boundary}\r\n"
                "Content-Type: image/jpeg\r\n\r\n".encode() + f"Stream error: {str(e)}".encode() + b"\r\n"
            )
            return
        
        # 记录开始时间，用于长时间无响应的情况
        start_time = time.time()
        frame_count = 0
        last_frame_time = time.time()
        
        try:
            # 发送流式帧
            while True:
                current_time = time.time()
                
                # 检查是否长时间无结果 (超过30秒无帧)
                if current_time - start_time > 30.0 and frame_count == 0:
                    logger.error(f"Camera {camera_id} stream timeout - no frames for 30 seconds")
                    break
                
                # 检查是否超过5秒没有新帧
                if frame_count > 0 and current_time - last_frame_time > 5.0:
                    logger.warning(f"Camera {camera_id} stream stalled - no frames for 5 seconds")
                    # 检查摄像头状态
                    with self._cameras_lock:
                        if camera_id in self._cameras and not self._cameras[camera_id].is_streaming:
                            logger.info(f"Camera {camera_id} stream was stopped, restarting")
                            self.start_stream(camera_id)
                
                # 尝试获取帧，不获取锁
                success, frame_data = self.get_frame(camera_id)
                if not success:
                    # 发送空白帧或错误信息
                    yield (
                        f"--{boundary}\r\n"
                        "Content-Type: image/jpeg\r\n\r\n".encode() + b"No frame available" + b"\r\n"
                    )
                    time.sleep(0.1)
                    continue
                
                # 更新最后帧时间
                last_frame_time = time.time()
                
                # 构造MJPEG帧并返回
                yield (
                    f"--{boundary}\r\n"
                    f"Content-Type: image/jpeg\r\n"
                    f"Content-Length: {len(frame_data)}\r\n\r\n".encode() + frame_data + b"\r\n"
                )
                
                # 更新帧计数
                frame_count += 1
                if frame_count % 100 == 0:
                    fps = frame_count / (current_time - start_time)
                    logger.info(f"Camera {camera_id} streaming at {fps:.1f} FPS to client {client_id}")
                
                # 检查摄像头是否仍在流式传输，使用短暂的锁
                is_running = True
                with self._cameras_lock:
                    if camera_id not in self._cameras or not self._cameras[camera_id].is_streaming:
                        is_running = False
                
                if not is_running:
                    logger.info(f"Camera {camera_id} stream stopped for client {client_id}")
                    break
                
                # 控制帧率
                time.sleep(0.03)  # 约30FPS
        
        except GeneratorExit:
            # 正常关闭流
            logger.info(f"Camera {camera_id} stream closed normally for client {client_id}")
        except Exception as e:
            # 流处理出错
            logger.error(f"Error in camera {camera_id} stream for client {client_id}: {str(e)}")
        finally:
            # 流结束，减少客户端计数，使用短暂的锁
            try:
                with self._cameras_lock:
                    if camera_id in self._cameras:
                        self._cameras[camera_id].clients -= 1
                        clients_left = self._cameras[camera_id].clients
                        
                        # 如果没有客户端，确保计数不为负
                        if clients_left < 0:
                            self._cameras[camera_id].clients = 0
                            clients_left = 0
                            
                        logger.info(f"Client {client_id} disconnected from camera {camera_id}, {clients_left} clients left")
            except Exception as e:
                logger.error(f"Error when closing camera {camera_id}: {str(e)}")

    def get_camera_status(self, camera_id: str) -> dict:
        """获取摄像头状态信息"""
        with self._cameras_lock:
            if camera_id not in self._cameras:
                return {
                    "status": "offline",
                    "message": "Camera not connected"
                }
            
            camera = self._cameras[camera_id]
            
            if camera.last_error:
                return {
                    "status": "error",
                    "message": camera.last_error
                }
            
            if camera.is_streaming:
                return {
                    "status": "online",
                    "message": "Camera streaming",
                    "clients": camera.clients
                }
            
            return {
                "status": "online",
                "message": "Camera connected but not streaming"
            }

    def _monitor_camera_status(self):
        """监控所有摄像头的状态并更新数据库"""
        while True:
            try:
                # 获取数据库会话
                from ..models.base import SessionLocal
                from .settings import SettingsService
                
                db = SessionLocal()
                settings_service = SettingsService(db)
                
                # 获取所有摄像头设备
                camera_devices = settings_service.get_devices(type="camera")
                device_map = {}
                
                # 创建设备ID到设备的映射
                for device in camera_devices:
                    if device.config and 'source' in device.config:
                        source = device.config['source']
                        if source.startswith('device:'):
                            device_id = source.split(':')[1]
                            camera_id = f"camera_{device_id}"
                            device_map[camera_id] = device
                
                # 复制摄像头状态信息，减少锁的持有时间
                camera_statuses = {}
                try:
                    with self._cameras_lock:
                        for camera_id, camera in self._cameras.items():
                            # 仅复制我们需要的信息
                            camera_statuses[camera_id] = {
                                'is_opened': camera.cap.isOpened(),
                                'last_error': camera.last_error
                            }
                except Exception as e:
                    logger.error(f"获取摄像头状态时发生错误: {str(e)}")
                    time.sleep(5)  # 出错时短暂等待后继续
                    continue
                
                # 锁外处理状态更新
                for camera_id, status_info in camera_statuses.items():
                    if camera_id in device_map:
                        device = device_map[camera_id]
                        status = "online" if status_info['is_opened'] and not status_info['last_error'] else "error"
                        
                        # 如果状态与设备状态不同，更新设备状态
                        if device.status != status:
                            try:
                                settings_service.update_device_status(device.id, status)
                                logger.info(f"更新设备 {device.name} 状态为 {status}")
                            except Exception as e:
                                logger.error(f"更新设备 {device.name} 状态时出错: {str(e)}")
                
                db.close()
            except Exception as e:
                logger.error(f"监控摄像头状态出错: {str(e)}")
            
            # 每10秒检查一次
            time.sleep(10)

    def get_frame_processor(self, db: Session) -> 'FrameProcessor':
        """获取或创建帧处理器实例"""
        db_id = id(db)
        with self._processors_lock:
            if db_id not in self._frame_processors:
                self._frame_processors[db_id] = FrameProcessor(db)
            return self._frame_processors[db_id]

    def apply_operation_to_frame(self, frame: bytes, operation_id: int, operation_type: str, db: Session) -> bytes:
        """对单帧应用操作并返回处理后的帧"""
        try:
            # 验证输入
            if frame is None or len(frame) == 0:
                logger.error("无法处理空帧")
                return b''
                
            # 验证操作类型
            if operation_type not in ['operation', 'pipeline']:
                logger.error(f"无效的操作类型: {operation_type}")
                return frame
                
            # 验证操作ID
            if not isinstance(operation_id, int) or operation_id <= 0:
                logger.error(f"无效的操作ID: {operation_id}")
                return frame
            
            # 获取框架处理器
            processor = self.get_frame_processor(db)
            if processor is None:
                logger.error(f"无法获取帧处理器")
                return frame
                
            # 更新最后使用时间
            processor.last_used = time.time()
            
            logger.info(f"应用{operation_type} (ID: {operation_id})到帧 ({len(frame)}字节)")
                
            # 处理帧
            try:
                processed_frame = processor.process_frame(frame, operation_id, operation_type)
                
                # 验证结果
                if processed_frame is None or len(processed_frame) == 0:
                    logger.warning(f"处理后的帧无效，返回原始帧")
                    return frame
                    
                logger.info(f"成功处理帧: {len(processed_frame)}字节")
                return processed_frame
            except Exception as e:
                logger.error(f"处理帧时出错: {str(e)}")
                return frame
        except Exception as e:
            logger.exception(f"应用操作到帧时发生错误: {str(e)}")
            return frame

    def get_processed_stream_key(self, camera_id: str, operation_id: int, operation_type: str) -> str:
        """生成处理流的唯一键值"""
        return f"{camera_id}_{operation_type}_{operation_id}"
    
    def start_processed_stream(self, camera_id: str, operation_id: int, operation_type: str, db: Session) -> bool:
        """启动处理后的摄像头流"""
        stream_key = self.get_processed_stream_key(camera_id, operation_id, operation_type)
        logger.info(f"尝试启动处理流: {stream_key}")
        
        with self._streams_lock:
            # 检查操作类型是否有效
            if operation_type not in ["operation", "pipeline"]:
                logger.error(f"无效的操作类型: {operation_type}")
                return False
                
            # 检查操作ID是否有效
            if not isinstance(operation_id, int) or operation_id <= 0:
                logger.error(f"无效的操作ID: {operation_id}")
                return False
                
            # 先检查并清理可能存在的无效流
            if stream_key in self._processed_streams:
                old_stream = self._processed_streams[stream_key]
                if not old_stream.is_streaming or old_stream.clients <= 0:
                    logger.info(f"清理已存在的无效流: {stream_key}")
                    self._force_cleanup_stream(stream_key)
                else:
                    logger.info(f"重用已存在的处理流: {stream_key}，客户端数: {old_stream.clients}")
                    return True

            # 检查摄像头状态
            if camera_id not in self._cameras:
                logger.error(f"未找到摄像头: {camera_id}")
                return False

            camera = self._cameras[camera_id]
            if not camera.cap.isOpened():
                logger.error(f"摄像头 {camera_id} 未正确打开")
                self._force_cleanup_camera(camera_id)
                return False

            # 确保摄像头在流式传输
            if not camera.is_streaming:
                logger.info(f"摄像头 {camera_id} 未流式传输，启动流")
                if not self.start_stream(camera_id):
                    logger.error(f"无法启动摄像头 {camera_id} 的流")
                    return False

            # 创建新的处理流
            try:
                # 检查操作存在性
                if operation_type == "operation":
                    # 验证操作是否存在
                    from .cv_operation import CVOperationService
                    cv_service = CVOperationService(db)
                    operation = cv_service.get_operation(operation_id)
                    if not operation:
                        logger.error(f"未找到指定的操作 (ID: {operation_id})")
                        return False
                elif operation_type == "pipeline":
                    # 验证流水线是否存在
                    from .pipeline import PipelineService
                    pipeline_service = PipelineService(db)
                    pipeline = pipeline_service.get_pipeline(operation_id)
                    if not pipeline:
                        logger.error(f"未找到指定的流水线 (ID: {operation_id})")
                        return False
                
                # 创建处理流实例
                self._processed_streams[stream_key] = ProcessedStream(camera_id, operation_id, operation_type, db)
                logger.info(f"成功启动处理流: {stream_key}")
                return True
            except Exception as e:
                logger.error(f"创建处理流失败: {str(e)}")
                return False

    def stop_processed_stream(self, camera_id: str, operation_id: int, operation_type: str) -> bool:
        """停止处理后的摄像头流"""
        stream_key = self.get_processed_stream_key(camera_id, operation_id, operation_type)
        logger.info(f"尝试停止处理流: {stream_key}")
        
        with self._streams_lock:
            # 检查流是否存在
            if stream_key not in self._processed_streams:
                logger.warning(f"找不到要停止的处理流: {stream_key}")
                return False
            
            try:
                # 获取并清理现有流
                stream = self._processed_streams[stream_key]
                logger.info(f"停止处理流: {stream_key}, 当前客户端数: {stream.clients}")
                
                # 记录流的统计信息
                stats = stream.get_stats()
                logger.info(f"流统计: FPS={stats['fps']:.1f}, 帧数={stats['frame_count']}, 持续时间={stats['duration']:.1f}秒")
                
                # 清理资源
                stream.cleanup()
                logger.info(f"已清理处理流资源: {stream_key}")
                
                # 删除处理流
                del self._processed_streams[stream_key]
                logger.info(f"已停止处理流: {stream_key}")
                return True
            except Exception as e:
                logger.error(f"停止处理流 {stream_key} 时出错: {str(e)}")
                
                # 尽管出错，仍然尝试强制清理
                try:
                    self._force_cleanup_stream(stream_key)
                    logger.warning(f"已强制清理处理流: {stream_key}")
                    return True
                except Exception as cleanup_err:
                    logger.error(f"强制清理处理流 {stream_key} 时出错: {str(cleanup_err)}")
                    return False

    def get_processed_mjpeg_frame_generator(self, camera_id: str, operation_id: int, operation_type: str, db: Session):
        """返回处理后MJPEG流的帧生成器"""
        boundary = "processedframe"
        stream_key = self.get_processed_stream_key(camera_id, operation_id, operation_type)
        client_id = f"client_{time.time()}_{id(threading.current_thread())}"
        processed_stream = None
        frame_processor = self.get_frame_processor(db)
        frame_interval = 0.03
        last_stats_time = time.time()
        error_count = 0
        max_errors = 5

        try:
            with self._cameras_lock:
                # 检查摄像头状态
                if camera_id not in self._cameras:
                    yield self._create_error_frame(boundary, "Camera not found")
                    return

                camera = self._cameras[camera_id]
                if not camera.cap.isOpened():
                    logger.error(f"Camera {camera_id} is not properly opened")
                    self._force_cleanup_camera(camera_id)
                    yield self._create_error_frame(boundary, "Camera is not properly opened")
                    return

                # 启动或获取处理流
                if stream_key not in self._processed_streams:
                    if not self.start_processed_stream(camera_id, operation_id, operation_type, db):
                        yield self._create_error_frame(boundary, "Failed to start processed stream")
                        return
                
                processed_stream = self._processed_streams[stream_key]
                processed_stream.increment_clients()
                logger.info(f"New processed stream client {client_id} for camera {camera_id}")

        except Exception as e:
            logger.error(f"Error initializing processed stream: {str(e)}")
            yield self._create_error_frame(boundary, f"Stream initialization error: {str(e)}")
            return

        try:
            last_process_time = 0
            while processed_stream and processed_stream.is_streaming:
                try:
                    current_time = time.time()
                    
                    # 检查摄像头状态
                    with self._cameras_lock:
                        if camera_id not in self._cameras or not self._cameras[camera_id].cap.isOpened():
                            logger.error(f"Camera {camera_id} became invalid")
                            break

                    # 获取和处理帧
                    success, frame_data = self.get_frame(camera_id)
                    if not success or not frame_data:
                        error_count += 1
                        logger.warning(f"摄像头 {camera_id} 获取帧失败 ({error_count}/{max_errors})")
                        
                        # 尝试等待一会儿再重试
                        if error_count < max_errors:
                            # 如果摄像头未流式传输，尝试重启
                            with self._cameras_lock:
                                if camera_id in self._cameras and not self._cameras[camera_id].is_streaming:
                                    logger.info(f"摄像头 {camera_id} 流停止，尝试重启")
                                    self.start_stream(camera_id)
                            
                            # 生成错误帧
                            yield self._create_error_frame(boundary, f"等待摄像头帧... ({error_count}/{max_errors})")
                            time.sleep(0.2)  # 稍长的等待时间
                            continue
                        else:
                            logger.error(f"摄像头 {camera_id} 获取帧失败次数过多")
                            
                            # 如果太多错误，创建一个特殊的错误图像
                            err_msg = "摄像头连续获取帧失败，请检查摄像头连接和权限"
                            yield self._create_error_frame(boundary, err_msg)
                            
                            # 尝试重置摄像头
                            with self._cameras_lock:
                                if camera_id in self._cameras:
                                    device_id = self._cameras[camera_id].device_id
                                    if not self._cameras[camera_id].is_streaming:
                                        logger.info(f"尝试重新启动摄像头 {camera_id} 流")
                                        self.start_stream(camera_id)
                                    
                            # 重置错误计数并继续尝试
                            error_count = 0
                            time.sleep(1.0)  # 较长时间等待
                            continue

                    # 重置错误计数
                    error_count = 0

                    # 处理帧
                    try:
                        processed_frame = frame_processor.process_frame(
                            frame_data,
                            processed_stream.operation_id,
                            processed_stream.operation_type
                        )
                        
                        # 检查处理后的帧是否为空或无效
                        if not processed_frame or len(processed_frame) == 0:
                            logger.warning(f"处理后的帧无效，使用原始帧作为替代")
                            processed_frame = frame_data
                    except Exception as e:
                        logger.error(f"处理帧时发生错误: {str(e)}，使用原始帧")
                        processed_frame = frame_data

                    # 更新处理流状态和缓存
                    processed_stream.update_frame(processed_frame)
                    self.frame_buffer.update_processed_frame(stream_key, processed_frame)

                    # 发送处理后的帧
                    yield (
                        f"--{boundary}\r\n"
                        f"Content-Type: image/jpeg\r\n"
                        f"Content-Length: {len(processed_frame)}\r\n\r\n".encode() + processed_frame + b"\r\n"
                    )

                    # 更新统计信息和调整帧率
                    if current_time - last_stats_time >= 1.0:
                        stats = processed_stream.get_stats()
                        logger.info(
                            f"Stream stats - camera: {camera_id}, "
                            f"client: {client_id}, "
                            f"fps: {stats['fps']:.1f}, "
                            f"clients: {stats['clients']}"
                        )
                        
                        if stats['fps'] > 35:
                            frame_interval = min(0.05, frame_interval + 0.001)
                        elif stats['fps'] < 25:
                            frame_interval = max(0.01, frame_interval - 0.001)
                        
                        last_stats_time = current_time

                    time.sleep(frame_interval)

                except Exception as e:
                    logger.error(f"Error processing frame: {str(e)}")
                    error_count += 1
                    if error_count >= max_errors:
                        break
                    time.sleep(0.1)

        except GeneratorExit:
            logger.info(f"Processed stream closed normally for client {client_id}")
        except Exception as e:
            logger.error(f"Fatal error in processed stream for client {client_id}: {str(e)}")
        finally:
            try:
                with self._streams_lock:
                    if stream_key in self._processed_streams:
                        clients_left = processed_stream.decrement_clients()
                        if clients_left <= 0:
                            logger.info(f"No clients left for processed stream {stream_key}, stopping")
                            self._force_cleanup_stream(stream_key)
                        else:
                            logger.info(
                                f"Client {client_id} disconnected from processed stream {stream_key}, "
                                f"{clients_left} clients left"
                            )
            except Exception as e:
                logger.error(f"Error during stream cleanup: {str(e)}")
                # 确保在出错时也能清理资源
                self._force_cleanup_stream(stream_key)

    def _create_error_frame(self, boundary: str, message: str) -> bytes:
        """创建包含错误信息的图像帧"""
        try:
            # 创建一个黑色背景图像
            height, width = 480, 640
            img = np.zeros((height, width, 3), np.uint8)
            
            # 在图像上添加错误文本
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.7
            color = (255, 255, 255)  # 白色文字
            thickness = 2
            line_type = cv2.LINE_AA
            
            # 分割长消息以适应宽度
            words = message.split()
            lines = []
            current_line = ""
            for word in words:
                test_line = current_line + " " + word if current_line else word
                # 计算文本宽度
                (text_width, _), _ = cv2.getTextSize(test_line, font, font_scale, thickness)
                if text_width < width - 40:  # 留出边距
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)
            
            # 添加所有文本行
            y_position = height // 2 - (len(lines) * 30) // 2  # 垂直居中文本
            for line in lines:
                text_size, _ = cv2.getTextSize(line, font, font_scale, thickness)
                x_position = (width - text_size[0]) // 2  # 水平居中文本
                cv2.putText(img, line, (x_position, y_position), font, font_scale, color, thickness, line_type)
                y_position += 30  # 行间距
            
            # 编码为JPEG
            _, buffer = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 80])
            jpg_bytes = buffer.tobytes()
            
            # 构造MJPEG帧
            return (
                f"--{boundary}\r\n"
                f"Content-Type: image/jpeg\r\n"
                f"Content-Length: {len(jpg_bytes)}\r\n\r\n".encode() + jpg_bytes + b"\r\n"
            )
        except Exception as e:
            logger.error(f"创建错误帧失败: {str(e)}")
            # 如果创建错误帧失败，返回简单文本帧
            return (
                f"--{boundary}\r\n"
                "Content-Type: image/jpeg\r\n\r\n".encode() + message.encode() + b"\r\n"
            )

    def close_all_cameras(self) -> None:
        """关闭所有摄像头并清理资源"""
        logger.info("正在关闭所有摄像头资源...")
        
        # 停止所有处理流
        with self._processed_streams_lock:
            for stream_key in list(self._processed_streams.keys()):
                try:
                    stream = self._processed_streams[stream_key]
                    stream.cleanup()
                    logger.info(f"已清理处理流: {stream_key}")
                except Exception as e:
                    logger.error(f"清理处理流 {stream_key} 失败: {str(e)}")
            self._processed_streams.clear()
        
        # 停止所有摄像头流
        with self._cameras_lock:
            for camera_id in list(self._cameras.keys()):
                try:
                    camera_info = self._cameras.get(camera_id)
                    if camera_info:
                        if camera_info.thread and camera_info.thread.is_alive():
                            camera_info.is_streaming = False
                            camera_info.thread.join(timeout=1.0)
                            logger.info(f"已停止摄像头线程: {camera_id}")
                        
                        if camera_info.cap and camera_info.cap.isOpened():
                            camera_info.cap.release()
                            logger.info(f"已释放摄像头资源: {camera_id}")
                except Exception as e:
                    logger.error(f"关闭摄像头 {camera_id} 失败: {str(e)}")
            self._cameras.clear()
        
        # 清空帧缓存
        if self._frame_buffer:
            self._frame_buffer.cleanup()
            
        logger.info("所有摄像头资源已成功关闭")

# 单例实例
camera_service = CameraService() 