from flask import render_template, Blueprint, request, jsonify, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import exc

from diplomaproject import bcrypt, db
from diplomaproject.models import Account
from diplomaproject.models import Address
from diplomaproject.user.forms import LoginForm, RegisterForm
from werkzeug.exceptions import Conflict, BadRequest, Unauthorized


user_blueprint = Blueprint('user', __name__)


@user_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)

    if request.method == 'GET':
        return render_template('register.html', form=form)

    if form.validate_on_submit():

        address = Address(
            addr_1=form.address1.data,
            addr_2=form.address2.data,
            city=form.city.data,
            country=form.country.data,
            postal_code=form.postal_code.data
        )

        account = Account(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            password=form.password.data,
            phone=form.phone.data,
            UCN=form.UCN.data,
            address=address
        )

        db.session.add(address)
        db.session.add(account)
        try:
            db.session.commit()
        except exc.IntegrityError:
            db.session.rollback()
            raise Conflict('Email already taken')

        login_user(account)

        return render_template('menu.html', account=account), 201
    else:
        raise BadRequest('Invalid form data')

@user_blueprint.route('/', methods=['GET', 'POST'])
@user_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)

    if request.method == 'GET':
        return render_template('login.html', title='Please Login', form=form)

    if form.validate_on_submit():
        account = Account.query.filter_by(email=form.email.data).first()
        if account and bcrypt.check_password_hash(
                account.password, request.form['password']):
            login_user(account)
            return render_template('menu.html', account=account), 200
        else:
            return Unauthorized('Wrong username or password')

@user_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('user.login'))

@user_blueprint.route('/account', methods=['GET'])
@login_required
def get_account():
    return jsonify(
        Account.query.filter_by(id=current_user.id).with_entities(
            Account.first_name,
            Account.last_name,
            Account.email,
            Account.balance
        ).first()._asdict()
    )
