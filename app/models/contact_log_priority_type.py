from flask import current_app
from .. import db
from flask_sqlalchemy import SQLAlchemy


class ContactLogPriorityType(db.Model):
    __tablename__ = 'contact log priority types'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(), unique = True, nullable = False)
    requests = db.relationship("Request", backref = "contact_log_priority_type", lazy = True)
    

    def __repr__(self):
        return f"contact log priority type( '{self.name}')"