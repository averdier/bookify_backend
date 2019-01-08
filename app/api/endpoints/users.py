# -*- coding: utf-8 -*-

import re
from flask import g, request, current_app, url_for
from flask_restplus import Namespace, Resource, abort
from flask_mail import Message
from app.extensions import mail
from itsdangerous import URLSafeTimedSerializer
from ..serializers.users import user_post_model
from app.models import User, db
from app.utils import render_email

ns = Namespace('users', description='Users related operations.')


# ================================================================================================
# ENDPOINTS
# ================================================================================================
#
#   API Users endpoints
#
# ================================================================================================

@ns.route('/register')
class UsersResource(Resource):

    @ns.expect(user_post_model)
    @ns.response(200, 'User successfully registered')
    def post(self):
        """
        Register user
        """
        data = request.json

        if User.query.filter_by(client_id=data['client_id']).first() is not None:
            abort(400, error='Client id already exist')

        if User.query.filter_by(email=data['email']).first() is not None:
            abort(400, error='Email already exist')

        if not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", data['email']):
            abort(400, error='{0} not pass email regex.'.format(data['email']))

        user = User(
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

            db.session.add(user)
            db.session.commit()

            return 200, 'User successfully register'

        except Exception as ex:
            current_app.logger.error('Unable to register user --> {0}'.format(ex))
            abort(400, error='Unable to register user, please contact administrator')


@ns.route('/confirm/<token>')
@ns.response(404, 'Token not found')
class ConfirmResource(Resource):

    @ns.response(200, 'User successfully confirmed')
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

            user = User.query.filter_by(email=email).first()

            if user is None:
                abort(404, error='Token not found')

            user.confirmed = True

            db.session.add(user)
            db.session.commit()

            return 200, 'User successfully confirmed'

        except Exception as ex:
            current_app.logger.error('Unable to confirm user --> {0}'.format(ex))
            abort(400, error='Invalid token')
