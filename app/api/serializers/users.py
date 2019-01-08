# -*- coding: utf-8 -*-

from flask_restplus import fields
from .. import api


user_post_model = api.model('User POST model', {
    'client_id': fields.String(required=True, min_length=3, max_length=32, description='Client ID'),
    'client_secret': fields.String(required=True, min_length=8, max_length=16, description='Client secret'),
    'email': fields.String(required=True, min_length=3, max_length=64, description='Email address')
})

user_model = api.model('User model', {
    'id': fields.Integer(required=True, description='User unique ID'),
    'client_id': fields.String(required=True, description='Client ID'),
    'email': fields.String(required=True, description='Email address')
})
