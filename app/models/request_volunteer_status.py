from flask import current_app
from .. import db

class RequestVolunteerStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    status = db.relationship('RequestVolunteerRecord', backref='record', lazy=True)
    
    def __repr__(self):
        return f"RequestVolunteerStatus('{self.name}', '{self.status}')"