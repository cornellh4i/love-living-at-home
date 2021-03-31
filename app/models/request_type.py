from flask import current_app
from .. import db
from flask_sqlalchemy import SQLAlchemy

class RequestType(db.Model):
    __tablename__ = 'request types'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(), unique = True, nullable = False)
    requests = db.relationship("Request", backref = "request_type", lazy = True)
    

    def __repr__(self):
        return f"request types( '{self.name}')"