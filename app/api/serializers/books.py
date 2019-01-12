# -*- coding: utf-8 -*-

from flask_restplus import fields
from .offers import api, offer_model


book_post_model = api.model('Book POST model', {
    'publication': fields.DateTime(required=True, description='Publication datetime'),
    'isbn': fields.String(required=True, min_length=10, max_length=16, description='Unique ISBN'),
    'name': fields.String(required=True, min_length=3, max_length=64, description='Name'),
    'authors': fields.List(fields.String(min_length=3, max_length=32), required=True, min_items=1, description='Authors'),
    'cover': fields.String(required=True, description='Cover uri'),
    'editor': fields.String(required=True, min_length=3, max_length=64, description='Editor'),
    'pages': fields.Integer(required=True, exclusiveMin=0, description='Number of pages'),
    'description': fields.String(required=True, max_length=1024, description='Description'),
    'genders': fields.List(fields.String(min_length=3, max_length=32), required=True, min_items=1, description='Genders')
})

book_model = api.model('Book model', {
    'id': fields.String(required=True, description='Unique ID'),
    'publication': fields.DateTime(required=True, description='Publication datetime'),
    'isbn': fields.String(required=True, description='Unique ISBN'),
    'name': fields.String(required=True, description='Name'),
    'authors': fields.List(fields.String(), required=True, description='Authors'),
    'cover': fields.String(required=True, description='Cover uri'),
    'editor': fields.String(required=True, description='Editor'),
    'pages': fields.Integer(required=True, description='Number of pages'),
    'description': fields.String(required=True, description='Description'),
    'genders': fields.List(fields.String(), required=True, description='Genders'),
    'last_offer': fields.DateTime(required=True, description='Last offer datetime'),
    'min_price': fields.Float(required=True, description='Min price'),
    'max_price': fields.Float(required=True, description='Max price'),
    'nb_offers': fields.Integer(required=True, description='Nb offers')
})

book_detail_model = api.inherit('Book detail model', book_model, {
    'offers': fields.List(fields.Nested(offer_model), description='Offers')
})

books_container = api.model('Books container', {
    'books': fields.List(fields.Nested(book_model), required=True, description='Books')
})
