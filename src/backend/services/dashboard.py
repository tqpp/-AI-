from sqlalchemy.orm import Session
from sqlalchemy import func, desc, cast, Date
from datetime import datetime, timedelta
import psutil
import os
import time
import logging
from typing import Optional
import json

from ..models import Detection, DetectionStatus, Alert, AlertType, Device, Settings
from ..dependencies import get_db
from fastapi import Depends

logger = logging.getLogger(__name__)

# 系统启动时间文件路径
STARTUP_TIME_FILE = "system_startup_time.json"

# 获取系统启动时间
def get_startup_time():
    try:
        # 首先尝试从文件读取启动时间
        if os.path.exists(STARTUP_TIME_FILE):
            with open(STARTUP_TIME_FILE, 'r') as f:
                data = json.load(f)
                return data.get('startup_time')
        return None
    except Exception as e:
        logger.error(f"读取启动时间文件失败: {str(e)}")
        return None

# 保存系统启动时间
def save_startup_time(startup_time):
    try:
        with open(STARTUP_TIME_FILE, 'w') as f:
            json.dump({'startup_time': startup_time}, f)
    except Exception as e:
        logger.error(f"保存启动时间文件失败: {str(e)}")

# 初始化系统启动时间
SYSTEM_START_TIME = get_startup_time() or time.time()
if get_startup_time() is None:
    save_startup_time(SYSTEM_START_TIME)

