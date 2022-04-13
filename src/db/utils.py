from pathlib import Path
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .exc import DBTableNotExist

__all__ = [
    "set_sqlite3_file_path", "get_session", "session_scope", "create_table",
    "check_tables",
]

conn_str = "sqlite:///data.sqlite3"
_SESSION_MAKER = None


def set_sqlite3_file_path(file_path:Path):
    global conn_str
    conn_str = f"sqlite:///{file_path.as_posix()}"


def init_conn():
    global _SESSION_MAKER
    engine = create_engine(conn_str, connect_args={}, echo=False)
    _SESSION_MAKER = sessionmaker(bind=engine)


def get_session():
    if not _SESSION_MAKER:
        init_conn()
    return _SESSION_MAKER()


@contextmanager
def session_scope():
    session = get_session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def create_table():
    from .schema import Base
    engine = create_engine(conn_str, connect_args={}, echo=False)
    Base.metadata.create_all(engine)


def check_tables():
    from sqlalchemy import inspect

    engine = create_engine(conn_str, connect_args={}, echo=False)
    inspector = inspect(engine)
    table_names = list(inspector.get_table_names())
    for name in ('bms', 'song', 'folder'):
        if name not in table_names:
            raise DBTableNotExist(f"table {name} not found")
