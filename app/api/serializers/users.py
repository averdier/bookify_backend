# -*- coding: utf-8 -*-

from flask_restplus import fields
from .offers import api, offer_model


user_post_model = api.model('Client POST model', {
    'client_id': fields.String(required=True, min_length=3, max_length=32, description='Client ID'),
    'client_secret': fields.String(required=True, min_length=8, max_length=16, description='Client secret'),
    'email': fields.String(required=True, min_length=3, max_length=64, description='Email address'),
    'favorite_genders': fields.List(fields.String(), required=True, description='Favorite genders')
})

user_patch_model = api.model('Client PATCH model', {
    'favorite_genders': fields.List(fields.String(), required=False, description='Favorite genders')
})

user_model = api.model('Client model', {
    'id': fields.String(required=True, description='Client unique ID'),
    'client_id': fields.String(required=True, description='Client ID'),
    'email': fields.String(required=True, description='Email address')
})

user_detail_model = api.inherit('Client detail model', user_model, {
    'balance': fields.Float(required=True, description='Balance'),
    'favorite_genders': fields.List(fields.String(), required=True, description='Favorite genders'),
    'offers': fields.List(fields.Nested(offer_model), description='Offers')
})
