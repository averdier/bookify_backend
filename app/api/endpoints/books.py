# -*- coding: utf-8 -*-

from flask import request
from flask_restplus import Namespace, Resource, abort
from .. import auth
from ..serializers.books import book_model, book_post_model, books_container
from app.models import Book, db

ns = Namespace('books', description='Books related operations.')


# ================================================================================================
# ENDPOINTS
# ================================================================================================
#
#   API Books endpoints
#
# ================================================================================================


@ns.route('/')
class BooksResource(Resource):
    decorators = [auth.login_required]

    @ns.marshal_with(books_container)
    def get(self):
        """
        Get books
        """
        return {
            'books': [
                b.to_json() for b in Book.query.all()
            ]
        }

    @ns.expect(book_post_model)
    @ns.marshal_with(book_model)
    def post(self):
        """
        Add book
        """
        data = request.json

        if Book.query.filter_by(isbn=data['isbn']).first() is not None:
            abort(400, error='ISBN number already exist')

        book = Book.from_dict(data)
        db.session.add(book)
        db.session.commit()

        return book.to_json()


@ns.route('/<int:book_id>')
@ns.response(404, 'Book not found')
class GoalResource(Resource):
    decorators = [auth.login_required]

    @ns.marshal_with(book_model)
    def get(self, book_id):
        """
        Get book from id
        """
        return Book.query.get_or_404(book_id).to_json()
