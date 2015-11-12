import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

'''Creates the User Database'''
class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))

'''Creates the Category Database'''
class Category(Base):
    __tablename__ = 'category'
   
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    image = Column(String(255))
    items = relationship("CategoryItem", backref="category", cascade="all, delete")

    # Serialize function to send JSON in a serialize format
    @property
    def serialize(self):
        return {
            'name': self.name,
            'id': self.id,
            }

'''Creates the Category Item Database''' 
class CategoryItem(Base):
    __tablename__ = 'category_item'

    name =Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    description = Column(String(250))
    price = Column(String(8))
    image = Column(String(255))
    category_id = Column(Integer,ForeignKey('category.id'))

    # Serialize function to send JSON in a serialize format
    @property
    def serialize(self):
        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
            'price': self.price,
        }
 
engine = create_engine('sqlite:///catalog.db')
Base.metadata.create_all(engine)