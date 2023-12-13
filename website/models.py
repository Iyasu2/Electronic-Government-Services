from . import db
from flask import current_app
from flask_login import UserMixin
from sqlalchemy.sql import func
from enum import Enum
from itsdangerous import URLSafeTimedSerializer as Serializer, SignatureExpired
import uuid
import time

# Enum class for pending status
class PendingStatus(Enum):
    NOT_APPLIED = 'Not Applied'
    APPLIED_PENDING = 'Applied and Pending'
    APPLIED_AWAITING_VERIFICATION = 'Applied and awaiting physical verification'
    APPLIED_ACCEPTED = 'Applied and Accepted'
    APPLIED_REJECTED = 'Applied and Rejected'

class Common():
    # Common attributes for different models
    firstName = db.Column(db.String(50))  # First name column
    fatherName = db.Column(db.String(50))  # Father's name column
    gfatherName = db.Column(db.String(50))  # Grandfather's name column
    birthDay = db.Column(db.Date)  # Birth date column
    gender = db.Column(db.String(10))  # Gender column
    region = db.Column(db.String(50))  # Region column
    photo = db.Column(db.String(100))  # Photo column
    pending = db.Column(db.Enum(PendingStatus), default=PendingStatus.NOT_APPLIED)  # Pending status column with default value 'Not Applied'
    comment = db.Column(db.String(255), default='')  # Comment column with default value ''
    Date1 = db.Column(db.Date)  # Date1 column
    Date2 = db.Column(db.Date)  # Date2 column
    Date3 = db.Column(db.Date)  # Date3 column
    Date4 = db.Column(db.Date)  # Date4 column
    Date5 = db.Column(db.Date)  # Date5 column
    Time1 = db.Column(db.Time)  # Time1 column
    Time2 = db.Column(db.Time)  # Time2 column
    Time3 = db.Column(db.Time)  # Time3 column
    Time4 = db.Column(db.Time)  # Time4 column
    Time5 = db.Column(db.Time)  # Time5 column
    link = db.Column(db.String)  # Link column

class Common2():
    # Additional common attributes for different models
    subCity = db.Column(db.String(50))  # Subcity column
    woreda = db.Column(db.String(50))  # Woreda column
    houseNumber = db.Column(db.String(50))  # House number column
    phoneNumber = db.Column(db.String(50))  # Phone number column
    bloodType = db.Column(db.String(10))  # Blood type column

class Driver_license_renewal(Common, Common2, db.Model):
    # Model for driver license renewal
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))  # ID column with a default value generated using uuid4()
    expiryDate = db.Column(db.Date)  # Expiry date column
    grade = db.Column(db.String(20))  # Grade column
    user_id = db.Column(db.String, db.ForeignKey('user.id'))  # Foreign key column referencing the 'user' table

    __tablename__ = 'driver_license_renewal'  # Table name for the model

class National_id(Common, Common2, db.Model):
    # Model for national ID
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))  # ID column with a default value generated using uuid4()
    ecName = db.Column(db.String(50))  # EC name column
    ecphoneNumber = db.Column(db.String(50))  # EC phone number column
    expiryDate = db.Column(db.Date)  # Expiry date column
    user_id = db.Column(db.String, db.ForeignKey('user.id'))  # Foreign key column referencing the 'user' table

    __tablename__ = 'national_id'  # Table name for the model

class Birth_certificate(Common, db.Model):
    # Model for birth certificate
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))  # ID column with a default value generated using uuid4()
    fatherfullName = db.Column(db.String(50))  # Father's full name column
    motherfullName = db.Column(db.String(50))  # Mother's full name column
    user_id = db.Column(db.String, db.ForeignKey('user.id'))  # Foreign key column referencing the 'user' table

    __tablename__ = 'birth_certificate'  # Table name for the model

class User(db.Model, UserMixin):
    # User model
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))  # ID column with a default value generated using uuid4()
    email = db.Column(db.String(50), unique=True)  # Email column (unique)
    password = db.Column(db.String(50))  # Password column
    first_name = db.Column(db.String(50))  # First name column
    admin = db.Column(db.Boolean, default=False)  # Admin column (boolean with default value False)

    def get_token(self, expires_sec=300):
        # Method to generate a token with an expiration time
        serial = Serializer(current_app.config['SECRET_KEY'])  # Create a serializer object with the secret key from the current app's configuration
        return serial.dumps({'user_id': self.id, 'exp': time.time() + expires_sec})  # Serialize the data (user ID and expiration time) and return the token

    @staticmethod
    def verify_token(token):
        # Static method to verify a token
        serial = Serializer(current_app.config['SECRET_KEY'])  # Create a serializer object with the secret key from the current app's configuration
        try:
            data = serial.loads(token)  # Deserialize the token to extract the data
        except SignatureExpired:
            return None  # If the token is expired, return None
        if time.time() > data['exp']:
            return None  # If the current time is greater than the expiration time, return None
        return User.query.get(data['user_id'])  # Return the user object corresponding to the user ID in the token

class Admin_User(db.Model, UserMixin):
    # Admin user model
    id = db.Column(db.Integer, primary_key=True)  # ID column (integer)
    email = db.Column(db.String(50), unique=True)  # Email column (unique)
    password = db.Column(db.String(50))  # Password column
    first_name = db.Column(db.String(50))  # First name column
    admin = db.Column(db.Boolean, default=False)  # Admin column (boolean with default value False)
