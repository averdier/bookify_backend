# -*- coding: utf-8 -*-

from dateutil.parser import parse
import json
from werkzeug.security import generate_password_hash, check_password_hash
from elasticsearch_dsl import Document, Keyword, Boolean, Date, Integer, Text, Completion, analyzer, token_filter


class Client(Document):
    """
    Client model
    """
    client_id = Keyword()
    secret_hash = Keyword()
    email = Keyword()
    confirmed = Boolean()

    class Index:
        name = 'client'

    @property
    def secret(self):
        return self.secret_hash

    @secret.setter
    def secret(self, pwd):
        self.secret_hash = generate_password_hash(pwd)

    def check_secret(self, pwd):
        return check_password_hash(self.secret_hash, pwd)

    def to_json(self):
        return {
            'id': self.meta.id,
            'client_id': self.client_id,
            'email': self.email
        }


class Book(Document):
    """
    Book model
    """
    publication = Date()
    isbn = Keyword()

    name = Text(fields={'keyword': Keyword()})
    name_suggest = Completion()

    authors = Keyword()
    cover = Keyword()
    editor = Keyword()
    pages = Integer()
    description = Keyword()
    genders = Keyword()

    class Index:
        name = 'books'

    @staticmethod
    def from_dict(data):
        return Book(
            publication=parse(data['publication']),
            isbn=data['isbn'],
            name=data['name'],
            name_suggest=data['name'],
            authors=json.dumps(data['authors']),
            cover=data['cover'],
            editor=data['editor'],
            pages=data['pages'],
            description=data.get('description'),
            genders=json.dumps(data['genders'])
        )

    def to_json(self):
        return {
            'id': self.meta.id,
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
