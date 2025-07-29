from sqlalchemy.orm import Session
from .models.base import Base, SessionLocal

# 数据库会话依赖项
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
