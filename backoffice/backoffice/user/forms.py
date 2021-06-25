from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email, ValidationError

from backoffice import db
from backoffice.models import Administrator

class LoginForm(FlaskForm):
    email = StringField('Email Address', [DataRequired(), Email()])
    password = PasswordField('Password', [DataRequired()])

    def validate_email(form, field):
        if db.session.query(Administrator).filter_by(email=field.data).count() == 0:
            raise ValidationError('Account not found')

