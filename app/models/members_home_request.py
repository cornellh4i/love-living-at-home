from datetime import datetime

from .. import db


class MembersHomeRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type_id = db.Column(db.Integer,
                        db.ForeignKey('request_type.id'),
                        nullable=False)
    status_id = db.Column(db.Integer,
                          db.ForeignKey('request_status.id'),
                          nullable=False)
    short_description = db.Column(db.Text, nullable=False)
    created_date = db.Column(db.Date,
                             nullable=False,
                             default=datetime.utcnow().date())
    modified_date = db.Column(db.Date,
                              nullable=False,
                              default=datetime.utcnow().date())
    requested_date = db.Column(db.Date)

    home_location = db.Column(db.Text, nullable=False)

    from_time = db.Column(db.Time,
                          nullable=False,
                          default=datetime.utcnow().time())
    until_time = db.Column(db.Time,
                           nullable=False,
                           default=datetime.utcnow().time())

    is_date_time_flexible = db.Column(db.Boolean, nullable=False)

    service_category_id = db.Column(db.Integer,
                                    db.ForeignKey('service_category.id'),
                                    nullable=False)
    service_id = db.Column(db.Integer,
                           db.ForeignKey('service.id'),
                           nullable=False)

    special_instructions = db.Column(db.Text, nullable=False)
    followup_date = db.Column(db.Date,
                              nullable=False,
                              default=datetime.utcnow().date())
    responsible_staffer_id = db.Column(db.Integer, db.ForeignKey('staffer.id'))
    contact_log_priority_id = db.Column(
        db.Integer,
        db.ForeignKey('contact_log_priority_type.id'),
        nullable=False)
    cc_email = db.Column(db.String(120), unique=False, nullable=False)

    # based on status of the request
    cancellation_reason_id = db.Column(
        db.Integer, db.ForeignKey('cancellation_reason.id'), unique=False)
    rating = db.Column(db.Integer)
    member_comments = db.Column(db.String(1000))
    provider_comments = db.Column(db.String(1000))
    duration_in_mins = db.Column(db.Integer)
    number_of_trips = db.Column(db.Integer)
    mileage = db.Column(db.Integer)
    expenses = db.Column(db.Integer)
    verified_by = db.Column(db.Integer)

    def __repr__(self):
        return f"Member\'s Home Request('{self.created_date}, '{self.cc_email}')"
