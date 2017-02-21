from datetime import datetime
from sqlalchemy import Column, ForeignKey, Integer, DateTime, String, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import create_engine
import config


Base = declarative_base()

# We can't access app.config at this point
engine = create_engine(config.DATABASE_URI)

# First time create database
# Base.metadata.create_all(engine)


# Connect to Database
Base.metadata.bind = engine

# Database session
DBSession = sessionmaker(bind=engine)
session = DBSession()
