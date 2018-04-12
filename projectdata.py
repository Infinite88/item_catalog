from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import db, User, MangaDB
from app import session
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()

User1 = User(name='admin', email='jlew2024@yahoo.com')
session.add(User1)
session.commit()

manga1 = MangaDB(name='Naruto', authorName='Masashi Kishimoto',
                 image='https://dw9to29mmj727.cloudfront.net/products/1569319006.jpg',
                 description='Twelve years ago the Village Hidden in the Leaves was attacked by a fearsome threat.',
                 genre='Action-Adventure', user_id=1)
session.add(manga1)
session.commit()

manga2 = MangaDB(name='Bleach', authorName='Tite Kubo',
                 image='https://dw9to29mmj727.cloudfront.net/products/1591167280.jpg',
                 description="Ichigo Kurosaki may not know this, but the world he lives in is one predicated on"
                             " balance--between the living and the dead, between everyday life and the Soul Society. "
                              , genre='action-adventure', user_id=1)

session.add(manga2)
session.commit()


print('Manga Added')