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
<<<<<<< HEAD:flask/diplomaproject/config.py
    QR_CODES = '/home/simo/qr-codes'
    FLASK_ADMIN_SWATCH = 'cerulean'

=======
    QR_CODES = '/home/simo09/qr-codes'
    FLASK_ADMIN_SWATCH = 'cerulean'
>>>>>>> 9b813e16178f8918f0a2377e583c0df6a84532e1:diplomaproject/config.py


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    BCRYPT_LOG_ROUNDS = 12
    SQLALCHEMY_DATABASE_URI = 'postgresql://simo:12092002SsG@localhost:5432/qrpayment'
