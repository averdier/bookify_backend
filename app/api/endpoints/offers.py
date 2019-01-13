# -*- coding: utf-8 -*-

from flask import request, g
from flask_restplus import Namespace, Resource, abort
from ..serializers.offers import offer_post_model, offer_put_model, offer_model
from .. import auth
from app.models import Book, BookOffer

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

    @ns.marshal_with(offer_model)
    @ns.expect(offer_put_model)
    def put(self, offer_id):
        """
        Update offer
        """
        data = request.json

        offer = BookOffer.get(id=offer_id, ignore=404)
        if offer is None:
            abort(404, error='Offer not found')

        if offer.client_id != g.user.client_id:
            abort(404, error='Offer not found')

        if offer.purchased:
            abort(400, error='Offer purchased')

        offer.price = data['price']
        offer.save(refresh=True)

        book = Book.get(id=offer.book_id, ignore=404)
        if book is not None:
            book.update_offers_summary()

        return offer.to_dict(include_id=True)

    @ns.response(204, 'Offer successfully deleted')
    def delete(self, offer_id):
        """
        Delete offer
        """
        offer = BookOffer.get(id=offer_id, ignore=404)
        if offer is None:
            abort(404, error='Offer not found')

        if offer.client_id != g.user.client_id:
            abort(404, error='Offer not found')

        if offer.purchased:
            abort(400, error='Offer purchased')

        offer.delete(refresh=True)

        return 'Offer successfully deleted', 204


@ns.route('/<offer_id>/purchase')
@ns.response(404, 'Offer not found')
class OfferPurchaseResource(Resource):
    decorators = [auth.login_required]

    @ns.response(204, 'Offer successfully purchased')
    def get(self, offer_id):
        """
        Purchase offer
        """
        offer = BookOffer.get(id=offer_id, ignore=404)
        if offer is None:
            abort(404, error='Offer not found')

        try:
            offer.purchase(g.user)

            return 'Offer successfully purchased', 204

        except Exception as ex:
            abort(400, error='{0}'.format(ex))
