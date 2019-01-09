# -*- coding: utf-8 -*-

from flask import Flask, request
from flask_cors import CORS
from config import config
from elasticsearch_dsl.connections import connections
from .extensions import mail


def create_app(config_name='default'):
    """
    Create Flask app
    :param config_name:
    :return: Flask
    """

    from .api import blueprint as api_blueprint

    app = Flask(__name__)
    CORS(app, resources={
        r"/api/*": {"origins": "*"}
    })

    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    connections.create_connection(
        hosts=app.config['ELASTICSEARCH_HOST'],
        http_auth=(app.config['ELASTICSEARCH_USER'], app.config['ELASTICSEARCH_SECRET']),
        timeout=20
    )
    connections.get_connection()

    app.register_blueprint(api_blueprint)

    extensions(app)

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        if request.method == 'OPTIONS':
            response.headers['Access-Control-Allow-Methods'] = 'DELETE, GET, POST, PUT'
            headers = request.headers.get('Access-Control-Request-Headers')
            if headers:
                response.headers['Access-Control-Allow-Headers'] = headers

        return response

    return app


def extensions(flask_app):
    """
    Init extensions
    """
    mail.init_app(flask_app)
