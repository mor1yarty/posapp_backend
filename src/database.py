import os
from sqlalchemy import create_engine, Column, Integer, String, TIMESTAMP, CHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import func
import psycopg2

# 開発環境でのみ.envファイルを読み込み
if os.getenv("ENVIRONMENT") != "production":
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        # dotenvが利用できない場合はスキップ
        pass

# Supabase PostgreSQL接続設定
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://zhppoucgzyogewhdjire.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpocHBvdWNnenlvZ2V3aGRqaXJlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE3OTMzMjgsImV4cCI6MjA2NzM2OTMyOH0.rS8EoZq0AUPsAukWBBWfmco_LSmULXl9fxF0gMvMOhE")

# PostgreSQL接続設定（Supabase）
DB_HOST = "db.zhppoucgzyogewhdjire.supabase.co"
DB_PORT = 5432
DB_USER = "postgres"
DB_PASSWORD = os.getenv("SUPABASE_DB_PASSWORD", "step4pos-supabase")
DB_NAME = "postgres"

# PostgreSQL接続文字列（Supabase）
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Supabase用の接続設定
connect_args = {}

# SSL設定付きでエンジンを作成
engine = create_engine(DATABASE_URL, echo=True, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# データベースモデル定義（PostgreSQL/Supabase用）
class PrdMaster(Base):
    __tablename__ = "prd_master"
    
    prd_id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(CHAR(13), unique=True, nullable=False)
    product_name = Column(String(50), nullable=False)
    color = Column(String(30), nullable=False)
    item_code = Column(String(20), nullable=False)
    name = Column(String(100), nullable=False)
    price = Column(Integer, nullable=False)

class Trd(Base):
    __tablename__ = "trd"
    
    trd_id = Column(Integer, primary_key=True, autoincrement=True)
    datetime = Column(TIMESTAMP, nullable=False, default=func.current_timestamp())
    emp_cd = Column(CHAR(10), nullable=False)
    store_cd = Column(CHAR(5), nullable=False, default='30')
    pos_no = Column(CHAR(3), nullable=False, default='90')
    total_amt = Column(Integer, nullable=False, default=0)
    ttl_amt_ex_tax = Column(Integer, nullable=True, comment='合計金額（税抜）')  # 🆕 Lv2追加

class TrdDtl(Base):
    __tablename__ = "trd_dtl"
    
    trd_id = Column(Integer, primary_key=True)
    dtl_id = Column(Integer, primary_key=True)
    prd_id = Column(Integer, nullable=False)
    prd_code = Column(CHAR(13), nullable=False)
    prd_name = Column(String(100), nullable=False)
    prd_price = Column(Integer, nullable=False)
    tax_cd = Column(CHAR(2), nullable=True, default='10', comment='消費税区分')  # 🆕 Lv2追加

# データベースセッションの取得
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()