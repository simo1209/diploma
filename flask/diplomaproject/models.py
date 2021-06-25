import datetime
import enum

from diplomaproject import app, db, bcrypt


class Company(db.Model):

    __tablename__ = 'companies'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.Text, unique=True, nullable=False)
    accounts = db.relationship('Account', backref='companies', lazy=True)

class Category(db.Model):

    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, unique=False, nullable=False)

    creator_account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'),
        nullable=False)

class Address(db.Model):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
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
        return '<Address {0}>'.format(self.address_1)


class Account(db.Model):

    __tablename__ = 'accounts'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, unique=False, nullable=False)
    password = db.Column(db.Text, nullable=False)
    login_attempts = db.Column(
        db.Integer, nullable=False, server_default=db.text('0'))
    registered_on = db.Column(
        db.DateTime, nullable=False, server_default=db.text('NOW()'))
    phone = db.Column(db.String(10), nullable=False)
    address_id = db.Column(db.Integer, db.ForeignKey('address.id'),
                           nullable=False)
    address = db.relationship('Address',
                              backref=db.backref('accounts', lazy=True))

    UCN = db.Column(db.String(10), nullable=False)
    balance = db.Column(db.Numeric, db.CheckConstraint(
        'balance>=0'), nullable=False, server_default=db.text('0'))

    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'),
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
        return '{0} {1}'.format(self.first_name, self.last_name)


class TransactionStatus(db.Model):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
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

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
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

class Transaction(db.Model):

    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    seller_id = db.Column(db.Integer, db.ForeignKey(
        'accounts.id'), nullable=True)
    seller = db.relationship(
        'Account', foreign_keys=[seller_id])
    buyer_id = db.Column(db.Integer,  db.CheckConstraint('buyer_id!=seller_id'), db.ForeignKey(
        'accounts.id'), nullable=True)
    buyer = db.relationship(
        'Account', foreign_keys=[buyer_id])
    amount = db.Column(db.Numeric, db.CheckConstraint(
        'amount>0'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    transaction_status_id = db.Column(db.Integer, db.ForeignKey('transaction_status.id'),
                                      nullable=False)
    transaction_status = db.relationship('TransactionStatus',
                                         backref=db.backref('transaction_status', lazy=True))

    transaction_type_id = db.Column(db.Integer, db.ForeignKey('transaction_type.id'),
                                    nullable=False)
    transaction_type = db.relationship('TransactionType',
                                       backref=db.backref('transaction_type', lazy=True))

    creation_time = db.Column(
        db.DateTime, nullable=False, server_default=db.text('NOW()'))
    status_update_time = db.Column(
        db.DateTime, nullable=True)

    categoriess = db.relationship('Category', secondary=transactions_categories, lazy='subquery',
        backref=db.backref('transactions', lazy=True))

    def __init__(self, seller, amount, description, status, type):
        self.seller = seller
        self.amount = amount
        self.description = description
        self.transaction_status = status
        self.transaction_type = type


payment_func = db.DDL(
    "CREATE OR REPLACE FUNCTION execute_payment() "
    "RETURNS TRIGGER AS $$ "
    "BEGIN "
    "IF NEW.buyer_id IS NOT NULL AND NEW.transaction_status_id = (SELECT id from transaction_status WHERE status = 'created') THEN "
    "UPDATE accounts SET balance = balance - NEW.amount WHERE accounts.id = NEW.buyer_id; "
    "UPDATE accounts SET balance = balance + NEW.amount WHERE accounts.id = NEW.seller_id; "
    "NEW.transaction_status_id = (SELECT id from transaction_status WHERE status = 'completed'); "
    "NEW.status_update_time = NOW();"
    "END IF; "
    "RETURN NEW; "
    "END; $$ LANGUAGE PLPGSQL "
)

payment_trig = db.DDL(
    "CREATE TRIGGER execute_payment_trigger BEFORE UPDATE ON transactions "
    "FOR EACH ROW EXECUTE PROCEDURE execute_payment();"
)

admin_func = db.DDL(
    "CREATE OR REPLACE FUNCTION administrative_transaction() "
    "RETURNS TRIGGER AS $$ "
    "BEGIN "
    "IF NEW.transaction_type_id = (SELECT id FROM transaction_type WHERE type = 'deposit') THEN "
    "UPDATE accounts SET balance = balance + NEW.amount WHERE accounts.id = NEW.buyer_id; "
    "NEW.transaction_status_id = (SELECT id from transaction_status WHERE status = 'completed'); "
    "NEW.status_update_time = NOW();"
    "ELSEIF NEW.transaction_type_id = (SELECT id FROM transaction_type WHERE type = 'withdraw') THEN "
    "UPDATE accounts SET balance = balance - NEW.amount WHERE accounts.id = NEW.buyer_id; "
    "NEW.transaction_status_id = (SELECT id from transaction_status WHERE status = 'completed'); "
    "NEW.status_update_time = NOW();"
    "END IF; "
    "RETURN NEW; "
    "END; $$ LANGUAGE PLPGSQL "
)

admin_trig = db.DDL(
    "CREATE TRIGGER administrative_transaction_trigger BEFORE INSERT ON transactions "
    "FOR EACH ROW EXECUTE PROCEDURE administrative_transaction();"
)

transfer_history = db.DDL(
    "CREATE OR REPLACE FUNCTION transaction_history ( account_id integer ) "
    "RETURNS TABLE ( "
    "debit NUMERIC, "
    "credit NUMERIC, "
    "description TEXT, "
    "date TIMESTAMP, "
    "counterparty TEXT "
    ") "
    "AS $$ "
    "BEGIN "
    "RETURN QUERY "
    "SELECT t.amount AS debit, NULL AS credit, t.description AS description, "
    "t.creation_time AS date, CONCAT(a.first_name, ' ', a.last_name) AS counterparty "
    "FROM transactions AS t "
    "LEFT JOIN accounts a on t.seller_id = a.id "
    "WHERE t.buyer_id = account_id "
    "UNION ALL "
    "SELECT NULL AS debit, t.amount AS credit, t.description AS description, "
    "t.creation_time AS date, CONCAT(a.first_name, ' ', a.last_name) AS counterparty "
    "FROM transactions AS t "
    "LEFT JOIN accounts a on t.buyer_id = a.id "
    "WHERE t.seller_id = account_id; "
    "END; $$ LANGUAGE PLPGSQL"
)

db.event.listen(
    Transaction.__table__, 'after_create',
    payment_func
)

db.event.listen(
    Transaction.__table__, 'after_create',
    payment_trig
)

db.event.listen(
    Transaction.__table__, 'after_create',
    admin_func
)

db.event.listen(
    Transaction.__table__, 'after_create',
    admin_trig
)

db.event.listen(
    Transaction.__table__, 'after_create',
    transfer_history
)

db.create_all()
