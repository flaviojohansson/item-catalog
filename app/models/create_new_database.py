from datetime import datetime
from sqlalchemy import Column, ForeignKey, Integer, DateTime, String, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import create_engine

from base import Base, engine, session
from handicraft import Handicraft
from category import Category
from user import User
from handicraft_picture import HandicraftPicture


Base.metadata.create_all(engine)

session.add(Category(name='Woodwork'))
session.add(Category(name='Knitting'))
session.add(Category(name='Sewing'))
session.add(Category(name='Papercraft'))
session.add(Category(name='Decoupage'))

session.commit()
