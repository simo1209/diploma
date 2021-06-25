from flask import render_template, Blueprint, request, jsonify, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import exc

from backoffice import admin, bcrypt, db
from backoffice.models import Administrator
from backoffice.user.forms import LoginForm
from backoffice.errors import BadRequest, Unauthorized, Conflict


administrator_blueprint = Blueprint('administrator', __name__)


@administrator_blueprint.route('/', methods=['GET'])
@administrator_blueprint.route('/login', methods=['GET'])
def login_form():
    form = LoginForm(request.form)
    return render_template('login.html', title='Please Login', form=form)


@administrator_blueprint.route('/administrator', methods=['GET'])
@login_required
def account_view():
    administrator = Administrator.query.filter_by(id=current_user.id).first()
    return render_template('menu.html', administrator=administrator)

@administrator_blueprint.route('/administrators/login', methods=['POST'])
def login():
    form = LoginForm(request.form)

    if form.validate_on_submit():
        administrator = Administrator.query.filter_by(email=form.email.data).first()
        if administrator and not administrator.is_active():
            return Unauthorized('Account is locked. Contact an administrator')
        if administrator and administrator.is_active() and bcrypt.check_password_hash(
                administrator.password, request.form['password']):
            administrator.login_attempts = 0
            db.session.commit()
            login_user(administrator)
            return render_template('menu.html', administrator=administrator), 200
        elif administrator:
            administrator.login_attempts+=1
            db.session.commit()            
    raise Unauthorized('Wrong username or password')

@administrator_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('administrator.login_form'))

