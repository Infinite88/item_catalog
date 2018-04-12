import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, validates
from sqlalchemy import create_engine
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

'''Creates the User Database'''
class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(255), nullable=False)
    email = db.Column(String(250), nullable=False)
    picture = db.Column(String(250))
    provider = db.Column(String(25))


'''Creates the Category Item Database'''
class MangaDB(db.Model):
    __tablename__ = 'manga'

    name = db.Column(String(80), nullable=False)
    id = db.Column(Integer, primary_key=True)
    authorName = db.Column(String(250), nullable=False)
    description = db.Column(String(250), nullable=False)
    image = db.Column(String(255), nullable=False)
    genre = db.Column(String(100), nullable=False)
    user_id = db.Column(Integer, db.ForeignKey('user.id'))
    user = db.relationship(User)

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

