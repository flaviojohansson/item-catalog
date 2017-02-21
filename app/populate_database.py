from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Category, User, Handicraft

engine = create_engine('sqlite:///thehandicrafter.db')

# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


#session.add(Category(name='Woodwork'))
#session.add(Category(name='Knitting'))
#session.add(Category(name='Sewing'))
#session.add(Category(name='Papercraft'))
#session.add(Category(name='Decoupage'))

#session.add(User(name='Jenna Jerkins', email='jenna@gmail.com'))

#session.add(
#    Handicraft(
#        name='Minecraft Pillows',
#        description='Creeper, Enderman, Steve and blocks.',
#        price=30.15,
#        category_id=3,
#        user_id=3
#    )
#)

session.commit()


print 'added categories !'
