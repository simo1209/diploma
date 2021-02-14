from flask import Flask
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_admin import Admin
from flask import json, request, render_template


from diplomaproject.config import CustomJSONEncoder

import logging
logging.basicConfig(filename='error.log', level=logging.DEBUG)

app = Flask(__name__)

app.config.from_object('diplomaproject.config.DevelopmentConfig')

app.json_encoder = CustomJSONEncoder

login_manager = LoginManager()
login_manager.init_app(app)

bcrypt = Bcrypt(app)

db = SQLAlchemy(app)

bootstrap = Bootstrap(app)


login_manager.login_view = "account.login"
login_manager.login_message_category = 'danger'

from diplomaproject.models import Account, Transaction
from diplomaproject.admin import UserAccountModelView, UserTransactionModelView
from diplomaproject.admin import AdminAccountModelView, AdminTransactionModelView


user_details = Admin(app, endpoint='details',template_mode='bootstrap3', url='/details')

user_details.add_view(UserAccountModelView(Account, db.session, endpoint='/acc'))
user_details.add_view(UserTransactionModelView(Transaction, db.session, endpoint='/trans'))

admin = Admin(app, endpoint='admin', template_mode='bootstrap3', url='/admin')

admin.add_view(AdminAccountModelView(Account, db.session, endpoint='/admin_acc'))
admin.add_view(AdminTransactionModelView(Transaction, db.session, endpoint='/admin_trans'))

@login_manager.user_loader
def load_user(account_id):
    return Account.query.filter(Account.id == int(account_id)).first()

from diplomaproject.user.views import account_blueprint
from diplomaproject.transactions.views import transaction_blueprint

app.register_blueprint(account_blueprint)
app.register_blueprint(transaction_blueprint)

from werkzeug.exceptions import HTTPException

@app.errorhandler(HTTPException)
def handle_exception(e):
    response = e.get_response()
    if isinstance(e, HTTPException):
        response.data = json.dumps({
            "code": e.code,
            "name": e.name,
            "description": e.description,
        })
        response.content_type = "application/json"
        return response
    return render_template("500_generic.html", e=e), 500
