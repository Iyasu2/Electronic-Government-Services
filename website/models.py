from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from enum import Enum
import uuid

class PendingStatus(Enum):
    NOT_APPLIED = 'Not Applied'
    APPLIED_PENDING = 'Applied and Pending'
    APPLIED_ACCEPTED = 'Applied and Accepted'
    APPLIED_REJECTED = 'Applied and Rejected'

class Common():
    firstName = db.Column(db.String(50))
    fatherName = db.Column(db.String(50))
    gfatherName = db.Column(db.String(50))
    birthDay = db.Column(db.Date)
    gender = db.Column(db.String(10))
    region = db.Column(db.String(50))
    photo = db.Column(db.String(100))
    pending = db.Column(db.Enum(PendingStatus), default=PendingStatus.NOT_APPLIED)
    comment = db.Column(db.String(255), default='')

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
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    __tablename__ = 'driver_license_renewal'

class National_id(Common, Common2, db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ecName = db.Column(db.String(50))
    ecphoneNumber = db.Column(db.String(50))
    expiryDate = db.Column(db.Date)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    __tablename__ = 'national_id'

class Birth_certificate(Common, db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    fatherfullName = db.Column(db.String(50))
    motherfullName = db.Column(db.String(50))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    __tablename__ = 'birth_certificate'

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))
    first_name = db.Column(db.String(50))
    admin = db.Column(db.Boolean, default=False)

class Admin_User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))
    first_name = db.Column(db.String(50))
    admin = db.Column(db.Boolean, default=False)