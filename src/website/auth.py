import dbus
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_user, login_required, logout_user, current_user
import jwt

from . import db
from .models import User, UserSchema
from werkzeug.security import generate_password_hash, check_password_hash

import datetime


auth = Blueprint('auth', __name__)


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

    user_role = 'USER'

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

        user_exists_query = User.query.all()
        if not user_exists_query:
            print("No user exists")
            user_role = 'ADMIN'
            office = 'ADMIN'
        else:
            print("No office exists")
            office_exists_query = User.query.filter_by(office=office).first()
            if not office_exists_query:
                user_role = 'SECRETARY'

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
                    role=user_role,
                    password=generate_password_hash(password, method='sha256')
                )
                db.session.add(new_user)
                db.session.commit()

                response_message['status'] = 0
                response_message['message'] = 'User created successfully'

    print(response_message)
    return jsonify(response_message)
