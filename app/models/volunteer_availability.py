from flask_sqlalchemy import SQLAlchemy
from flask import current_app

from .. import db


class VolunteerAvailability(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    volunteer_id = db.Column(
        db.Integer, db.ForeignKey('volunteer.id'), nullable=False)
    day = db.Column(db.String(20), nullable=False)
    time_period_id = db.Column(db.Integer, unique=True, nullable=False)
    availability_status_id = db.Column(db.Integer, unique=True, nullable=False)
    time_period = db.relationship(
        'TimePeriod', backref='time_period', lazy=True)
    availability_status = db.relationship(
        'AvailabilityStatus', backref='availability_status', lazy=True)
