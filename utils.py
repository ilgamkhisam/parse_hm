from db import engine
from models import BASE


def create_tables():
    BASE.metadata.create_all(engine, checkfirst=True)
    print("Таблицы созданы...")


