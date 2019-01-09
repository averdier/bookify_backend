# -*- coding: utf-8 -*-


from . import api

auth_parser = api.parser()
auth_parser.add_argument('client_id', required=True, type=str, help='Client ID', location='form')
auth_parser.add_argument('client_secret', required=True, type=str, help='Client Secret', location='form')

books_parsers = api.parser()
books_parsers.add_argument('from', required=False, type=int, help='From', location='args')
books_parsers.add_argument('size', required=False, type=int, help='Size', location='args')
books_parsers.add_argument('order', required=False, type=str, help='Order (asc|desc)', location='args')

search_parsers = books_parsers.copy()
search_parsers.add_argument('name', required=False, type=str, help='Name', location='args')
