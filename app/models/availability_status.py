from flask_sqlalchemy import SQLAlchemy
from flask import current_app

from .. import db


class AvailabilityStatus(db.Model):
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    name = db.Column(db.String(64), nullable=False)

    def __repr__(self):
        return f"AvailabilityStatus('{self.name}')"
