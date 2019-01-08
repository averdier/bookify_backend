# -*- coding: utf-8 -*-


from . import api

auth_parser = api.parser()
auth_parser.add_argument('client_id', required=True, type=str, help='Client ID', location='form')
auth_parser.add_argument('client_secret', required=True, type=str, help='Client Secret', location='form')
