import datetime
import enum

from diplomaproject import app, db, bcrypt


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
    email = db.Column(db.Text, unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, server_default='f')
    login_attempts = db.Column(db.Integer, nullable=False, server_default=db.text('0'))
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
        return '<Account {0}>'.format(self.email)


class TransactionStatus(enum.Enum):
    created = 1
    completed = 2
    expired = 3

class TransactionType(enum.Enum):
    withdraw = 1
    deposit = 2
    payment = 3


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
    status = db.Column(db.Enum(TransactionStatus),
                       nullable=False, server_default='created')
    type = db.Column(db.Enum(TransactionType),
                       nullable=False, server_default='payment')
    creation_time = db.Column(
        db.DateTime, nullable=False, server_default=db.text('NOW()'))

    def __init__(self, seller, amount, description):
        self.seller = seller
        self.amount = amount
        self. description = description


transfer_func = db.DDL(
    "CREATE OR REPLACE FUNCTION transfer_money() "
    "RETURNS TRIGGER AS $$ "
    "BEGIN "
    "IF NEW.buyer_id IS NOT NULL THEN "
    "UPDATE accounts SET balance = balance - NEW.amount WHERE accounts.id = NEW.buyer_id; "
    "UPDATE accounts SET balance = balance + NEW.amount WHERE accounts.id = NEW.seller_id; "
    "NEW.status = 'completed'; "
    "END IF; "
    "RETURN NEW; "
    "END; $$ LANGUAGE PLPGSQL"
)

transfer_trig = db.DDL(
    "CREATE TRIGGER transfer_money_trigger BEFORE UPDATE ON transactions "
    "FOR EACH ROW EXECUTE PROCEDURE transfer_money();"
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
    "JOIN accounts a on t.seller_id = a.id "
    "WHERE t.buyer_id = account_id "
    "UNION ALL "
    "SELECT NULL AS debit, t.amount AS credit, t.description AS description, "
    "t.creation_time AS date, CONCAT(a.first_name, ' ', a.last_name) AS counterparty "
    "FROM transactions AS t "
    "JOIN accounts a on t.buyer_id = a.id "
    "WHERE t.seller_id = account_id; "
    "END; $$ LANGUAGE PLPGSQL"
)

db.event.listen(
    Transaction.__table__, 'after_create',
    transfer_func
)

db.event.listen(
    Transaction.__table__, 'after_create',
    transfer_trig
)

db.event.listen(
    Transaction.__table__, 'after_create',
    transfer_history
)

db.create_all()
