from flask import current_app
from .. import db
from flask_sqlalchemy import SQLAlchemy


class RequestStatus(db.Model):
    __tablename__ = 'request status'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(), unique = True, nullable = False)
    requests = db.relationship("Request", backref = "request_status", lazy = True)
    

    def __repr__(self):
        return f"request status( '{self.name}')"