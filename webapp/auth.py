from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user


auth = Blueprint('auth', __name__)

@auth.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email = email).first()
        
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully.', category='success')
                login_user(user, remember=False)
                return  redirect(url_for('views.home'))
            else:
                flash('Password is incorrect, try again!', category='error')
        else:
            flash('User with that email does not exist!', category='error')

    return render_template("login.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('views.about'))

@auth.route('/signup', methods = ['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        fullname = request.form.get('fullName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists', category='error')
        elif len(email) < 4:
            flash('Email must be longer than 3 characters!', category='error')
        elif len(fullname) < 2:
            flash('Fullname must be longer than 1 characters!', category='error')
        elif password1 != password2:
            flash("Password doesn't match", category='error')
        elif len(password1) < 4:
            flash('Password must be longer than 3 characters!', category='error')
        else:
            # add user to database
            newuser = User(fullname=fullname, email=email, password=generate_password_hash(password1, method='sha256'))
            db.session.add(newuser)
            db.session.commit()
            login_user(newuser, remember=False)
            flash("Account created", category='success')
            return redirect(url_for('views.home'))
        
    return render_template("sign_up.html", user=current_user)

