# -*- coding: utf-8 -*-

from flask_restplus import fields
from .. import api


user_model = api.model('User model', {
    'id': fields.Integer(required=True, description='User unique ID'),
    'client_id': fields.String(required=True, description='Client ID')
})
