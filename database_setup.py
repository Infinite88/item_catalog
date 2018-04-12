import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, validates
from sqlalchemy import create_engine
from app import engine

Base = declarative_base()

'''Creates the User Database'''
class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))
    provider = Column(String(25))


'''Creates the Category Item Database'''
class MangaDB(Base):
    __tablename__ = 'manga'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    authorName = Column(String(250), nullable=False)
    description = Column(String(250), nullable=False)
    image = Column(String(255), nullable=False)
    genre = Column(String(100), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @validates('genre')
    def capData(self, key, value):
        return value.capitalize()

    # Serialize function to send JSON in a serialize format
    @property
    def serialize(self):
        return {
            'name': self.name,
            'id': self.id,
            'author': self.authorName,
            'description': self.description,
            'image': self.image,
            'genre': self.genre

        }


Base.metadata.create_all(engine)