# -*- coding: utf-8 -*-

import re
from flask import g, request, current_app, url_for
from flask_restplus import Namespace, Resource, abort
from .. import auth
from flask_mail import Message
from app.extensions import mail
from itsdangerous import URLSafeTimedSerializer
from ..serializers.users import user_post_model, user_patch_model, user_model
from app.models import Client
from app.utils import render_email

ns = Namespace('users', description='Users related operations.')


# ================================================================================================
# ENDPOINTS
# ================================================================================================
#
#   API Users endpoints
#
# ================================================================================================


@ns.route('/')
class UserResource(Resource):
    decorators = [auth.login_required]

    @ns.expect(user_patch_model)
    @ns.marshal_with(user_model)
    def patch(self):
        """
        Update user
        """
        data = request.json

        if data.get('favorite_genders'):
            g.user.favorite_genders = data['favorite_genders']
            g.user.save()

        return g.user


@ns.route('/register')
class UsersResource(Resource):

    @ns.expect(user_post_model)
    @ns.response(200, 'Client successfully registered')
    def post(self):
        """
        Register user
        """
        data = request.json

        if Client.search().query('match', client_id=data['client_id']).execute().hits.total != 0:
            abort(400, error='Client id already exist')

        if Client.search().query('match', email=data['email']).execute().hits.total != 0:
            abort(400, error='Email already exist')

        if not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", data['email']):
            abort(400, error='{0} not pass email regex.'.format(data['email']))

        user = Client(
            client_id=data['client_id'],
            email=data['email'],
            secret=data['client_secret']
        )

        try:
            serializer = URLSafeTimedSerializer(current_app.config['PRIVATE_KEY'])
            token = serializer.dumps(user.email, salt=current_app.config['SALT_KEY'])

            payload = {
                'confirm_url': url_for('api.users_confirm_resource', token=token, _external=True),
            }

            msg = Message(
                recipients=[data['email']],
                html=render_email('register.html', payload),
                subject='Register'
            )

            mail.send(msg)

            user.save()

            return 'Client successfully registered', 200

        except Exception as ex:
            current_app.logger.error('Unable to register user --> {0}'.format(ex))
            abort(400, error='Unable to register user, please contact administrator')


@ns.route('/confirm/<token>')
@ns.response(404, 'Token not found')
class ConfirmResource(Resource):

    @ns.response(200, 'Client successfully confirmed')
    def get(self, token):
        """
        Confirm registration
        """
        serializer = URLSafeTimedSerializer(current_app.config['PRIVATE_KEY'])
        try:
            email = serializer.loads(
                token,
                salt=current_app.config['SALT_KEY'],
                max_age=3600
            )

            response = Client.search().query('match', email=email).execute()
            if response.hits.total == 0:
                abort(404, error='Token not found')

            user = response.hits[0]
            user.confirmed = True
            user.save()

            return 'Client successfully confirmed', 200

        except Exception as ex:
            current_app.logger.error('Unable to confirm user --> {0}'.format(ex))
            abort(400, error='Invalid token')
