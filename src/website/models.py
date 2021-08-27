from sqlalchemy import func
from flask_login import UserMixin
from enum import Enum
from marshmallow_sqlalchemy.fields import Nested

from . import db
from . import ma


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    name = db.Column(db.String(150))
    phone = db.Column(db.String(150))
    password = db.Column(db.String(150))
    office = db.Column(db.String(150))
    role = db.Column(db.String(150))
    # requests = db.relationship('Delivery', backref='requested_by')


class Delivery(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    senderId = db.Column(db.Integer, db.ForeignKey('user.id'))
    receiver = db.Column(db.String(150))
    item = db.Column(db.String(150))
    office = db.Column(db.String(150))
    status = db.Column(db.String(150))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    requested_by = db.relationship('User', backref='requests')


class Status(str, Enum):
    PENDING = 'PENDING'
    IN_PROGRESS = 'IN_PROGRESS'
    DELIVERED = 'DELIVERED'
    RECEIVED = 'RECEIVED'


class UserSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User

    id = ma.auto_field()
    name = ma.auto_field()
    email = ma.auto_field()
    phone = ma.auto_field()
    office = ma.auto_field()
    role = ma.auto_field()


class DeliverySchema(ma.SQLAlchemySchema):
    class Meta:
        model = Delivery

    id = ma.auto_field()
    # senderId = ma.auto_field()
    receiver = ma.auto_field()
    item = ma.auto_field()
    office = ma.auto_field()
    status = ma.auto_field()
    date = ma.auto_field()
    requested_by = Nested(UserSchema)
