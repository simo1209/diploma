from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Regexp, Optional


class LoginForm(FlaskForm):
    email = StringField('Email Address', [DataRequired(), Email()])
    password = PasswordField('Password', [DataRequired()])


class RegisterForm(FlaskForm):
    first_name = StringField(
        'First Name',
        validators=[DataRequired()]
    )
    last_name = StringField(
        'Last Name',
        validators=[DataRequired()]
    )
    email = StringField(
        'Email Address',
        validators=[DataRequired(), Email(message=None), Length(min=6, max=40)])
    password = PasswordField(
        'Password',
        validators=[DataRequired(), Length(min=6, max=25)]
    )
    confirm = PasswordField(
        'Confirm password',
        validators=[
            DataRequired(),
            EqualTo('password', message='Passwords must match.')
        ]
    )
    phone = StringField(
        'Phone Number',
        validators=[DataRequired(), Regexp(r'\d{10}')]
    )
    UCN = StringField(
        'Unique citizenship number',
        validators=[DataRequired(), Regexp(r'\d{10}')]
    )
    country = StringField(
        'Country',
        validators=[DataRequired()]
    )
    city = StringField(
        'City',
        validators=[DataRequired()]
    )
    address1 = StringField(
        'Address Line 1',
        validators=[DataRequired()]
    )
    address2 = StringField(
        'Address Line 2'
    )
    postal_code = StringField(
        'Zip/Postal Code',
        validators=[DataRequired()]
    )
