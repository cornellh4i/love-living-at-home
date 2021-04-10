from flask import current_app
from .. import db
from flask_sqlalchemy import SQLAlchemy


class Staffer(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    first_name = db.Column(db.String(), unique = True, nullable = False)
    last_name = db.Column(db.String(), unique = True, nullable = False)

    def __repr__(self):
        return f"Staffer('ID: {self.id}: {self.first_name} {self.last_name}')"

