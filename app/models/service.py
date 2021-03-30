from flask import current_app
from .. import db
from flask_sqlalchemy import SQLAlchemy

from service_category.py import ServiceCategory

class Service(db.Model):
    __tablename__ = 'services'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(), unique = True, nullable = False)
    category_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False) 

    def __repr__(self):
        return f"Service( '{self.name}', '{self.category_id}')"

