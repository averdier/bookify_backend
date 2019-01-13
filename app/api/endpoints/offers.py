# -*- coding: utf-8 -*-

from flask import request, g
from flask_restplus import Namespace, Resource, abort
from ..serializers.offers import offer_post_model, offer_model
from .. import auth
from app.models import Book

ns = Namespace('offers', description='Offers related operations.')


# ================================================================================================
# ENDPOINTS
# ================================================================================================
#
#   API Offers endpoints
#
# ================================================================================================


@ns.route('/')
class OffersResource(Resource):
    decorators = [auth.login_required]

    @ns.expect(offer_post_model)
    @ns.marshal_with(offer_model)
    def post(self):
        """
        Add offer
        """
        data = request.json
        book = Book.get(data['book_id'], ignore=404)

        if book is None:
            abort(404, error='Book not found')

        offer = book.add_offer(g.user.client_id, data['price'])

        return offer.to_dict(include_id=True)


@ns.route('/<offer_id>')
@ns.response(404, 'Offer not found')
class OfferResource(Resource):
    decorators = [auth.login_required]

    def put(self, offer_id):
        """
        Update offer
        """
        abort(400, error='Not yet implemented')

    @ns.response(204, 'Offer successfully deleted')
    def delete(self, offer_id):
        """
        Delete offer
        """
        abort(400, error='Not yet implemented')


@ns.route('/<offer_id>/purchase')
@ns.response(404, 'Offer not found')
class OfferPurchaseResource(Resource):
    decorators = [auth.login_required]

    def get(self, offer_id):
        """
        Purchase offer
        """
        abort(400, error='Not yet implemented')
