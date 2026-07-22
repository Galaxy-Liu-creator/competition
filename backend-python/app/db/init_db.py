"""建表 + 播种入口。"""

from app.db import models  # noqa: F401  确保所有 ORM 模型完成注册
from app.db.database import Base, SessionLocal, engine
from app.db.seed import seed


def init_db() -> None:
    """创建所有表；若为空库则写入种子数据。"""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seeded = seed(db)
        if seeded:
            print("[init_db] 已写入演示种子数据。")
        else:
            print("[init_db] 数据库已存在数据，跳过播种。")
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
