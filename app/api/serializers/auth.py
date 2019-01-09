# -*- coding: utf-8 -*-

from flask_restplus import fields
from .users import api, user_model


token_unencoded_model = api.model('Token unencoded model', {
    'iss': fields.String(required=True, desctiption='Issuer'),
    'aud': fields.String(required=True, description='Audience'),
    'iat': fields.Integer(required=True, description='Issued at'),
    'exp': fields.Integer(required=True, description='Expiration time'),
    'user': fields.Nested(user_model, required=True, description='Client')
})

token_encoded_model = api.model('Token encoded model', {
    'encoded': fields.String(required=True, description='Encoded token'),
    'unencoded': fields.Nested(token_unencoded_model, required=True, description='Unencoded token')
})
