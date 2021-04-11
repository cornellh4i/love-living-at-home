from flask import current_app
from .. import db
from flask_sqlalchemy import SQLAlchemy

class ServiceCategory(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(), unique = True, nullable = False)
    is_visible = db.Column(db.Boolean, nullable=False) 
    services = db.relationship("Service", backref = "service_category", lazy = True)
    requests = db.relationship("Request", backref = "service_category", lazy = True)

    def __repr__(self):
        return f"Service Category( '{self.name}', '{self.is_visible}')"