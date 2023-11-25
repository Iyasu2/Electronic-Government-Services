from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from enum import Enum

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class PendingStatus(Enum):
    NOT_APPLIED = 'Not Applied'
    APPLIED_PENDING = 'Applied and Pending'
    APPLIED_ACCEPTED = 'Applied and Accepted'

class Common():
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(50))
    fatherName = db.Column(db.String(50))
    gfatherName = db.Column(db.String(50))
    birthDay = db.Column(db.Date)
    gender = db.Column(db.String(10))
    region = db.Column(db.String(50))
    photo = db.Column(db.String(100))
    pending = db.Column(db.Enum(PendingStatus), default=PendingStatus.NOT_APPLIED)

class Common2():
    id = db.Column(db.Integer, primary_key=True)
    subCity = db.Column(db.String(50))
    woreda = db.Column(db.String(50))
    houseNumber = db.Column(db.String(50))
    phoneNumber = db.Column(db.String(50))
    bloodType = db.Column(db.String(10))

class Driver_license_renewal(Common, Common2, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    expiryDate = db.Column(db.Date)
    grade = db.Column(db.String(20))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class National_id_new(Common, Common2, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ecName = db.Column(db.String(50))
    ecphoneNumber = db.Column(db.String(50))
    birthPhoto = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class National_id_renewal(Common, Common2, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ecName = db.Column(db.String(50))
    ecphoneNumber = db.Column(db.String(50))
    expiryDate = db.Column(db.Date)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Birth_certificate(Common, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fatherfullName = db.Column(db.String(50))
    motherfullName = db.Column(db.String(50))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))
    first_name = db.Column(db.String(50))
    notes = db.relationship('Note')

