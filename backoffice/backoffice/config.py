import os

from flask import json
import decimal

basedir = os.path.abspath(os.path.dirname(__file__))

class CustomJSONEncoder(json.JSONEncoder): #Encode Account balance to string

    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return str(obj)
        return super(CustomJSONEncoder, self).default(obj)

class BaseConfig(object):
    SECRET_KEY = 'secret'
    DEBUG = False
    BCRYPT_LOG_ROUNDS = 10
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False
    QR_CODES = '/home/simo/qr-codes'
    FLASK_ADMIN_SWATCH = 'cerulean'



class DevelopmentConfig(BaseConfig):
    DEBUG = True
    BCRYPT_LOG_ROUNDS = 12
    SQLALCHEMY_DATABASE_URI = 'postgresql://simo:12092002SsG@localhost:5432/qrpayment'
