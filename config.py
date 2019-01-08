# -*- coding: utf-8 -*-

import os
import logging
from logging.handlers import RotatingFileHandler

basedir = os.path.dirname(__file__)


class Config:
    ADMINS = os.environ.get('ADMINS', '').split(',')

    PRIVATE_KEY = os.environ.get('PRIVATE_KEY', os.path.join(basedir, 'auth_privkey.pem'))
    PUBLIC_KEY = os.environ.get('PUBLIC_KEY', os.path.join(basedir, 'auth_pubkey.pem'))

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI', 'sqlite:///' + os.path.join(basedir, 'app.db'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    LOG_PATH = os.environ.get('LOG_PATH', os.path.join(basedir, 'goals_backend.log'))
    LOG_SIZE = int(os.environ.get('LOG_SIZE', '20000'))
    LOG_COUNT = int(os.environ.get('LOG_COUNT', '10'))
    LOG_ENCODING = os.environ.get('LOG_ENCODING', 'utf-8')

    RESTPLUS_SWAGGER_UI_DOC_EXPANSION = 'list'
    RESTPLUS_VALIDATE = True
    RESTPLUS_MASK_SWAGGER = False
    RESTPLUS_ERROR_404_HELP = True
    JSON_SORT_KEYS = False

    @staticmethod
    def init_app(app):
        """
        Init app

        :param app: Flask App
        :type app: Flask

        """
        with open(app.config['PRIVATE_KEY']) as f:
            app.config['PRIVATE_KEY'] = f.read()

        with open(app.config['PUBLIC_KEY']) as f:
            app.config['PUBLIC_KEY'] = f.read()


class DevelopmentConfig(Config):
    """
    Development configuration
    """
    DEBUG = True

    @staticmethod
    def init_app(app):
        """
        Init app

        :param app: Flask App
        :type app: Flask
        """
        Config.init_app(app)

        for hdler in app.logger.handlers:
            if isinstance(hdler, logging.FileHandler):
                if hdler.baseFilename == os.path.abspath(os.fspath(app.config['LOG_PATH'])):
                    return

        handler = RotatingFileHandler(app.config['LOG_PATH'],
                                      maxBytes=app.config['LOG_SIZE'],
                                      backupCount=app.config['LOG_COUNT'],
                                      encoding=app.config['LOG_ENCODING'])
        formatter = logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'
        )

        handler.setFormatter(formatter)
        handler.setLevel(logging.INFO)

        app.logger.addHandler(handler)


class ProductionConfig(Config):
    """
    Production configuration
    """
    DEBUG = False

    @staticmethod
    def init_app(app):
        """
        Init app

        :param app: Flask App
        :type app: Flask
        """
        DevelopmentConfig.init_app(app)


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
