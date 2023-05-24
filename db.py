from config import MYSQL_URL
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker



engine = create_engine(MYSQL_URL)
session=sessionmaker(bind=engine, autoflush=True, autocommit=False)

def get_session(): 
    return session()