import dbus
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_user, login_required, logout_user, current_user
import jwt

from . import db
from .models import User, UserSchema
from werkzeug.security import generate_password_hash, check_password_hash

import datetime


auth = Blueprint('auth', __name__)


@auth.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        print(request.data)
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Invalid credentials', category='error')
        else:
            flash('Email doesn\'t exist', category='error')

    return render_template("login.html", user=current_user)


@auth.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/loginapi/', methods=['POST'])
def login_api():
    if request.method == 'POST':
        print(request.get_json())
        data = request.get_json()
        email = data['email']
        password = data['password']

        response_message = {
            "status": 0,
            "message": "",
            "payload": ""
        }

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                token = jwt.encode({
                    'id': user.id,
                    'email': user.email,
                    'name': user.name,
                    'role': user.role,
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60)
                }, 'supersecretkeysupersecretkeysupersecretkey')
                response_message['status'] = 0
                response_message['message'] = 'Login Successful'
                response_message['token'] = token.decode('UTF-8')
            else:
                response_message['status'] = 1
                response_message['message'] = 'Invalid Credentials'
        else:
            response_message['status'] = 1
            response_message['message'] = 'Invalid Credentials'

    return jsonify(response_message)


@auth.route("/signup/", methods=['POST'])
def signup():
    print("signup")
    print(request.get_json())

    response_message = {
        "status": 0,
        "message": "",
        "payload": {}
    }

    if request.method == 'POST':
        data = request.get_json()
        name = data['name']
        email = data['email']
        office = data['office']
        phone = data['phone']
        password = data['password']
        confirm = data['confirm']

        user = User.query.filter_by(email=email).first()
        if user:
            response_message['status'] = 1
            response_message['message'] = 'Email already exists'
        else:
            if email.find('@') < 0:
                response_message['status'] = 1
                response_message['message'] = 'Email is not valid'

            elif len(office) < 2:
                response_message['status'] = 1
                response_message['message'] = 'Office must be greater than 1 character'

            elif password != confirm:
                flash('Passwords don\'t match', category='error')
                response_message['status'] = 1
                response_message['message'] = 'Passwords don\'t match'

            else:
                # Add user to db
                new_user = User(
                    email=email,
                    name=name,
                    phone=phone,
                    office=office,
                    role='USER',
                    password=generate_password_hash(password, method='sha256')
                )
                db.session.add(new_user)
                db.session.commit()

                response_message['status'] = 0
                response_message['message'] = 'User created successfully'

    print(response_message)
    return jsonify(response_message)


@auth.route("/sign-up/", methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        print(request.form)
        email = request.form.get('email')
        office = request.form.get('office')
        password = request.form.get('password1')
        confirm_password = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email exists', category='error')
        else:
            if email.find('@') < 0:
                flash('Email is not valid', category='error')
                pass
            elif len(office) < 2:
                flash('Office must be greater than 1 character', category='error')
                pass
            elif password != confirm_password:
                flash('Passwords don\'t match', category='error')
                pass
            else:
                # Add user to db
                new_user = User(
                    email=email,
                    office=office,
                    role='USER',
                    password=generate_password_hash(password, method='sha256')
                )
                db.session.add(new_user)
                db.session.commit()
                flash('User created successfully', category='success')
                login_user(new_user, remember=True)
                return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)


@auth.route('/created_by/<user_id>', methods=['GET'])
def created_by(user_id):
    print(user_id)
    user_query = User.query.filter_by(id=user_id).first()
    user_schema = UserSchema()
    user = user_schema.dump(user_query)
    return user
