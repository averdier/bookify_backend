# -*- coding: utf-8 -*-

from flask_restplus import fields
from .. import api


offer_post_model = api.model('Offer POST model', {
    'book_id': fields.String(required=True, description='Book ID'),
    'price': fields.Float(required=True, min=0, description='Price')
})


offer_model = api.model('Offer model', {
    'id': fields.String(required=True, description='Offer unique ID'),
    'client_id': fields.String(required=True, description='Client ID'),
    'book_id': fields.String(required=True, description='Book ID'),
    'created_at': fields.DateTime(required=True, description='Creation datetime'),
    'price': fields.Float(required=True, description='Price'),
})
