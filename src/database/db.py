from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings


engine = create_engine(settings.DB_URL)

_SessionFactory = sessionmaker(bind=engine)

Base = declarative_base()

def session_factory():
    return _SessionFactory()
