from flask import Blueprint, render_template, request, flash

auth = Blueprint('auth', __name__)

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        firstName = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        if len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(firstName) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            #make sure password is strong
            flash('Password must be at least 7 characters.', category='error')
        else:
            flash('Account created!', category='success')


    return render_template("signup.html")

@auth.route('/login', methods=['GET', 'POST'])
def login():
    return render_template("login.html", text=True)

@auth.route('/logout')
def logout():
    return "<p>Logout</p>"