'''
This module defines the authentication routes and functions for the Flask application.
'''

from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User, Admin_User
from . import db, mail
from . import create_app as app
from passlib.hash import sha256_crypt
from flask_login import login_user, login_required, logout_user, current_user
from flask_mail import Message

auth = Blueprint('auth', __name__)

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    '''
    This route handles the user signup process.
    '''
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()

        if user:
            flash('Email already exists.', category='error')
            return redirect(url_for('auth.signup'))

        if len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
            return redirect(url_for('auth.signup'))
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
            return redirect(url_for('auth.signup'))
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
            return redirect(url_for('auth.signup'))
        elif len(password1) < 7:
            # Make sure password is strong
            flash('Password must be at least 7 characters.', category='error')
            return redirect(url_for('auth.signup'))
        else:
            new_user = User(email=email, first_name=first_name, password=sha256_crypt.hash(password1))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("signup.html", user=current_user)

@auth.route('/admin/signup', methods=['GET', 'POST'])
def signup_admin():
    '''
    This route handles the admin user signup process.
    '''
    admin_user = Admin_User.query.first()

    if admin_user:
        flash('This is an admin page.', category='error')
        return redirect(url_for('auth.signup'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        if len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
            return redirect(url_for('auth.signup_admin'))
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
            return redirect(url_for('auth.signup_admin'))
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
            return redirect(url_for('auth.signup_admin'))
        elif len(password1) < 7:
            # Make sure password is strong
            flash('Password must be at least 7 characters.', category='error')
            return redirect(url_for('auth.signup_admin'))
        else:
            new_user = Admin_User(email=email, first_name=first_name, password=sha256_crypt.hash(password1), admin=True)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Admin Account created!', category='success')
            return redirect(url_for('views.home_admin'))

    return render_template("signup_admin.html", user=current_user)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    '''
    This route handles the user login process.
    '''
    if current_user.is_authenticated:
        flash('You are already signed in!', category='error')
        return redirect(url_for('views.home'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if sha256_crypt.verify(password, user.password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password', category='error')
        else:
            flash('Email does not exist.', category='error')
    return render_template("login.html", user=current_user)

def send_email(user):
    '''
    This function sends a password reset email to the user.
    '''
    token = user.get_token()
    msg = Message('Password Reset Request', recipients=[user.email], sender='noreply@egov.com')
    msg.body = f''' Toreset your password, visit the following link:
{url_for('auth.reset_password', token=token, _external=True)}

If you did not make this request, simply ignore this email and no changes will be made.
'''
    mail.send(msg)

@auth.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    '''
    This route handles the forgot password process.
    '''
    if current_user.is_authenticated:
        flash('You are already signed in!', category='error')
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            send_email(user)
            flash('An email has been sent with instructions to reset your password.', category='success')
            return redirect(url_for('auth.login'))
        else:
            flash('Email does not exist.', category='error')

    return render_template("forgot_password.html", user=current_user)

@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    '''
    This route handles the password reset process.
    '''
    if current_user.is_authenticated:
        flash('You are already signed in!', category='error')
        return redirect(url_for('views.home'))

    user = User.verify_token(token)
    if not user:
        flash('That is an invalid or expired token.', category='error')
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        if password1 != password2:
            flash('Passwords don\'t match.', category='error')
            return redirect(url_for('auth.reset_password', token=token))
        elif len(password1) < 7:
            # Make sure password is strong
            flash('Password must be at least 7 characters.', category='error')
            return redirect(url_for('auth.reset_password', token=token))
        else:
            user.password = sha256_crypt.hash(password1)
            db.session.commit()
            flash('Your password has been reset! You are now able to log in.', category='success')
            return redirect(url_for('auth.login'))

    return render_template("reset_password.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    '''
    This route handles the user logout process.
    '''
    logout_user()
    return redirect(url_for('views.home'))
