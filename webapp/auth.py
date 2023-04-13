from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
import mysql.connector

cnx = mysql.connector.connect(user='admin', database='ecom', password='Elviskhorem12!?', host='127.0.0.1')
cursor = cnx.cursor(buffered=True)
auth = Blueprint('auth', __name__)

@auth.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        query = "SELECT email, password FROM image_analysis.doctors WHERE email=%s"
        values = (email,)
        cursor.execute(query, values)
        user = cursor.fetchone()
        
        if user:
            if user[1] == password:
                flash('Logged in successfully.', category='success')
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

        email = request.form['email']
        firstname = request.form['firstName']
        lastname = request.form['lastName']
        address = request.form['address']
        dob = request.form['dob']
        password1 = request.form['password1']
        password2 = request.form['password2']
        if password1 == password2:
            add_product = ("INSERT INTO image_analysis.doctors "
                           "(first_name, last_name, address, dob, email, password) "
                           "VALUES (%s, %s, %s, %s, %s, %s)")

            cursor.execute(add_product, (email, firstname, lastname, address, dob, password1))
            cnx.commit()

        flash("Account created", category='success')
        return redirect(url_for('views.login'))
        
    return render_template("sign_up.html", user=current_user)

