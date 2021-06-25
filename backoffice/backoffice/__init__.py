from flask import Flask, jsonify
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_admin import Admin
from flask import json, request, render_template


from backoffice.config import CustomJSONEncoder

import logging
logging.basicConfig(filename='error.log', level=logging.DEBUG)

app = Flask(__name__)

app.config.from_object('backoffice.config.DevelopmentConfig')

app.json_encoder = CustomJSONEncoder

login_manager = LoginManager()
login_manager.init_app(app)

bcrypt = Bcrypt(app)

db = SQLAlchemy(app)

bootstrap = Bootstrap(app)


login_manager.login_view = "administrator.login"
login_manager.login_message_category = 'danger'

from backoffice.models import Account, Administrator, Role, Transaction
from backoffice.admin import AccountModelView, TransactionModelView, AdministratorModelView, RoleModelView


admin = Admin(app, endpoint='admin', template_mode='bootstrap3', url='/admin')

admin.add_view(AdministratorModelView(Administrator, db.session, endpoint='/admin_admins'))
admin.add_view(RoleModelView(Role, db.session, endpoint='/admin_roles'))
admin.add_view(AccountModelView(Account, db.session, endpoint='/admin_accnts'))
admin.add_view(TransactionModelView(Transaction, db.session, endpoint='/admin_trans'))

@login_manager.user_loader
def load_user(administrator_id):
    return Administrator.query.filter(Administrator.id == int(administrator_id)).first()

from backoffice.errors import BaseHTTPException

@app.errorhandler(BaseHTTPException)
def custom_error_handler(e):
    
    if request.args.get('response-type') == 'json':
        response = jsonify(e.to_dict())
        response.status_code = e.status_code
        return response

    return render_template('error.html', e=e)

from backoffice.user.views import administrator_blueprint

app.register_blueprint(administrator_blueprint)

