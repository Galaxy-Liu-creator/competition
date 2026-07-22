"""测试初始化：确保数据库建表并播种（生产环境由 main.py 的 lifespan 完成）。"""

import pytest

from app.db.init_db import init_db


@pytest.fixture(scope="session", autouse=True)
def _prepare_database():
    init_db()
    yield
