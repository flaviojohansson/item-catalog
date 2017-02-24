from sqlalchemy import Column, ForeignKey, Integer, DateTime, String, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
from base import Base
from handicraft import Handicraft


class HandicraftPicture(Base):
    __tablename__ = 'handicraft_picture'

    id = Column(Integer, primary_key=True)
    file_name = Column(String(80), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    handicraft_id = Column(Integer, ForeignKey('handicraft.id'))
    handicraft = relationship(Handicraft)
