import os
from sqlalchemy import create_engine, Column, Integer, String, TIMESTAMP, CHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import func
from dotenv import load_dotenv
import pymysql

load_dotenv()

# MySQL接続設定
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_NAME = os.getenv("DB_NAME", "pos_app")

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# データベースモデル定義
class PrdMaster(Base):
    __tablename__ = "PRD_MASTER"
    
    PRD_ID = Column(Integer, primary_key=True, autoincrement=True)
    CODE = Column(CHAR(13), unique=True, nullable=False)
    PRODUCT_NAME = Column(String(50), nullable=False)
    COLOR = Column(String(30), nullable=False)
    ITEM_CODE = Column(String(20), nullable=False)
    NAME = Column(String(100), nullable=False)
    PRICE = Column(Integer, nullable=False)

class Trd(Base):
    __tablename__ = "TRD"
    
    TRD_ID = Column(Integer, primary_key=True, autoincrement=True)
    DATETIME = Column(TIMESTAMP, nullable=False, default=func.current_timestamp())
    EMP_CD = Column(CHAR(10), nullable=False)
    STORE_CD = Column(CHAR(5), nullable=False, default='30')
    POS_NO = Column(CHAR(3), nullable=False, default='90')
    TOTAL_AMT = Column(Integer, nullable=False, default=0)

class TrdDtl(Base):
    __tablename__ = "TRD_DTL"
    
    TRD_ID = Column(Integer, primary_key=True)
    DTL_ID = Column(Integer, primary_key=True)
    PRD_ID = Column(Integer, nullable=False)
    PRD_CODE = Column(CHAR(13), nullable=False)
    PRD_NAME = Column(String(100), nullable=False)
    PRD_PRICE = Column(Integer, nullable=False)

# データベースセッションの取得
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()