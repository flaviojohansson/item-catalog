from datetime import datetime
from sqlalchemy import Column, ForeignKey, Integer, DateTime, String, Numeric
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
    created_at = Column(DateTime, default=datetime.now)


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
        }


class Handicraft(Base):
    __tablename__ = 'handicraft'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    description = Column(String(250))
    price = Column(Numeric(precision=2))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
            'price': self.price,
            'course': self.course,
        }


class HandicraftPicture(Base):
    __tablename__ = 'handicraft_picture'

    id = Column(Integer, primary_key=True)
    file_name = Column(String(80), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    handicraft_id = Column(Integer, ForeignKey('handicraft.id'))
    handicraft = relationship(Handicraft)


engine = create_engine('sqlite:///thehandicrafter.db')


Base.metadata.create_all(engine)