from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime
from database_setup import *

# create the datbase file
engine = create_engine('sqlite:///wallpapers.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# RESET DB: For debuggin purposes, check if tables already exist
# and replace with new data.
session.query(Category).delete()
session.query(Wallpapers).delete()
session.query(User).delete()

# Create a default mock user
user1 = User(name="Sys Admin",
             email="admin@localhost",
             picture='http://localhost:8000/static/admin.jpg')
session.add(user1)
session.commit()

# Create a mock categories
Cat1 = Category(name="Animal",
                user_id=1)
session.add(Cat1)
session.commit()

Cat2 = Category(name="Aquarium",
                user_id=1)
session.add(Cat2)
session.commit

Cat3 = Category(name="Automobile",
                user_id=1)
session.add(Cat3)
session.commit()

Cat4 = Category(name="Bird",
                user_id=1)
session.add(Cat4)
session.commit()


# Populate a category with items for testing
# Using different users for items also
Wallpaper1 = Wallpapers(name="Tigers",
                        date=datetime.datetime.now(),
                        description="A really nice wallpaper of two tigers",
                        picture="http://bit.ly/2wzE6K4",
                        category_id=1,
                        user_id=1)
session.add(Wallpaper1)
session.commit()

Wallpaper2 = Wallpapers(name="Plants",
                        date=datetime.datetime.now(),
                        description="This is an underwater plants\
                         inside an aquarium.",
                        picture="http://bit.ly/2gvXbVB",
                        category_id=2,
                        user_id=1)
session.add(Wallpaper2)
session.commit()

Wallpaper3 = Wallpapers(name="Futuistic Car",
                        date=datetime.datetime.now(),
                        description="This is a car of the future concept car.",
                        picture="http://bit.ly/2gCxrL5",
                        category_id=3,
                        user_id=1)
session.add(Wallpaper3)
session.commit()

print "[OK] Mock Data Has Been Created."
