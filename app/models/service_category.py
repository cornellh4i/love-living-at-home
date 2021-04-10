from flask import current_app
from flask_sqlalchemy import SQLAlchemy

from .. import db


class ServiceCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), unique=True, nullable=False)
    services = db.relationship("Service",
                               backref="service_category",
                               lazy=True)
    requests = db.relationship("Request",
                               backref="service_category",
                               lazy=True)

    @staticmethod
    def insert_categories():
        categories = [
            'COVID Community Support', 'Professional Home/Garden Services',
            'Professional In-Home Support', 'Technical Support',
            'Transportation', 'Village Admin', 'Volunteer Home/Garden Service',
            'Volunteer In-Home Support'
        ]
        for c in categories:
            category = ServiceCategory.query.filter_by(name=c).first()
            if category is None:
                category = ServiceCategory(name=c)
            db.session.add(category)
        db.session.commit()

    def __repr__(self):
        return f"Service Category('{self.name}')"
