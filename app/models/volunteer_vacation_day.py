from flask_sqlalchemy import SQLAlchemy
from flask import current_app
from .. import db


class VolunteerVacationDay(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    volunteer_id = db.Column(
        db.Integer, db.ForeignKey('volunteer.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)

    def __repr__(self):
        return f"VolunteerVacationDay('{self.date}')"
