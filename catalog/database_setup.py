from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    items = relationship('Item', lazy='dynamic', cascade="delete")

    @property
    def serialize(self):
        """Return object data in easily serializeable json format"""
        return {
           'id': self.id,
           'name': self.name,
           'Item': [i.serialize for i in self.items]
        }


class Item(Base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    title = Column(String(80), nullable=False)
    description = Column(String(250))
    date_added = Column(DateTime, nullable=False, default=func.now())
    cat_id = Column(Integer, ForeignKey('category.id'))
    user_id = Column(Integer, ForeignKey('user.id'))
    category = relationship(Category)
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable json format"""
        return {
          'id': self.id,
          'title': self.title,
          'description': self.description,
          'date_added': str(self.date_added.isoformat()),
          'cat_id': self.cat_id
        }


engine = create_engine('postgresql://catalog:catal0g@localhost/catalog')
Base.metadata.create_all(engine)
