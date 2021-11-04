from .. import db


class RequestVolunteerRecord(db.Model):
    """
    A record of a volunteer associated with a request.
    (e.g., "Volunteer1 has been emailed (an example of a possible volunteer-request <status>) for request Request2.")
    """
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer,
                           nullable=False)
    request_category_id = db.Column(db.Integer,
                                    db.ForeignKey('request_type.id'),
                                    nullable=False)
    volunteer_id = db.Column(db.Integer,
                             db.ForeignKey('volunteer.id'),
                             nullable=False)
    status_id = db.Column(db.Integer,
                          db.ForeignKey('request_volunteer_status.id'),
                          nullable=False)
    staffer_id = db.Column(db.Integer,
                           db.ForeignKey('staffer.id'),
                           nullable=False)
    updated_datetime = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f"RequestVolunteerRecord('{self.updated_datetime}')"
