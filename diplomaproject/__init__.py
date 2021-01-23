from flask import Flask
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask import json

from diplomaproject.config import CustomJSONEncoder

app = Flask(__name__)

app.config.from_object('diplomaproject.config.DevelopmentConfig')

app.json_encoder = CustomJSONEncoder

login_manager = LoginManager()
login_manager.init_app(app)

bcrypt = Bcrypt(app)

db = SQLAlchemy(app)

bootstrap = Bootstrap(app)


from diplomaproject.models import Account

login_manager.login_view = "user.login"
login_manager.login_message_category = 'danger'


@login_manager.user_loader
def load_user(account_id):
    return Account.query.filter(Account.id == int(account_id)).first()


from diplomaproject.user.views import user_blueprint
from diplomaproject.transactions.views import transaction_blueprint

app.register_blueprint(user_blueprint)
app.register_blueprint(transaction_blueprint)