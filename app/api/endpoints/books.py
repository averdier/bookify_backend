# -*- coding: utf-8 -*-

import json
from flask import request, current_app
from flask_restplus import Namespace, Resource, abort
from .. import auth
from ..serializers.books import book_model, book_post_model, books_container
from ..parsers import books_parsers, search_parsers
from app.models import Book

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
    @ns.expect(books_parsers)
    def get(self):
        """
        Get books
        """
        args = request.args
        start = int(args.get('from', 0))
        if start < 0:
            abort(400, error='from >= 0')

        size = int(args.get('size', current_app.config['PAGINATION_SIZE']))
        if size < 0:
            abort(400, error='size >= 0')

        order = args.get('order', 'desc')
        if order not in ['asc', 'desc']:
            abort(400, error='Unknown order')

        return {
            'books': [
                b.to_json() for b in Book.search().sort({'publication': {'order': order}})[start:size]
            ]
        }

    @ns.expect(book_post_model)
    @ns.marshal_with(book_model)
    def post(self):
        """
        Add book
        """
        data = request.json

        if Book.search().query('match', isbn=data['isbn']).execute().hits.total != 0:
            abort(400, error='ISBN number already exist')

        book = Book.from_dict(data)
        book.save()

        return book.to_json()


@ns.route('/autocomplete/<name>')
class BooksSearchResource(Resource):
    decorators = [auth.login_required]

    @ns.marshal_with(books_container)
    def get(self, name):
        """
        Autocomplete books
        """
        response = Book.search().suggest('auto_complete', name, completion={'field': 'name_suggest'}).execute()
        books = []

        for result in response.suggest.auto_complete:
            for option in result.options:
                payload = option._source.to_dict()
                payload['authors'] = json.loads(payload['authors'])
                payload['genders'] = json.loads(payload['genders'])
                payload['id'] = option._id

                if len(books) < 10:
                    books.append(payload)
                else:
                    break

        return {
            'books': books
        }


@ns.route('/<book_id>')
@ns.response(404, 'Book not found')
class BookResource(Resource):
    decorators = [auth.login_required]

    @ns.marshal_with(book_model)
    def get(self, book_id):
        """
        Get book from id
        """
        book = Book.get(book_id, ignore=404)

        if book:
            return book.to_json()

        else:
            abort(404, error='Book not found')
