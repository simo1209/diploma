import datetime

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


class UserAccount(db.Model):

    __tablename__ = 'user_accounts'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)
    phone = db.Column(db.String(10), nullable=False)
    address_id = db.Column(db.Integer, db.ForeignKey('address.id'),
                           nullable=False)
    address = db.relationship('Address',
                              backref=db.backref('user_accounts', lazy=True))

    UCN = db.Column(db.String(10), nullable=False)

    def __init__(self, first_name, last_name,  email, password, phone, address, UCN):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = bcrypt.generate_password_hash(
            password, app.config.get('BCRYPT_LOG_ROUNDS')
        ).decode('utf-8')
        self.registered_on = datetime.datetime.now()
        self.phone = phone
        self.address = address
        self.UCN = UCN

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def __repr__(self):
        return '<UserAccount {0}>'.format(self.email)


db.create_all()
