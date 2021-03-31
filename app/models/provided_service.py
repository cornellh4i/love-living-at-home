from flask import current_app
from .. import db

class ProvidedService(db.Model):
    __tablename__ = 'provided_services'
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'),
        nullable=False)
    volunteer_id = db.Column(db.Integer, db.ForeignKey('volunteer.id'),
        nullable=False)
    volunteer_status = db.Column(db.String(80), nullable=false)
    