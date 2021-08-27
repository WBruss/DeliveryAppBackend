import json

from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from sqlalchemy import desc
from functools import wraps
import jwt

from . import db
from .models import Delivery, User, Status, DeliverySchema, UserSchema

views = Blueprint('views', __name__)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            token = request.headers['Authorization']

        if not token:
            return jsonify({"message": "Token is missing"}), 401

        try:
            data = jwt.decode(token, "supersecretkeysupersecretkeysupersecretkey")
            logged_in_user = User.query.filter_by(id=data['id']).first()
        except:
            return jsonify({"message": "Token is invalid"}), 401

        return f(logged_in_user, *args, **kwargs)

    return decorated


@views.route('/mydeliveryrequests/', methods=['GET'])
@token_required
def my_delivery_requests(logged_in_user):
    if request.method == 'GET':
        print("logged_in_user: ", logged_in_user.id)
        print("logged_in_user: ", logged_in_user.name)

        delivery_requests = Delivery.query.filter_by(senderId=logged_in_user.id).order_by(desc(Delivery.date))
        delivery_schema = DeliverySchema(many=True)
        my_requests = delivery_schema.dump(delivery_requests)

        print("my_requests: ", my_requests)
        return jsonify({
            'status': 0,
            'message': 'success',
            'payload': my_requests,
        })
    else:
        return jsonify({"message": "Token is invalid"}), 405


@views.route('/deliveriestooffice/', methods=['GET'])
@token_required
def delivery_to_office(logged_in_user):
    if request.method == 'GET':
        print("logged_in_user: ", logged_in_user.office)
        print("logged_in_user: ", logged_in_user.name)
        print("logged_in_user: ", logged_in_user.role)

        # Get office
        secretary_query = User.query.filter_by(email=logged_in_user.email).first()
        user_schema = UserSchema()
        secretary = user_schema.dump(secretary_query)

        print("secretary_query: ", secretary_query)
        print("secretary: ", secretary)

        if secretary:
            office_delivery_requests = Delivery.query.filter_by(office=logged_in_user.office).order_by(desc(Delivery.date))
            print("Office_delivery ", office_delivery_requests)
            delivery_schema = DeliverySchema(many=True)
            office_requests = delivery_schema.dump(office_delivery_requests)

            print("my_requests: ", office_requests)
            return jsonify({
                'status': 0,
                'message': 'success',
                'payload': office_requests,
            })
        else:
            return jsonify({"message": "Secretary is invalid"}), 405
    else:
        return jsonify({"message": "Token is invalid"}), 405


@views.route('/deliveries/', methods=['GET', 'POST'])
@token_required
def deliveries(logged_in_user):

    if request.method == 'POST':
        print("logged_in_user: ", logged_in_user)
        data = request.get_json()
        print(data)
        new_delivery = Delivery(
            requested_by=logged_in_user,
            receiver=data['receiver'],
            office=data['office'],
            item=data['item'],
            status=Status.PENDING
        )
        print("New delivery ", new_delivery.id)
        print("New delivery ", new_delivery.receiver)
        print("New delivery ", new_delivery.item)
        db.session.add(new_delivery)
        db.session.flush()
        print("New delivery 1 ", new_delivery.id)
        db.session.refresh(new_delivery)
        print("New delivery 2 ", new_delivery.id)
        db.session.commit()
        created = Delivery.query.filter_by(id=new_delivery.id).first()
        print("Query", created)
        delivery_schema = DeliverySchema()
        delivery_request = delivery_schema.dump(created)

        print("Jsoned ", delivery_request)
    return jsonify({
        'status': 0,
        'message': "Delivery request made",
        'payload': delivery_request
    })


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    print(current_user.email)
    print(current_user.id)
    print(current_user.office)
    delivery_requests = Delivery.query.filter_by(senderId=current_user.id)
    my_requests = []
    for item in delivery_requests:
        my_request = {
            'item': item.item,
            'receiver': User.query.filter_by(id=item.receiverId).first().email,
            'status': item.status
        }
        my_requests.append(my_request)

    deliveries = Delivery.query.filter_by(receiverId=current_user.id)
    my_deliveries = []
    for item in deliveries:
        my_delivery = {
            'item': item.item,
            'sender': User.query.filter_by(id=item.senderId).first().email,
            'status': item.status
        }

        my_deliveries.append(my_delivery)

    print("my_request")
    print(my_requests)
    print("my_deliveries")
    print(my_deliveries)

    if request.method == 'POST':
        print(request.date)
        item = request.form.get('item')
        office = request.form.get('office')

        office_to = User.query.filter_by(office=office).first()

        if office_to:
            if len(item) < 2:
                flash('Item should be greater than 1 character')
            else:
                new_delivery = Delivery(
                    senderId=current_user.id,
                    receiverId=office_to.id,
                    item=item,
                    status=Status.PENDING
                )

                db.session.add(new_delivery)
                db.session.commit()
                flash('Delivery request made', category='success')

    return render_template("home.html", user=current_user, my_requests=my_requests, my_deliveries=my_deliveries)


@views.route("api_receive_item", methods=['GET'])
@token_required
def receive_item(logged_in_user):
    delivery_id = request.args.get("delivery_id")
    print("delivery_id ", delivery_id)
    if delivery_id:
        delivery_query = Delivery.query.filter_by(id=delivery_id).first()
        delivery_query.status = Status.RECEIVED
        print(delivery_query    )
        print(delivery_query.status)
        db.session.commit()
        delivery_schema = DeliverySchema()
        delivery = delivery_schema.dump(delivery_query)
        print("delivery ", delivery)
        return jsonify(
            {
                "status": 0,
                "message": "Success",
                "payload": delivery
            })
    else:
        return jsonify(
            {
                "status": 1,
                "message": "Invalid delivery request id"
            })

