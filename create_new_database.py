from datetime import datetime
from sqlalchemy import Column, ForeignKey, Integer, DateTime, String, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import create_engine

import config
import os
from app.models.base import Base, engine, session
from app.models.handicraft import Handicraft
from app.models.category import Category
from app.models.user import User
from app.models.handicraft_picture import HandicraftPicture


print "Checking for directory..."

database_folder = os.path.dirname(os.path.abspath(config.DATABASE_URI.split('///')[1]))
if not os.path.exists(database_folder):
    print "Creating directory {}...".format(database_folder)
    os.mkdir(database_folder)

print "Ok."


print "Creating database ..."

Base.metadata.create_all(engine)

print "Creating categories ..."

session.add(Category(name='Woodwork'))
session.add(Category(name='Knitting'))
session.add(Category(name='Sewing'))
session.add(Category(name='Papercraft'))
session.add(Category(name='Decoupage'))

session.commit()

print "Done. Database created at ease."