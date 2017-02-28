from sqlalchemy import Column, ForeignKey, Integer, DateTime, String, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
from base import Base
from user import User
from category import Category


class Handicraft(Base):
    __tablename__ = 'handicraft'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    description = Column(String(250))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    pictures = relationship("HandicraftPicture", back_populates="handicraft")

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
            'user': self.user.name,
            'category': self.category.name
        }
