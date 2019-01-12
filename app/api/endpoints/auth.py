# -*- coding: utf-8 -*-

import time
import jwt
from flask import g, request, current_app
from flask_restplus import Namespace, Resource, abort, marshal
from .. import auth
from ..serializers.auth import token_encoded_model, token_unencoded_model
from ..serializers.users import user_detail_model
from ..parsers import auth_parser
from app.models import Client

ns = Namespace('auth', description='Auth related operations.')


# ================================================================================================
# ENDPOINTS
# ================================================================================================
#
#   API Auth endpoints
#
# ================================================================================================


def is_authorized_client(client_id, secret):
    """
    Verify if is authorized client

    :param client_id:
    :param secret:
    :return:
    """
    response = Client.search().query('match', client_id=client_id).execute()

    if response.hits.total == 0:
        return False

    u = response.hits[0]
    if u.check_secret(secret) and u.confirmed:
        g.user = u
        return True

    return False


@ns.route('/me')
class UserResource(Resource):
    decorators = [auth.login_required]

    @ns.marshal_with(user_detail_model)
    def get(self):
        """
        Get user
        """
        return g.user.to_dict(include_id=True, include_offers=True)


@ns.route('/token')
class TokenResource(Resource):

    @auth.login_required
    @ns.marshal_with(token_unencoded_model)
    def get(self):
        """
        Get unencoded model
        """
        try:
            response = jwt.decode(g.user_token,
                                  current_app.config['PUBLIC_KEY'],
                                  audience='bookify_backend',
                                  algorithms=['RS512']
                                  )

            return response

        except Exception as ex:
            current_app.logger.debug('Invalid token --> {0}'.format(ex))
            abort(400, 'Invalid token')

    @ns.marshal_with(token_encoded_model)
    @ns.expect(auth_parser)
    def post(self):
        """
        Get token
        """
        data = request.form

        audience = 'bookify_backend'

        try:

            if not is_authorized_client(data['client_id'], data['client_secret']):
                abort(401, error='Unauthorized')

            now = int(time.time())
            unencoded = {
                'iss': 'bookify_backend',
                'aud': audience,
                'iat': now,
                'exp': now + 3600 * 24,
                'user': g.user.to_dict(include_id=True)
            }

            token = jwt.encode(unencoded, current_app.config['PRIVATE_KEY'], algorithm='RS512')

            current_app.logger.info('{0} claim token'.format(g.user.client_id))

            return {
                'encoded': token.decode('utf-8'),
                'unencoded': unencoded
            }

        except Exception as ex:
            current_app.logger.error('Unable to create token --> {0}'.format(ex))

            abort(400, error='Unable to create token, please contact administrators')
