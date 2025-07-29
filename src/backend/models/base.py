from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
engine = create_engine(
    'sqlite:///./industrial_ocr.db',
    connect_args={"check_same_thread": False},
    pool_pre_ping=True,
    pool_size=20,               # 增加连接池大小
    max_overflow=20,            # 增加最大溢出连接数
    pool_timeout=60,            # 增加获取连接超时时间
    pool_recycle=3600           # 连接回收时间（1小时）
)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)