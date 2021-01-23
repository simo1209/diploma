from flask import render_template, Blueprint, request, jsonify
from flask_login import current_user, login_required
from cryptography.fernet import Fernet
import qrcode

from diplomaproject import db
from diplomaproject.models import Transaction
from diplomaproject.models import Account
from diplomaproject.transactions.forms import TransactionForm

key_file = open('secret.key', 'rb')
key = key_file.read()
fernet = Fernet(key)

transaction_blueprint = Blueprint(
    'transaction', __name__, url_prefix='/transactions')


@transaction_blueprint.route('/create', methods=['GET', 'POST'])
@login_required
def create_transaction():
    form = TransactionForm(request.form)

    if form.validate_on_submit():

        transaction = Transaction(
            current_user,
            float(form.amount.data),
            form.description.data
        )

        db.session.add(transaction)
        db.session.commit()

        ba = bytearray('QRPayment:'.encode()) # Distinct QR codes
        secret_id = fernet.encrypt(bytes([transaction.id]))
        ba.extend(secret_id)

        img = qrcode.make(ba.decode())
        img.save('qr-codes/{}.png'.format(transaction.id))

        return "Transactions Created", 201
    return render_template('create_transaction.html', form=form)
