# General configuration (development, production)

import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('CLASSFORGE_SECRET_KEY') or 'CLASSFORGE'
    DEBUG = True # Set to False for productions
    DB_USER = 'postgres'
    DB_PASSWORD = 'dbpassword'
    DB_HOST = 'localhost'
    DB_PORT = '5432'
    DB_NAME = 'easyresi'

    SQLALCHEMY_DATABASE_URI = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'

    SQLALCHEMY_TRACK_MODIFICATIONS = False
