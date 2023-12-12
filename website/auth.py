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
            #make sure password is strong
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
            #make sure password is strong
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
    token = user.get_token()
    msg = Message('Password Reset Request', recipients=[user.email], sender='noreply@egov.com')
    msg.body = f''' To reset your password, Please follow the link below.

    {url_for('auth.reset_token', token=token, _external=True)}
If you didn't send a password reset request, Please ignore this message.

'''
    mail.send(msg)


@auth.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form.get('email')

        user = User.query.filter_by(email=email).first()
        if user:
            send_email(user) 
            flash('Reset request sent. Check your email.', category='success')

    return render_template("reset_request.html", user=current_user)

@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    user = User.verify_token(token)
    if user is None:
        flash('That is an invalid or expired token!', category='error')
        return redirect(url_for('reset_password'))

    if request.method == 'POST':
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        if password1 != password2:
            flash('Passwords don\'t match.', category='error')
            return redirect(url_for('auth.reset_token'))
        elif len(password1) < 7:
            #make sure password is strong
            flash('Password must be at least 7 characters.', category='error')
            return redirect(url_for('auth.reset_token'))
        else:
            user.password = sha256_crypt.hash(password1)
            db.session.commit()
            flash('Password changed!', category='success')
            return redirect(url_for('auth.login'))
        
    return render_template("change_password.html", user=current_user)

 
@auth.route('/admin/login', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        Admin_user = Admin_User.query.filter_by(email=email).first()
        if Admin_user:
            if sha256_crypt.verify(password, Admin_user.password):
                flash('Logged in successfully!', category='success')
                login_user(Admin_user, remember=True)
                return redirect(url_for('views.home_admin'))
            else:
                flash('Incorrect password or email', category='error')
        else:
            flash('Email does not exist.', category='error')
    return render_template("login_admin.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login') )