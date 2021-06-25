from flask import render_template, url_for, redirect, Blueprint, request, jsonify, send_from_directory
from flask_login import current_user, login_required
from cryptography.fernet import Fernet, InvalidToken
from qrcode import make as qrc
from sqlalchemy import exc

from diplomaproject import app, db
from diplomaproject.models import Transaction
from diplomaproject.models import TransactionStatus, TransactionType
from diplomaproject.models import Account
from diplomaproject.transactions.forms import TransactionForm
from diplomaproject.errors import BadRequest


key_file = open('secret.key', 'rb')
key = key_file.read()
fernet = Fernet(key)

transaction_blueprint = Blueprint(
    'transaction', __name__, url_prefix='/transactions')


@transaction_blueprint.route('/create', methods=['GET', 'POST'])
@login_required
def create_transaction():

    form = TransactionForm(request.form)

    if request.method == 'GET':
        return render_template('create_transaction.html', form=form)

    if form.validate_on_submit():

        transaction = Transaction(
            Account.query.filter_by(id=current_user.id).first(),
            float(form.amount.data),
            form.description.data,
            TransactionStatus.query.filter_by(status='created').first(),
            TransactionType.query.filter_by(type='payment').first()
        )

        db.session.add(transaction)
        try:
            db.session.commit()
        except exc.IntegrityError:
            db.session.rollback()
            raise BadRequest('Invalid Transaction Amount')

        ba = bytearray('QRPayment:'.encode())  # Distinct QR codes
        secret_id = fernet.encrypt((transaction.id).to_bytes(
            (transaction.id).bit_length()//8 + 1, 'big'))
        ba.extend(secret_id)

        img = qrc(ba.decode())
        img.save('{}/{}.png'.format(app.config['QR_CODES'], transaction.id))

        return redirect(url_for('transaction.qrcode', id=secret_id))
    else:
        raise BadRequest('Invalid form data')


@transaction_blueprint.route('/qrcode/<id>')
def qrcode(id):
    try:
        image = int.from_bytes(fernet.decrypt(id.encode()), 'big')
    except InvalidToken:
        raise BadRequest('Supply valid id')
    return send_from_directory(app.config['QR_CODES'], '{}.png'.format(image))


@transaction_blueprint.route('/<id>')
def transaction_details(id):
    
    try:
        transaction_id = int.from_bytes(fernet.decrypt(id.encode()), 'big')
    except InvalidToken:
        raise BadRequest('Supply valid id')

    return jsonify(
        Transaction.query
        .filter_by(id=transaction_id)
        .with_entities(
            Transaction.amount,
            Transaction.description
        ).first()._asdict()
    )

@transaction_blueprint.route('/accept', methods=['POST'])
@login_required
def accept():
    payload = request.get_json()
    if not payload:
        raise BadRequest('Invalid Payload')
    id = payload['id']
    if not id:
        raise BadRequest('Supply valid id')
    
    try:
        transaction_id = int.from_bytes(fernet.decrypt(id.encode()), 'big')
    except InvalidToken:
        raise BadRequest('Supply valid id')

    transaction = Transaction.query.filter_by(id=transaction_id).first()
    
    if transaction.transaction_status == TransactionStatus.query.filter_by(status='created').first():
        transaction.buyer = current_user
        try:
            db.session.commit()
        except exc.IntegrityError:
            db.session.rollback()
            raise BadRequest('Transaction Error. Check your balance.')
        return 'Transaction Complete', 200
    else:
        raise BadRequest('Transaction Invalid')