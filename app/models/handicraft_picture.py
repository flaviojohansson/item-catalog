from sqlalchemy import Column, ForeignKey, Integer, DateTime, String, Numeric
from base import Base


class HandicraftPicture(Base):
    __tablename__ = 'handicraft_picture'

    id = Column(Integer, primary_key=True)
    file_name = Column(String(80), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    handicraft_id = Column(Integer, ForeignKey('handicraft.id'))
    handicraft = relationship(Handicraft)
