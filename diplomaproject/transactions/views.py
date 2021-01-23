from flask import render_template, url_for, redirect, Blueprint, request, jsonify, send_from_directory
from flask_login import current_user, login_required
from cryptography.fernet import Fernet
from qrcode import make as qrc

from diplomaproject import app, db
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

        ba = bytearray('QRPayment:'.encode())  # Distinct QR codes
        secret_id = fernet.encrypt((transaction.id).to_bytes(
            (transaction.id).bit_length()//8 + 1, 'big'))
        ba.extend(secret_id)

        print(ba.decode())
        img = qrc(ba.decode())
        img.save('{}/{}.png'.format(app.config['QR_CODES'], transaction.id))

        return redirect(url_for('transaction.qrcode', id=secret_id))
    return render_template('create_transaction.html', form=form)


@transaction_blueprint.route('/qrcode/<id>')
def qrcode(id):
    image = int.from_bytes(fernet.decrypt(id.encode()), 'big')
    return send_from_directory(app.config['QR_CODES'], '{}.png'.format(image))


@transaction_blueprint.route('/<id>')
def transaction_details(id):
    
    transaction_id = int.from_bytes(fernet.decrypt(id.encode()), 'big')

    return jsonify(
        Transaction.query
        .filter_by(id=transaction_id)
        .with_entities(
            Transaction.amount,
            Transaction.description
        ).first()._asdict()
    )
