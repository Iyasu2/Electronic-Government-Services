from . import db
from flask import current_app
from flask_login import UserMixin
from sqlalchemy.sql import func
from enum import Enum
from itsdangerous import URLSafeTimedSerializer as Serializer, SignatureExpired
import uuid
import time

class PendingStatus(Enum):
    NOT_APPLIED = 'Not Applied'
    APPLIED_PENDING = 'Applied and Pending'
    APPLIED_AWAITING_VERIFICATION = 'Applied and awaiting physical verification'
    APPLIED_ACCEPTED = 'Applied and Accepted'
    APPLIED_REJECTED = 'Applied and Rejected'

class Common():
    firstName = db.Column(db.String(50))
    fatherName = db.Column(db.String(50))
    gfatherName = db.Column(db.String(50))
    birthDay = db.Column(db.Date)
    gender = db.Column(db.String(10))
    region = db.Column(db.String(50))
    photo = db.Column(db.String(255))
    pending = db.Column(db.Enum(PendingStatus), default=PendingStatus.NOT_APPLIED)
    comment = db.Column(db.String(255), default='')
    Date1 = db.Column(db.Date)
    Date2 = db.Column(db.Date)
    Date3 = db.Column(db.Date)
    Date4 = db.Column(db.Date)
    Date5 = db.Column(db.Date)
    Time1 = db.Column(db.Time)
    Time2 = db.Column(db.Time)
    Time3 = db.Column(db.Time)
    Time4 = db.Column(db.Time)
    Time5 = db.Column(db.Time)
    link = db.Column(db.String)

class Common2():
    subCity = db.Column(db.String(50))
    woreda = db.Column(db.String(50))
    houseNumber = db.Column(db.String(50))
    phoneNumber = db.Column(db.String(50))
    bloodType = db.Column(db.String(10))

class Driver_license_renewal(Common, Common2, db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    expiryDate = db.Column(db.Date)
    grade = db.Column(db.String(20))
    user_id = db.Column(db.String, db.ForeignKey('user.id'))

    __tablename__ = 'driver_license_renewal'

class National_id(Common, Common2, db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ecName = db.Column(db.String(50))
    ecphoneNumber = db.Column(db.String(50))
    user_id = db.Column(db.String, db.ForeignKey('user.id'))

    __tablename__ = 'national_id'

class Birth_certificate(Common, db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    fatherfullName = db.Column(db.String(50))
    motherfullName = db.Column(db.String(50))
    user_id = db.Column(db.String, db.ForeignKey('user.id'))

    __tablename__ = 'birth_certificate'

class User(db.Model, UserMixin):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(100))
    first_name = db.Column(db.String(50))
    verified = db.Column(db.Boolean, default=False)
    admin = db.Column(db.Boolean, default=False)
    

    def get_token(self, expires_sec=300):
        serial = Serializer(current_app.config['SECRET_KEY'])
        return serial.dumps({'user_id':self.id, 'exp': time.time() + expires_sec})
    
    @staticmethod
    def verify_token(token):
        serial = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = serial.loads(token)
        except SignatureExpired:
            return None
        if time.time() > data['exp']:
            return None
        return User.query.get(data['user_id'])

class Admin_User(db.Model, UserMixin):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(100))
    first_name = db.Column(db.String(50))
    admin = db.Column(db.Boolean, default=False)