from flask_sqlalchemy import SQLAlchemy
from flask import current_app
from .. import db


class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_number = db.Column(db.Integer, unique=True, nullable=False)
    salutation = db.Column(db.String(20))
    first_name = db.Column(db.String(64), nullable=False)
    middle_initial = db.Column(db.String(1))
    last_name = db.Column(db.String(64))
    gender = db.Column(db.String(64), nullable=False)
    birthdate = db.Column(db.Date, nullable=False)
    preferred_name = db.Column(db.String(64))
    address_id = db.Column(db.Integer)
    phone_number = db.Column(db.String(64))
    email_address = db.Column(db.String(64), nullable=False)
    membership_expiration_date = db.Column(db.Date)
    volunteer_notes = db.Column(db.Text)
    staffer_notes = db.Column(db.Text)
    requests = db.relationship(
        'Request', backref='member', lazy='dynamic')
    # data might be sent the other way
    volunteer = db.relationship(
        'Volunteer', backref='member', lazy='dynamic')

    def __repr__(self):
        return f"Member('{self.member_number}', '{self.first_name}' , '{self.last_name}','{self.email_address}')"
