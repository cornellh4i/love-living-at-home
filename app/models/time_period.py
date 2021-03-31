from flask_sqlalchemy import SQLAlchemy
from flask import current_app

from .. import db


class TimePeriod(db.Model):
    id = db.Column(db.Integer, db.ForeignKey(
        'volunteer_availability.time_period_id'), nullable=False)
    name = db.Column(db.String(64), nullable=False)
