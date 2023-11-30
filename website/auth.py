from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User, Admin_User
from . import db
from passlib.hash import sha256_crypt
from flask_login import login_user, login_required, logout_user, current_user

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
                flash('Incorrect password or email', category='error')
        else:
            flash('Email does not exist.', category='error')
    return render_template("login.html", user=current_user)

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