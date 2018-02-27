from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Category, Base, Item, User

engine = create_engine('sqlite:///catalog.db')
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


# Create dummy user
User1 = User(name="Robo Barista", email="tinnyTim@udacity.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()

# Ski
category1 = Category(user_id=1, name="Ski")

session.add(category1)
session.commit()

item2 = Item(user_id=1, name="Helmet", 
             description="Head protection for skiers", category=category1)

session.add(item2)
session.commit()


item1 = Item(user_id=1, name="Skis", 
             description="Very good skis to ski", category=category1)

session.add(item1)
session.commit()


# Surf
category1 = Category(user_id=1, name="Surf")

session.add(category1)
session.commit()

item2 = Item(user_id=1, name="Leash", 
             description="Best thing ever invented", category=category1)

session.add(item2)
session.commit()


item1 = Item(user_id=1, name="Surfing Table", 
             description="Nice table to surf", category=category1)

session.add(item1)
session.commit()


# Basketball
category1 = Category(user_id=1, name="Basketball")

session.add(category1)
session.commit()

item2 = Item(user_id=1, name="Ball", 
             description="Ball to play basketball", category=category1)

session.add(item2)
session.commit()


item1 = Item(user_id=1, name="Shoes", 
             description="Nice shoes to play basketball", category=category1)

session.add(item1)
session.commit()


item2 = Item(user_id=1, name="Basket", 
             description="Stand up basket to play basketball", category=category1)

session.add(item2)
session.commit()


# Skateboard
category1 = Category(user_id=1, name="Skateboarding")

session.add(category1)
session.commit()

item2 = Item(user_id=1, name="Skateboard", 
             description="Nice skate to skateboarding", category=category1)

session.add(item2)
session.commit()


item1 = Item(user_id=1, name="Shoes", 
             description="Nice shoes to do skateboarding", category=category1)

session.add(item1)
session.commit()


item2 = Item(user_id=1, name="Wheels", 
             description="Set of 4 wheels for replacement", category=category1)

session.add(item2)
session.commit()

print "added menu items!"