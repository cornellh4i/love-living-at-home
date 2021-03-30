from flask import current_app
from .. import db
from flask_sqlalchemy import SQLAlchemy


class RequestDurationType(db.Model):
    __tablename__ = 'request duration type'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(), unique = True, nullable = False)
    

    def __repr__(self):
        return f"request duration type( '{self.name}')"