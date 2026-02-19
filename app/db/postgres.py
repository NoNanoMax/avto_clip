from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def make_engine(dsn: str):
    return create_engine(dsn, pool_pre_ping=True)

def make_session_factory(engine):
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)
