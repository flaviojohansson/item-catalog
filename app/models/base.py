from datetime import datetime
from sqlalchemy import Column, ForeignKey, Integer, DateTime, String, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import create_engine
import config
import os


Base = declarative_base()

new_database = os.path.isfile(
    os.path.abspath(config.DATABASE_URI.split('///')[1])
)

# We can't access app.config at this point, so we import config
engine = create_engine(config.DATABASE_URI)

# Connect to Database
Base.metadata.bind = engine

# Database session
DBSession = sessionmaker(bind=engine)
session = DBSession()
