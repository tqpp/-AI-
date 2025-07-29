from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from ..dependencies import get_db
from ..services.settings import SettingsService
from pydantic import BaseModel, Field

router = APIRouter(
    prefix="/api/settings",
    tags=["settings"]
)

# Pydantic models
class SettingResponse(BaseModel):
    category: str
    key: str
    value: str
    description: Optional[str] = None
    
    class Config:
        from_attributes = True

class SystemSettingsUpdate(BaseModel):
    auto_save_interval: Optional[int] = None
    data_retention: Optional[str] = None
    alarm_threshold: Optional[int] = None
    language: Optional[str] = None

class MesSettingsUpdate(BaseModel):
    server_url: Optional[str] = None
    api_key: Optional[str] = None

class DeviceCreate(BaseModel):
    name: str
    type: str
    model: Optional[str] = None
    config: Dict[str, Any] = Field(default_factory=dict)

class DeviceUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    model: Optional[str] = None
    status: Optional[str] = None
    config: Optional[Dict[str, Any]] = None

class DeviceResponse(BaseModel):
    id: int
    name: str
    type: str
    model: Optional[str] = None
    status: str
    config: Dict[str, Any]
    
    class Config:
        from_attributes = True

# Routes for general settings
@router.get("/", response_model=List[SettingResponse])
def get_all_settings(category: Optional[str] = None, db: Session = Depends(get_db)):
    service = SettingsService(db)
    return service.get_settings(category)

# Routes for system settings
@router.get("/system", response_model=Dict[str, Any])
def get_system_settings(db: Session = Depends(get_db)):
    service = SettingsService(db)
    return service.get_system_settings()

@router.put("/system", response_model=Dict[str, Any])
def update_system_settings(settings: SystemSettingsUpdate, db: Session = Depends(get_db)):
    service = SettingsService(db)
    # Convert to dict and filter out None values
    settings_dict = {k: v for k, v in settings.dict().items() if v is not None}
    return service.update_system_settings(settings_dict)

# Routes for MES settings
@router.get("/mes", response_model=Dict[str, str])
def get_mes_settings(db: Session = Depends(get_db)):
    service = SettingsService(db)
    return service.get_mes_settings()

@router.put("/mes", response_model=Dict[str, str])
def update_mes_settings(settings: MesSettingsUpdate, db: Session = Depends(get_db)):
    service = SettingsService(db)
    # Convert to dict and filter out None values
    settings_dict = {k: v for k, v in settings.dict().items() if v is not None}
    return service.update_mes_settings(settings_dict)

# Routes for devices
@router.get("/devices", response_model=List[DeviceResponse])
def get_devices(type: Optional[str] = None, db: Session = Depends(get_db)):
    service = SettingsService(db)
    return service.get_devices(type)

@router.get("/devices/{device_id}", response_model=DeviceResponse)
def get_device(device_id: int, db: Session = Depends(get_db)):
    service = SettingsService(db)
    device = service.get_device(device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device

@router.post("/devices", response_model=DeviceResponse)
def create_device(device: DeviceCreate, db: Session = Depends(get_db)):
    service = SettingsService(db)
    return service.create_device(
        name=device.name,
        type=device.type,
        model=device.model,
        config=device.config
    )

@router.put("/devices/{device_id}", response_model=DeviceResponse)
def update_device(device_id: int, device: DeviceUpdate, db: Session = Depends(get_db)):
    service = SettingsService(db)
    # Convert to dict and filter out None values
    device_dict = {k: v for k, v in device.dict().items() if v is not None}
    return service.update_device(device_id, device_dict)

@router.delete("/devices/{device_id}")
def delete_device(device_id: int, db: Session = Depends(get_db)):
    service = SettingsService(db)
    if not service.delete_device(device_id):
        raise HTTPException(status_code=404, detail="Device not found")
    return {"message": "Device deleted successfully"}

@router.put("/devices/{device_id}/status")
def update_device_status(device_id: int, status: str, db: Session = Depends(get_db)):
    service = SettingsService(db)
    return service.update_device_status(device_id, status) 