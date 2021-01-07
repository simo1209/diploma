from flask import render_template, Blueprint, request
from flask_login import login_user, logout_user, login_required

from diplomaproject import bcrypt, db
from diplomaproject.models import UserAccount
from diplomaproject.user.forms import LoginForm, RegisterForm


user_blueprint = Blueprint('user', __name__)


@user_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    print(request.form)
    print(type(request.form))
    form = RegisterForm(request.form    )

    if form.validate_on_submit():
        user_account = UserAccount(
            email=form.email.data,
            password=form.password.data,
            phone=form.phone.data,
            UCN=form.UCN.data,
            country=form.country.data,
            city=form.city.data,
            addr_1=form.address1.data,
            addr_2=form.address2.data,
            postal_code=form.postal_code.data
        )

        db.session.add(user)
        db.session.commit()

        login_user(user)

        return "Successfully Registered", 201
    return render_template('register.html', form=form)

@user_blueprint.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm(request.form)
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(
                user.password, request.form['password']):
            login_user(user)
            return "Authenticated", 200
        else:
            return render_template('user/login.html', form=form)
    return render_template('user/login.html', title='Please Login', form=form)
