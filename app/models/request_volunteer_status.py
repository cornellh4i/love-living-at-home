from .. import db


class RequestVolunteerStatus(db.Model):
    """
    The status of a volunteer with respect to a request that has been created. 
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    records = db.relationship('RequestVolunteerRecord',
                             backref='request_volunteer_status',
                             lazy=True)

    @staticmethod
    def insert_statuses():
        statuses = [
            'Called', 'Contact by Email', 'Contact by Phone', 'Called',
            'Emailed', 'Left Message 1', 'Left Message 2', 'Will Call Back',
            'Not Available', 'Available', 'Selected', 'Not Needed',
            'Not Needed/Notified', 'Cancel'
        ]
        for s in statuses:
            status = RequestVolunteerStatus.query.filter_by(name=s).first()
            if status is None:
                status = RequestVolunteerStatus(name=s)
            db.session.add(status)
        db.session.commit()

    def __repr__(self):
        return f"RequestVolunteerStatus('{self.name}', '{self.status}')"
