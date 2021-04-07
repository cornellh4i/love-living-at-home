from flask_sqlalchemy import SQLAlchemy
from flask import current_app

from .. import db


class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    street_address = db.Column(db.String(64), nullable=False)
    city = db.Column(db.String(64), nullable=False)
    state = db.Column(db.String(64), nullable=False)
    country = db.Column(db.String(64), nullable=False)

    def __repr__(self):
        return(f"Address('{self.street_address}',\
                         '{self.city}', '{self.state}', '{self.country}')")
