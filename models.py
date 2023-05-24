from sqlalchemy import Column, Integer, String, Text, DECIMAL
from sqlalchemy.orm import declarative_base

BASE = declarative_base()


from db import get_session

class PostManager(): 
    
    def __init__(self): 
        self.model = MyModel
        self.session = get_session()

    def insert_data(self, data): 
        self.session.add(
            self.model(
            title = data['title'],
            price_som = data['price_som'],
            price_dollar = data['price_dollar'],
            description = data['description'],
            link = data['link']
            )
        )
        self.session.commit()
        self.session.close()

    def check_link(self, link):
        from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
        try:
            r=self.session.query(self.model).filter_by(link=link).one()
            self.session.close()
            return True # Возвращает True если в базе есть уже эта запись
        except NoResultFound:
            return False # Возвращает False, если в базе отсутствует эта ссылка.
        except MultipleResultsFound:
            return True


class MyModel(BASE):
    __tablename__ = 'main_table'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price_som = Column(DECIMAL(10,2), nullable=False)
    price_dollar = Column(DECIMAL(10,2), nullable=False)
    link = Column(String(2048))

    

