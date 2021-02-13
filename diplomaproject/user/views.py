from flask import render_template, Blueprint, request, jsonify, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import exc

from diplomaproject import bcrypt, db
from diplomaproject.models import Account
from diplomaproject.models import Address
from diplomaproject.user.forms import LoginForm, RegisterForm
from werkzeug.exceptions import Conflict, BadRequest, Unauthorized


account_blueprint = Blueprint('account', __name__)

@account_blueprint.route('/register', methods=['GET'])
def register_form():
    form = RegisterForm(request.form)
    return render_template('register.html', form=form)


@account_blueprint.route('/accounts/register', methods=['POST'])
def register():
    form = RegisterForm(request.form)

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
        raise Unauthorized('Invalid form data')

@account_blueprint.route('/', methods=['GET'])
@account_blueprint.route('/login', methods=['GET'])
def login_form():
    form = LoginForm(request.form)
    return render_template('login.html', title='Please Login', form=form)


@account_blueprint.route('/account', methods=['GET'])
@login_required
def account_view():
    account = Account.query.filter_by(id=current_user.id).first()
    return render_template('menu.html', account=account)

@account_blueprint.route('/accounts/login', methods=['POST'])
def login():
    form = LoginForm(request.form)

    if form.validate_on_submit():
        account = Account.query.filter_by(email=form.email.data).first()
        if account and bcrypt.check_password_hash(
                account.password, request.form['password']):
            account.login_attempts = 0
            db.session.commit()
            login_user(account)
            return render_template('menu.html', account=account), 200
        elif account:
            account.login_attempts+=1
            db.session.commit()            
    return Unauthorized('Wrong username or password')

@account_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('account.login_form'))

@account_blueprint.route('/accounts/account', methods=['GET'])
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

@account_blueprint.route('/accounts/account/transactions', methods=['GET'])
@login_required
def account_transactions():
    result = []
    transactions = db.engine.execute('select * from transaction_history({})'.format(current_user.id))
    for transaction in transactions:
        result.append(dict(transaction.items()))
    return jsonify(result)