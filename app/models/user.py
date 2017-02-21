from sqlalchemy import Column, ForeignKey, Integer, DateTime, String, Numeric
from datetime import datetime
from base import Base


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))
    created_at = Column(DateTime, default=datetime.now)
