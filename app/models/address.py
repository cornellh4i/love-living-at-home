from flask_sqlalchemy import SQLAlchemy
from flask import current_app

from .. import db


class Address(db.Model):
    id = db.Column(db.Integer, db.ForeignKey(
        'request.starting_address_id'), primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    street_address = db.Column(db.String(64), nullable=False)
    city = db.Column(db.String(64), nullable=False)
    state = db.Column(db.String(64), nullable=False)
    country = db.Column(db.String(64), nullable=False)
