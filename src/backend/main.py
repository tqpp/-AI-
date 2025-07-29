from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
from .routers.annotation import router as annotation_router
from .routers.cv_operation import router as cv_operation_router
from .routers.pipeline import router as cv_pipeline_router
from .routers import model
from .routers import settings
from .routers import camera
from .routers import detection
from .routers.dashboard import router as dashboard_router
import os
import threading
import time
from .services.camera import camera_service
from sqlalchemy.orm import Session
from .dependencies import get_db
from .models.base import SessionLocal, engine
from .services.model import ModelService
from .models import ModelStatus
import platform
import pathlib

if platform.system() == "Windows":
    temp = pathlib.PosixPath
    pathlib.PosixPath = pathlib.WindowsPath

# 创建FastAPI应用实例
app = FastAPI(
    title="工业铸字识别系统API",
    description="工业铸字识别系统的后端API服务",
    version="1.0.0"
)

# 配置CORS
app.add_middleware( 
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 确保uploads文件夹存在
uploads_dir = "uploads"
if not os.path.exists(uploads_dir):
    os.makedirs(uploads_dir)
    
dist_dir = "dist"
if not os.path.exists(dist_dir):
    os.makedirs(dist_dir)

# 配置静态文件路由
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

# 注册路由
app.include_router(annotation_router)
app.include_router(cv_operation_router)
app.include_router(cv_pipeline_router)
app.include_router(model.router)
app.include_router(settings.router)
app.include_router(camera.router)
app.include_router(detection.router)
app.include_router(dashboard_router)

app.mount("/", StaticFiles(directory=dist_dir, html=True), name="frontend")


# 自动检测和注册摄像头的后台任务
def auto_detect_cameras():
    # 等待应用启动完成
    time.sleep(2)
    
    try:
        print("Starting camera detection...")
        # 检测可用摄像头
        detected_cameras = camera_service.detect_cameras()
        
        if detected_cameras:
            print(f"检测到 {len(detected_cameras)} 个摄像头")
            
            # 获取数据库会话
            db = SessionLocal()
            try:
                # 导入设置服务
                from .services.settings import SettingsService
                settings_service = SettingsService(db)
                
                # 获取现有设备列表 (改为手动过滤以防止参数错误)
                existing_devices = settings_service.get_devices()
                existing_camera_devices = [device for device in existing_devices if device.type == "camera"]
                existing_device_names = [device.name for device in existing_camera_devices]
                
                # 添加未注册的摄像头
                registered_count = 0
                for camera in detected_cameras:
                    camera_name = camera['name']
                    if camera_name not in existing_device_names:
                        try:
                            # 创建一个配置，包括摄像头的device_id
                            device_id = camera['device_id']
                            config = {
                                'source': f"device:{device_id}",
                                'resolution': '640x480',
                                'fps': 30
                            }
                            
                            # 添加摄像头
                            settings_service.add_device(
                                name=camera_name,
                                type="camera",
                                status="offline",
                                config=config,
                                description=f"自动检测到的摄像头 ({platform.system()})"
                            )
                            registered_count += 1
                            print(f"自动注册摄像头: {camera_name}")
                            # 添加到已有设备名称列表，避免重复添加
                            existing_device_names.append(camera_name)
                        except Exception as e:
                            print(f"注册摄像头 {camera_name} 失败: {str(e)}")
                
                if registered_count > 0:
                    print(f"自动注册了 {registered_count} 个新摄像头")
                
                # 启动所有检测到的摄像头
                for camera in detected_cameras:
                    try:
                        device_id = camera['device_id']
                        camera_id = f"camera_{device_id}"
                        
                        if camera_service.open_camera(camera_id, device_id):
                            if camera_service.start_stream(camera_id):
                                print(f"启动摄像头流: {camera['name']}")
                                
                                # 找到数据库中对应的设备并更新状态
                                matching_devices = [d for d in existing_camera_devices 
                                                   if d.name == camera['name'] or 
                                                      (d.config and d.config.get('source') == f"device:{device_id}")]
                                
                                if matching_devices:
                                    # 更新设备状态为online
                                    for device in matching_devices:
                                        settings_service.update_device_status(device.id, "online")
                                        print(f"已更新设备 {device.name} (ID: {device.id}) 状态为online")
                            else:
                                print(f"无法启动摄像头流: {camera['name']}")
                    except Exception as cam_e:
                        print(f"启动摄像头 {camera['name']} 出错: {str(cam_e)}")
            finally:
                db.close()
        else:
            print("未检测到任何摄像头")
            
            # On macOS, provide instructions for camera permissions
            if platform.system() == 'Darwin':
                print("\n*** macOS相机权限说明 ***")
                print("如果您正在使用macOS，需要手动授予应用程序相机访问权限。")
                print("请前往系统偏好设置 -> 安全性与隐私 -> 隐私 -> 相机，")
                print("确保您的终端应用或Python应用程序已获得相机访问权限。")
                print("授权后重新启动应用程序。\n")
    except Exception as e:
        print(f"摄像头自动检测出错: {str(e)}")


def update_camera_urls():
    """更新所有摄像头的RTSP/HTTP流URL"""
    # 等待应用启动完成
    time.sleep(3)
    
    try:
        print("更新摄像头URL...")
        # 获取数据库会话
        db = SessionLocal()
        try:
            # 导入设置服务
            from .services.settings import SettingsService
            settings_service = SettingsService(db)
            
            # 获取所有摄像头设备
            devices = settings_service.get_devices()
            camera_devices = [device for device in devices if device.type == "camera"]
            
            for device in camera_devices:
                try:
                    # 检查是否有配置
                    if not device.config:
                        continue
                        
                    # 检查配置是否包含URL
                    source = device.config.get('source', '')
                    if source and (source.startswith('rtsp://') or source.startswith('http://')):
                        print(f"更新摄像头URL: {device.name} ({source})")
                        camera_id = f"camera_{device.id}"
                        
                        # 尝试打开并启动流
                        if camera_service.open_camera(camera_id, source):
                            if camera_service.start_stream(camera_id):
                                print(f"成功连接到摄像头流: {device.name}")
                                # 更新设备状态
                                settings_service.update_device_status(device.id, "online")
                            else:
                                print(f"无法启动摄像头流: {device.name}")
                                settings_service.update_device_status(device.id, "offline")
                except Exception as cam_e:
                    print(f"处理摄像头 {device.name} URL时出错: {str(cam_e)}")
        finally:
            db.close()
    except Exception as e:
        print(f"更新摄像头URL时出错: {str(e)}")


# 预加载所有已训练完成的模型
def preload_all_models():
    """在应用启动时预加载所有已训练完成的模型到内存中"""
    # 等待应用启动完成
    time.sleep(5)
    
    try:
        print("开始预加载所有已训练完成的模型...")
        # 获取数据库会话
        db = SessionLocal()
        try:
            # 创建模型服务实例
            model_service = ModelService(db)
            
            # 获取所有已完成训练的模型
            all_models = model_service.get_models()
            completed_models = [m for m in all_models if m.status == ModelStatus.COMPLETED]
            
            if not completed_models:
                print("没有找到已训练完成的模型")
                return
                
            print(f"找到 {len(completed_models)} 个已训练完成的模型")
            loaded_count = 0
            failed_count = 0
            
            # 尝试加载每个模型
            for model in completed_models:
                try:
                    # 检查模型文件是否存在
                    if not model.file_path or not os.path.exists(model.file_path):
                        print(f"模型 ID:{model.id}, 名称:{model.name} 的文件不存在: {model.file_path}")
                        failed_count += 1
                        continue
                        
                    # 加载模型实例
                    model_instance = model_service.get_model_instance(model.id)
                    if model_instance:
                        print(f"成功加载模型 ID:{model.id}, 名称:{model.name}")
                        loaded_count += 1
                except Exception as e:
                    print(f"加载模型 ID:{model.id}, 名称:{model.name} 失败: {str(e)}")
                    failed_count += 1
            
            print(f"预加载模型完成: 成功 {loaded_count} 个, 失败 {failed_count} 个")
            
            # 打印加载的模型缓存信息
            print(f"当前已加载模型缓存数量: {len(model_service._loaded_models)}")
            for model_id, model_instance in model_service._loaded_models.items():
                print(f"- 模型 ID:{model_id}, 文件:{model_instance.model_path}")
        finally:
            db.close()
    except Exception as e:
        print(f"预加载模型时出错: {str(e)}")


# 在应用启动时运行自动检测摄像头
@app.on_event("startup")
async def startup_event():
    print("应用启动中...")
    # 在后台线程中运行摄像头检测
    auto_detect_cameras()
    update_camera_urls()
    preload_all_models()
    # threading.Thread(target=auto_detect_cameras, daemon=True).start()
    
    # # 添加一个任务更新所有摄像头URL
    # threading.Thread(target=update_camera_urls, daemon=True).start()
    
    # # 预加载所有模型
    # threading.Thread(target=preload_all_models, daemon=True).start()
    
    # 记录内存和连接池状态
    pool_status = engine.pool.status()
    print(f"数据库连接池状态: {pool_status}")
    print(f"当前连接池大小: {engine.pool.size()}")
    print(f"连接池使用情况: 大小={engine.pool.size()}, 最大溢出={engine.pool._max_overflow}, 超时时间={engine.pool._timeout}")

@app.on_event("shutdown")
async def shutdown_event():
    print("应用正在关闭...")
    # 清理数据库连接池
    engine.dispose()
    print("数据库连接池已关闭")
    
    # 尝试进行垃圾回收
    import gc
    gc.collect()
    print("垃圾回收已执行")
    
    # 关闭所有摄像头连接
    camera_service.close_all_cameras()
    print("所有摄像头连接已关闭")


# 启动服务器
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)