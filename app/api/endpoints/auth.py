# -*- coding: utf-8 -*-

import time
import jwt
from flask import g, request, current_app
from flask_restplus import Namespace, Resource, abort, marshal
from .. import auth
from ..serializers.auth import user_model, token_encoded_model, token_unencoded_model
from ..parsers import auth_parser
from app.models import User

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
    u = User.query.filter_by(client_id=client_id).first()

    if u is None:
        return False

    if u.check_secret(secret) and u.confirmed:
        g.user = u
        return True

    return False


@ns.route('/me')
class UserResource(Resource):
    decorators = [auth.login_required]

    @ns.marshal_with(token_unencoded_model)
    def get(self):
        """
        Get unencoded token
        """
        try:
            response = jwt.decode(g.user_token,
                                  current_app.config['PUBLIC_KEY'],
                                  audience='bookify_backend',
                                  algorithms=['RS512']
                                  )
            current_app.logger.info('{0} get profile'.format(g.user.client_id))

            return response

        except Exception as ex:
            current_app.logger.debug('Invalid token --> {0}'.format(ex))
            abort(400, 'Invalid token')


@ns.route('/token')
class TokenResource(Resource):

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
                'user': marshal(g.user, user_model)
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
