from flask import Flask
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap

app = Flask(__name__)

app.config.from_object('diplomaproject.config.DevelopmentConfig')

login_manager = LoginManager()
login_manager.init_app(app)

bcrypt = Bcrypt(app)

db = SQLAlchemy(app)

bootstrap = Bootstrap(app)


from diplomaproject.models import UserAccount

login_manager.login_view = "user.login"
login_manager.login_message_category = 'danger'


@login_manager.user_loader
def load_user(user_id):
    return UserAccount.query.filter(UserAccount.id == int(user_id)).first()


from diplomaproject.user.views import user_blueprint
app.register_blueprint(user_blueprint)