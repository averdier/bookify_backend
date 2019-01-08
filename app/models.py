# -*- coding: utf-8 -*-

from dateutil.parser import parse
import hashlib
import json
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db


class User(db.Model):
    """
    User model
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.String(32), index=True, unique=True)
    secret_hash = db.Column(db.String(128), nullable=False)

    @property
    def secret(self):
        return self.secret_hash

    @secret.setter
    def secret(self, pwd):
        self.secret_hash = generate_password_hash(pwd)

    def check_secret(self, pwd):
        return check_password_hash(self.secret_hash, pwd)


class Book(db.Model):
    """
    Book model
    """
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    publication = db.Column(db.DateTime)
    isbn = db.Column(db.String(16), index=True, unique=True)
    name = db.Column(db.String(64), nullable=False)
    authors = db.Column(db.String(512), nullable=False)
    cover = db.Column(db.String(64), nullable=False)
    editor = db.Column(db.String(64), nullable=False)
    pages = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(1024))
    genders = db.Column(db.String(512))

    @staticmethod
    def from_dict(data):
        return Book(
            publication=parse(data['publication']),
            isbn=data['isbn'],
            name=data['name'],
            authors=json.dumps(data['authors']),
            cover=data['cover'],
            editor=data['editor'],
            pages=data['pages'],
            description=data.get('description'),
            genders=json.dumps(data['genders'])
        )

    def to_json(self):
        return {
            'id': self.id,
            'publication': self.publication,
            'isbn': self.isbn,
            'name': self.name,
            'authors': json.loads(self.authors),
            'cover': self.cover,
            'editor': self.editor,
            'pages': self.pages,
            'description': self.description,
            'genders': json.loads(self.genders)
        }



