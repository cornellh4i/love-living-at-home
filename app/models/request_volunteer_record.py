from flask import current_app
from .. import db

class RequestVolunteerRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('request.id'),
        nullable=False)
    volunteer_id = db.Column(db.Integer, db.ForeignKey('volunteer.id'),
        nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey('status.id'),
        nullable=False)
    staffer_id = db.Column(db.Integer, db.ForeignKey('staffer.id'),
        nullable=False)
    updated_datetime = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f"RequestVolunteerRecord('{self.updated_datetime}')"
    