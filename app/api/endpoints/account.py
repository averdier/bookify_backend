# -*- coding: utf-8 -*-

from flask import request, g
from flask_restplus import Namespace, Resource
from ..serializers.users import user_detail_model, user_patch_model
from .. import auth

ns = Namespace('account', description='Account related operations.')


# ================================================================================================
# ENDPOINTS
# ================================================================================================
#
#   API Account endpoints
#
# ================================================================================================


@ns.route('/')
class AccountResource(Resource):
    decorators = [auth.login_required]

    @ns.marshal_with(user_detail_model)
    def get(self):
        """
        Get account information
        """
        return g.user.to_dict(include_id=True, include_offers=True)

    @ns.expect(user_patch_model)
    @ns.marshal_with(user_detail_model)
    def patch(self):
        """
        Update account information
        """
        data = request.json

        if data.get('favorite_genders'):
            g.user.favorite_genders = data['favorite_genders']
            g.user.save()

        return g.user.to_dict(include_id=True)
