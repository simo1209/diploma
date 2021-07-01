import datetime
import enum

from diplomaproject import app, db, bcrypt


class Company(db.Model):

    __tablename__ = 'companies'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    email = db.Column(db.Text, unique=True, nullable=False)
    accounts = db.relationship('Account', backref='companies', lazy=True)

class Category(db.Model):

    __tablename__ = 'categories'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, unique=False, nullable=False)

    creator_account_id = db.Column(db.BigInteger, db.ForeignKey('accounts.id'),
        nullable=False)

class Address(db.Model):

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    address_1 = db.Column(db.Text, nullable=False)
    address_2 = db.Column(db.Text)
    city = db.Column(db.Text, nullable=False)
    country = db.Column(db.Text, nullable=False)

    def __init__(self, addr_1, addr_2, city, country, postal_code):
        self.address_1 = addr_1
        self.address_2 = addr_2
        self.city = city
        self.country = country
        self.postal_code = postal_code

    def __repr__(self):
        return '<Address {0}, {1}, {2}>'.format(self.country, self.city, self.address_1)


class Account(db.Model):

    __tablename__ = 'accounts'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    login_attempts = db.Column(
        db.BigInteger, nullable=False, server_default=db.text('0'))
    registered_on = db.Column(
        db.DateTime, nullable=False, server_default=db.text('NOW()'))
    phone = db.Column(db.Text, nullable=False)
    address_id = db.Column(db.BigInteger, db.ForeignKey('address.id'),
                           nullable=False)
    address = db.relationship('Address',
                              backref=db.backref('accounts', lazy=True))

    UCN = db.Column(db.Text, nullable=False)
    balance = db.Column(db.Numeric, db.CheckConstraint(
        'balance>=0'), nullable=False, server_default=db.text('0'))

    company_id = db.Column(db.BigInteger, db.ForeignKey('companies.id'),
        nullable=True)

    categories = db.relationship('Category', backref='categories', lazy=True)


    def __init__(self, first_name, last_name,  email, password, phone, address, UCN):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = bcrypt.generate_password_hash(
            password, app.config.get('BCRYPT_LOG_ROUNDS')
        ).decode('utf-8')
        self.phone = phone
        self.address = address
        self.UCN = UCN

    def is_authenticated(self):
        return True

    def is_active(self):
        return self.login_attempts < 10

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def __repr__(self):
        return '{0} {1} {2}'.format(self.first_name, self.last_name, self.email)


class TransactionStatus(db.Model):

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    status = db.Column(db.Text, nullable=False, unique=True)

    def __init__(self, status):
        self.status = status

    def __repr__(self):
        return '<Status {0}>'.format(self.status)

# created_status = TransactionStatus(status='created')
# completed_status = TransactionStatus(status='completed')
# exipired_status = TransactionStatus(status='exipired')

# db.session.add(created_status)
# db.session.add(completed_status)
# db.session.add(exipired_status)
# db.session.commit()


class TransactionType(db.Model):

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    type = db.Column(db.Text, nullable=False, unique=True)

    def __init__(self, type):
        self.type = type

    def __repr__(self):
        return '<Type {0}>'.format(self.type)


# withdraw_type = TransactionType(type='withdraw')
# deposit_type = TransactionType(type='deposit')
# payment_type = TransactionType(type='payment')

# db.session.add(withdraw_type)
# db.session.add(deposit_type)
# db.session.add(payment_type)
# db.session.commit()

transactions_categories = db.Table('transactions_categories',
    db.Column('transaction_id', db.Integer, db.ForeignKey('transactions.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('categories.id'), primary_key=True)
)

transactions_categories = db.Table('transactions_categories',
    db.Column('transaction_id', db.BigInteger, db.ForeignKey('transactions.id'), primary_key=True),
    db.Column('category_id', db.BigInteger, db.ForeignKey('categories.id'), primary_key=True)
)

class Transaction(db.Model):

    __tablename__ = 'transactions'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    seller_id = db.Column(db.BigInteger, db.ForeignKey(
        'accounts.id'), nullable=True)
    seller = db.relationship(
        'Account', foreign_keys=[seller_id])
    buyer_id = db.Column(db.BigInteger,  db.CheckConstraint('buyer_id!=seller_id'), db.ForeignKey(
        'accounts.id'), nullable=True)
    buyer = db.relationship(
        'Account', foreign_keys=[buyer_id])
    amount = db.Column(db.Numeric, db.CheckConstraint(
        'amount>0'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    transaction_status_id = db.Column(db.BigInteger, db.ForeignKey('transaction_status.id'),
                                      nullable=True)
    transaction_status = db.relationship('TransactionStatus',
                                         backref=db.backref('transaction_status', lazy=True))

    transaction_type_id = db.Column(db.BigInteger, db.ForeignKey('transaction_type.id'),
                                    nullable=True)
    transaction_type = db.relationship('TransactionType',
                                       backref=db.backref('transaction_type', lazy=True))

    creation_time = db.Column(
        db.DateTime, nullable=False, server_default=db.text('NOW()'))
    status_update_time = db.Column(
        db.DateTime, nullable=True)

    categories = db.relationship('Category', secondary=transactions_categories, lazy='subquery',
        backref=db.backref('transactions', lazy=True))

    def __init__(self, seller, amount, description, t_status, t_type):
        self.seller = seller
        self.amount = amount
        self.description = description
        self.transaction_status = t_status
        self.transaction_type = t_type


db.create_all()