class DashboardService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_system_status(self):
        """获取系统状态信息"""
        try:
            # 获取系统启动时间
            startup_time = SYSTEM_START_TIME
            
            # 尝试从数据库中读取系统配置
            system_startup_setting = self.db.query(Settings)\
                .filter(Settings.category == 'system')\
                .filter(Settings.key == 'startup_time')\
                .first()
                
            # 如果数据库中有配置，使用数据库中的值
            if system_startup_setting:
                try:
                    startup_time = float(system_startup_setting.value)
                except (ValueError, TypeError):
                    # 如果数据库中的值无效，使用默认值并更新数据库
                    startup_time = SYSTEM_START_TIME
                    system_startup_setting.value = str(startup_time)
                    self.db.commit()
            else:
                # 如果数据库中没有配置，创建新的配置
                new_setting = Settings(
                    category='system',
                    key='startup_time',
                    value=str(SYSTEM_START_TIME),
                    description='系统启动时间戳'
                )
                self.db.add(new_setting)
                try:
                    self.db.commit()
                except Exception as e:
                    logger.error(f"保存系统启动时间到数据库失败: {str(e)}")
                    self.db.rollback()
            
            # 获取系统运行时间（小时）
            current_time = time.time()
            uptime_hours = round((current_time - startup_time) / 3600, 1)
            
            logger.info(f"系统启动时间: {startup_time}, 当前时间: {current_time}, 运行时间: {uptime_hours}小时")
            
            # 获取CPU和内存使用情况
            cpu_percent = psutil.cpu_percent()
            memory_percent = psutil.virtual_memory().percent
            disk_percent = psutil.disk_usage('/').percent
            
            # 判断系统状态
            status = "normal"
            message = "dashboard.systemStatus.systemNormal"
            
            if cpu_percent > 90 or memory_percent > 90 or disk_percent > 90:
                status = "error"
                message = "dashboard.systemStatus.systemResourceStress"
            elif cpu_percent > 70 or memory_percent > 70 or disk_percent > 70:
                status = "warning"
                message = "dashboard.systemStatus.systemLoadHigh"
            
            return {
                "status": status,
                "uptime": uptime_hours,
                "message": message,
                "resources": {
                    "cpu": cpu_percent,
                    "memory": memory_percent,
                    "disk": disk_percent
                }
            }
        except Exception as e:
            logger.error(f"获取系统状态时出错: {str(e)}")
            return {
                "status": "error",
                "uptime": 0,
                "message": "dashboard.systemStatus.systemStatusError"
            }
    
    def get_detection_stats(self):
        """获取今日检测统计"""
        try:
            # 获取今天的日期
            today = datetime.now().date()
            yesterday = today - timedelta(days=1)
            
            logger.info(f"当前系统日期：{today}, 查询检测统计")
            
            # 查询今日检测总数 - 先检查是否有使用今天日期的记录
            today_total = self.db.query(func.count(Detection.id))\
                .filter(cast(Detection.timestamp, Date) == today)\
                .scalar() or 0
                
            logger.info(f"今日记录数：{today_total}")
                
            # 如果没有今天的记录，查询最近的记录日期
            if today_total == 0:
                # 获取所有检测记录
                all_records = self.db.query(func.count(Detection.id)).scalar() or 0
                logger.info(f"数据库中总记录数：{all_records}")
                
                # 查找最近的记录
                latest_detection = self.db.query(Detection).order_by(desc(Detection.timestamp)).first()
                
                if latest_detection:
                    # 获取最近记录的日期作为"今天"
                    latest_date = latest_detection.timestamp.date()
                    one_day_before = latest_date - timedelta(days=1)
                    
                    logger.info(f"找到最新记录日期：{latest_date}, 前一天：{one_day_before}")
                    
                    # 使用最近的记录日期重新查询
                    latest_count_query = self.db.query(func.count(Detection.id))\
                        .filter(cast(Detection.timestamp, Date) == latest_date)
                    latest_date_total = latest_count_query.scalar() or 0
                    
                    logger.info(f"使用最新日期 {latest_date} 查询结果：{latest_date_total}, SQL: {str(latest_count_query)}")
                    
                    # 直接使用日期字符串比较尝试查询
                    date_str = latest_date.isoformat()
                    manual_count = self.db.query(func.count(Detection.id))\
                        .filter(func.substr(Detection.timestamp, 1, 10) == date_str)\
                        .scalar() or 0
                    
                    logger.info(f"使用日期字符串 {date_str} 查询结果：{manual_count}")
                    
                    # 使用此方法查询前一天
                    yesterday_str = one_day_before.isoformat()
                    yesterday_manual_count = self.db.query(func.count(Detection.id))\
                        .filter(func.substr(Detection.timestamp, 1, 10) == yesterday_str)\
                        .scalar() or 0
                    
                    # 使用日期字符串比较的结果
                    if manual_count > 0:
                        change = 0
                        if yesterday_manual_count > 0:
                            change = round(((manual_count - yesterday_manual_count) / yesterday_manual_count) * 100, 1)
                        
                        return {
                            "total": manual_count,
                            "change": change,
                            "today": latest_date.isoformat(),
                            "yesterday_total": yesterday_manual_count,
                            "note": "显示最近的检测记录统计，而非当前日期"
                        }
                    
                    # 如果字符串比较也无法找到记录，返回所有记录总数
                    return {
                        "total": all_records,
                        "change": 0,
                        "today": latest_date.isoformat(),
                        "yesterday_total": 0,
                        "note": "显示所有检测记录统计"
                    }
                
                # 没有找到任何记录，返回所有记录（应该也是0）
                return {
                    "total": all_records,
                    "change": 0,
                    "today": today.isoformat(),
                    "yesterday_total": 0,
                    "note": "无检测记录"
                }
            
            # 查询昨日检测总数
            yesterday_total = self.db.query(func.count(Detection.id))\
                .filter(cast(Detection.timestamp, Date) == yesterday)\
                .scalar() or 0
            
            # 计算变化百分比
            change = 0
            if yesterday_total > 0:
                change = round(((today_total - yesterday_total) / yesterday_total) * 100, 1)
            
            return {
                "total": today_total,
                "change": change,
                "today": today.isoformat(),
                "yesterday_total": yesterday_total
            }
        except Exception as e:
            logger.error(f"获取检测统计时出错: {str(e)}")
            return {
                "total": 0,
                "change": 0
            }
    
    def get_defect_stats(self):
        """获取缺陷统计"""
        try:
            # 获取今天的日期
            today = datetime.now().date()
            yesterday = today - timedelta(days=1)
            
            logger.info(f"当前系统日期：{today}, 查询缺陷统计")
            
            # 获取所有检测记录
            all_records = self.db.query(func.count(Detection.id)).scalar() or 0
            if all_records == 0:
                return {
                    "total": 0,
                    "change": 0,
                    "today": today.isoformat(),
                    "yesterday_total": 0,
                    "note": "无检测记录"
                }
            
            # 查找最近的记录
            latest_detection = self.db.query(Detection).order_by(desc(Detection.timestamp)).first()
            if not latest_detection:
                return {
                    "total": 0,
                    "change": 0,
                    "today": today.isoformat(),
                    "yesterday_total": 0,
                    "note": "无检测记录"
                }
            
            # 获取最近记录的日期
            latest_date = latest_detection.timestamp.date()
            one_day_before = latest_date - timedelta(days=1)
            logger.info(f"找到最新记录日期：{latest_date}, 前一天：{one_day_before}")
            
            # 使用日期字符串比较查询
            date_str = latest_date.isoformat()
            defect_count = self.db.query(func.count(Detection.id))\
                .filter(func.substr(Detection.timestamp, 1, 10) == date_str)\
                .filter(Detection.status == DetectionStatus.FAIL)\
                .scalar() or 0
            
            logger.info(f"使用日期字符串 {date_str} 查询缺陷结果：{defect_count}")
            
            # 查询前一天
            yesterday_str = one_day_before.isoformat()
            yesterday_defect_count = self.db.query(func.count(Detection.id))\
                .filter(func.substr(Detection.timestamp, 1, 10) == yesterday_str)\
                .filter(Detection.status == DetectionStatus.FAIL)\
                .scalar() or 0
            
            # 计算变化百分比
            change = 0
            if yesterday_defect_count > 0:
                change = round(((defect_count - yesterday_defect_count) / yesterday_defect_count) * 100, 1)
            
            return {
                "total": defect_count,
                "change": change,
                "today": latest_date.isoformat(),
                "yesterday_total": yesterday_defect_count,
                "note": "显示最近的检测记录统计，而非当前日期"
            }
            
        except Exception as e:
            logger.error(f"获取缺陷统计时出错: {str(e)}")
            return {
                "total": 0,
                "change": 0
            }
    
    def get_accuracy(self):
        """获取检测准确率统计"""
        try:
            # 获取今天的日期
            today = datetime.now().date()
            yesterday = today - timedelta(days=1)
            
            logger.info(f"当前系统日期：{today}, 查询准确率统计")
            
            # 获取所有检测记录
            all_records = self.db.query(func.count(Detection.id)).scalar() or 0
            if all_records == 0:
                return {
                    "value": 0,
                    "change": 0,
                    "today_total": 0,
                    "today_pass": 0,
                    "yesterday_accuracy": 0,
                    "note": "无检测记录"
                }
            
            # 查找最近的记录
            latest_detection = self.db.query(Detection).order_by(desc(Detection.timestamp)).first()
            if not latest_detection:
                return {
                    "value": 0,
                    "change": 0,
                    "today_total": 0,
                    "today_pass": 0,
                    "yesterday_accuracy": 0,
                    "note": "无检测记录"
                }
            
            # 获取最近记录的日期
            latest_date = latest_detection.timestamp.date()
            one_day_before = latest_date - timedelta(days=1)
            logger.info(f"找到最新记录日期：{latest_date}, 前一天：{one_day_before}")
            
            # 使用日期字符串比较查询今日总数和通过数
            date_str = latest_date.isoformat()
            today_total = self.db.query(func.count(Detection.id))\
                .filter(func.substr(Detection.timestamp, 1, 10) == date_str)\
                .scalar() or 0
                
            today_pass = self.db.query(func.count(Detection.id))\
                .filter(func.substr(Detection.timestamp, 1, 10) == date_str)\
                .filter(Detection.status == DetectionStatus.PASS)\
                .scalar() or 0
            
            logger.info(f"使用日期字符串 {date_str} 查询结果：总数={today_total}, 通过={today_pass}")
            
            # 查询前一天
            yesterday_str = one_day_before.isoformat()
            yesterday_total = self.db.query(func.count(Detection.id))\
                .filter(func.substr(Detection.timestamp, 1, 10) == yesterday_str)\
                .scalar() or 0
                
            yesterday_pass = self.db.query(func.count(Detection.id))\
                .filter(func.substr(Detection.timestamp, 1, 10) == yesterday_str)\
                .filter(Detection.status == DetectionStatus.PASS)\
                .scalar() or 0
            
            # 计算准确率
            today_accuracy = 0
            if today_total > 0:
                today_accuracy = round((today_pass / today_total) * 100, 1)
            
            yesterday_accuracy = 0
            if yesterday_total > 0:
                yesterday_accuracy = round((yesterday_pass / yesterday_total) * 100, 1)
            
            # 计算变化
            change = round(today_accuracy - yesterday_accuracy, 1)
            
            return {
                "value": today_accuracy,
                "change": change,
                "today_total": today_total,
                "today_pass": today_pass,
                "yesterday_accuracy": yesterday_accuracy,
                "note": "显示最近的检测记录统计，而非当前日期"
            }
            
        except Exception as e:
            logger.error(f"获取准确率统计时出错: {str(e)}")
            return {
                "value": 0,
                "change": 0
            }
    
    def get_recent_alerts(self, limit: int = 10):
        """获取最近告警"""
        try:
            alerts = self.db.query(Alert)\
                .order_by(desc(Alert.created_at))\
                .limit(limit)\
                .all()
            
            result = []
            for alert in alerts:
                device_name = None
                if alert.device:
                    device_name = alert.device.name
                
                result.append({
                    "id": str(alert.id),
                    "type": alert.type.value,
                    "message": alert.message,
                    "timestamp": int(alert.created_at.timestamp() * 1000),
                    "device_name": device_name,
                    "is_read": alert.is_read
                })
            
            return result
        except Exception as e:
            logger.error(f"获取最近告警时出错: {str(e)}")
            return []
    
    def create_alert(self, message: str, alert_type: AlertType = AlertType.INFO, device_id: int = None):
        """创建新的告警"""
        try:
            alert = Alert(
                type=alert_type,
                message=message,
                device_id=device_id,
                created_at=datetime.now()
            )
            
            self.db.add(alert)
            self.db.commit()
            self.db.refresh(alert)
            
            return alert
        except Exception as e:
            logger.error(f"创建告警时出错: {str(e)}")
            self.db.rollback()
            return None
    
    def mark_alert_as_read(self, alert_id: int):
        """将告警标记为已读"""
        try:
            alert = self.db.query(Alert).filter(Alert.id == alert_id).first()
            if alert:
                alert.is_read = True
                self.db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"标记告警为已读时出错: {str(e)}")
            self.db.rollback()
            return False
    
    def get_device_status_summary(self):
        """获取设备状态摘要"""
        try:
            total = self.db.query(func.count(Device.id)).scalar() or 0
            online = self.db.query(func.count(Device.id))\
                .filter(Device.status == 'online')\
                .scalar() or 0
            offline = self.db.query(func.count(Device.id))\
                .filter(Device.status == 'offline')\
                .scalar() or 0
            error = self.db.query(func.count(Device.id))\
                .filter(Device.status == 'error')\
                .scalar() or 0
            
            cameras = self.db.query(func.count(Device.id))\
                .filter(Device.type == 'camera')\
                .scalar() or 0
            
            return {
                "total": total,
                "online": online,
                "offline": offline,
                "error": error,
                "cameras": cameras,
                "online_rate": round((online / total) * 100 if total > 0 else 0, 1)
            }
        except Exception as e:
            logger.error(f"获取设备状态摘要时出错: {str(e)}")
            return {
                "total": 0,
                "online": 0,
                "offline": 0,
                "error": 0,
                "cameras": 0,
                "online_rate": 0
            }
    
    def get_daily_detection_trends(self, days: int = 7):
        """获取每日检测趋势"""
        try:
            result = []
            today = datetime.now().date()
            
            logger.info(f"当前系统日期：{today}, 查询检测趋势")
            
            # 获取所有检测记录
            all_records = self.db.query(func.count(Detection.id)).scalar() or 0
            if all_records == 0:
                # 如果没有记录，返回空数组
                logger.info("没有检测记录，返回空趋势数据")
                return []
            
            # 查找最近的记录
            latest_detection = self.db.query(Detection).order_by(desc(Detection.timestamp)).first()
            if not latest_detection:
                logger.info("没有找到最近的记录，返回空趋势数据")
                return []
            
            # 获取最近记录的日期
            reference_date = latest_detection.timestamp.date()
            logger.info(f"找到最新记录日期：{reference_date}，计算前{days}天的趋势")
            
            for i in range(days - 1, -1, -1):
                date = reference_date - timedelta(days=i)
                date_str = date.isoformat()
                
                # 查询当日检测总数
                total = self.db.query(func.count(Detection.id))\
                    .filter(func.substr(Detection.timestamp, 1, 10) == date_str)\
                    .scalar() or 0
                
                # 查询当日通过数
                pass_count = self.db.query(func.count(Detection.id))\
                    .filter(func.substr(Detection.timestamp, 1, 10) == date_str)\
                    .filter(Detection.status == DetectionStatus.PASS)\
                    .scalar() or 0
                
                # 查询当日失败数
                fail_count = self.db.query(func.count(Detection.id))\
                    .filter(func.substr(Detection.timestamp, 1, 10) == date_str)\
                    .filter(Detection.status == DetectionStatus.FAIL)\
                    .scalar() or 0
                
                result.append({
                    "date": date.isoformat(),
                    "total": total,
                    "pass": pass_count,
                    "fail": fail_count
                })
                
                logger.info(f"日期 {date_str} 统计：总数={total}, 通过={pass_count}, 失败={fail_count}")
            
            return result
        except Exception as e:
            logger.error(f"获取每日检测趋势时出错: {str(e)}")
            return []

# 创建单例服务实例
def get_dashboard_service(db: Session = Depends(get_db)) -> DashboardService:
    """获取仪表板服务实例"""
    return DashboardService(db)

# 全局实例用于非依赖注入场景
dashboard_service = DashboardService(next(get_db())) 