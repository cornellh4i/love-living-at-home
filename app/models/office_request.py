from datetime import datetime

from .. import db

class OfficeRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type_id = db.Column(db.Integer,
                        db.ForeignKey('request_type.id'),
                        nullable=False)
    status_id = db.Column(db.Integer,
                          db.ForeignKey('request_status.id'),
                          nullable=False)
    short_description = db.Column(db.Text, nullable=False)
    # Date Info
    created_date = db.Column(db.Date,
                             nullable=False,
                             default=datetime.utcnow().date())
    modified_date = db.Column(db.Date,
                              nullable=False,
                              default=datetime.utcnow().date())
    requested_date = db.Column(
        db.Date,
        default=datetime.utcnow().date())
    # Time Info
    start_time =db.Column(db.Time,
                            nullable=False,
                            default=datetime.utcnow().time())
    end_time =db.Column(db.Time,
                        nullable=False,
                        default=datetime.utcnow().time())
    is_high_priority = db.Column(db.Boolean, nullable=False)
    # Service Info
    service_category_id = db.Column(db.Integer,
                                    db.ForeignKey('service_category.id'),
                                    nullable=False)
    service_id = db.Column(db.Integer,
                           db.ForeignKey('service.id'),
                           nullable=False)

    # Misc.
    special_instructions = db.Column(db.Text, nullable=False)
    # Staffer Info
    responsible_staffer_id = db.Column(db.Integer, db.ForeignKey('staffer.id'))
    # Contact Info
    contact_log_priority_id = db.Column(
        db.Integer,
        db.ForeignKey('contact_log_priority_type.id'),
        nullable=False)
    cc_email = db.Column(db.String(120), unique=False, nullable=False)

    def __repr__(self):
        return f"Request('{self.created_date}, '{self.cc_email}')"