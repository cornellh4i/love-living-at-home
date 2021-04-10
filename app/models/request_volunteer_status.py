from flask import current_app
from .. import db

class RequestVolunteerStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    status = db.relationship('RequestVolunteerRecord', backref='record', lazy=True)
    
    @staticmethod
    def insert_statuses():
        statuses = [
            'Called', 
            'Contact by Email',
            'Contact by Phone',
            'Called',
            'Emailed',
            'Left Message 1',
            'Left Message 2',
            'Will Call Back',
            'Not Available',
            'Available',
            'Selected',
            'Not Needed',
            'Not Needed/Notified',
            'Cancel'
        ]
        for s in statuses:
            status = RequestVolunteerStatus.query.filter_by(name=s).first()
            if status is None:
                status = RequestVolunteerStatus(name=s)
            db.session.add(status)
        db.session.commit()

    def __repr__(self):
        return f"RequestVolunteerStatus('{self.name}', '{self.status}')"