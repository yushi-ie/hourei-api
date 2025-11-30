# db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLite の DBファイルを指定（同じディレクトリに app.db ができる）
SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"

# connect_args は SQLite 特有のおまじない（マルチスレッド対応）
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# セッション（DB とやりとりするための「接続オブジェクト」を作る工場）
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# モデル定義のための基底クラス
Base = declarative_base()

from typing import Generator
from sqlalchemy.orm import Session

def get_db() -> Generator[Session, None, None]:
    """
    FastAPI の Depends から呼び出すための DB セッション提供関数
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

import models  # User モデルをインポート（相対インポート）

# これで models に定義した全テーブルを app.db に作成
Base.metadata.create_all(bind=engine)
