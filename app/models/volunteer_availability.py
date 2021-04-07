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
        'TimePeriod', backref='volunteer_availability', lazy=True)
    availability_status = db.relationship(
        'AvailabilityStatus', backref='volunteer_availability', lazy=True)

    def __repr__(self):
        return f"VolunteerAvailability('{self.day}')"
