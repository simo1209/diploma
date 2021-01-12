from flask import render_template, Blueprint, request
from flask_login import login_user, logout_user, login_required

from diplomaproject import bcrypt, db
from diplomaproject.models import UserAccount
from diplomaproject.models import Address
from diplomaproject.user.forms import LoginForm, RegisterForm


user_blueprint = Blueprint('user', __name__)


@user_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    print(request.form)
    print(type(request.form))
    form = RegisterForm(request.form)

    if form.validate_on_submit():

        address = Address(
            addr_1=form.address1.data,
            addr_2=form.address2.data,
            city=form.city.data,
            country=form.country.data,
            postal_code=form.postal_code.data
        )

        user_account = UserAccount(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            password=form.password.data,
            phone=form.phone.data,
            UCN=form.UCN.data,
            address=address
        )

        db.session.add(address)
        db.session.add(user_account)
        db.session.commit()

        login_user(user_account)

        return "Successfully Registered", 201
    return render_template('register.html', form=form)


@user_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if form.validate_on_submit():
        user = UserAccount.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(
                user.password, request.form['password']):
            login_user(user)
            return "Authenticated", 200
        else:
            return render_template('login.html', form=form)
    return render_template('login.html', title='Please Login', form=form)
