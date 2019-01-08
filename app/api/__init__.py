# -*- coding: utf-8 -*-

import os
import jwt
from flask import Blueprint, current_app, g
from flask_restplus import Api
from flask_httpauth import HTTPTokenAuth
from app.models import User


blueprint = Blueprint('api', __name__, url_prefix='/api')
api = Api(blueprint,
          title='Bookify backend',
          version='0.1',
          description='Bookify backend',
          doc='/' if os.environ.get('APP_CONFIG', 'default') != 'production' else None,
          authorizations={
              'tokenKey': {
                  'type': 'apiKey',
                  'in': 'header',
                  'name': 'Authorization'
              }
          },
          security='tokenKey'
          )


auth = HTTPTokenAuth(scheme='Bearer')


@auth.verify_token
def verify_token(token):
    """
    Verify authorization token

    :param token: Token
    :type token: str

    :return: True if valid token, else False
    :rtype: bool
    """
    try:
        response = jwt.decode(
            token,
            current_app.config['PUBLIC_KEY'],
            audience='bookify_backend',
            algorithms=['RS512']
        )
        u = User.query.get(int(response['user']['id']))

        if u is not None and u.confirmed:
            g.user = u
            g.user_token = token
            return True

        return False

    except Exception as ex:
        current_app.logger.warning('Unable to verify token, reason : {0}'.format(ex))

        return False


from .endpoints.auth import ns as auth_namespace
from .endpoints.books import ns as books_namespace
from .endpoints.users import ns as users_namespace

api.add_namespace(auth_namespace)
api.add_namespace(books_namespace)
api.add_namespace(users_namespace)