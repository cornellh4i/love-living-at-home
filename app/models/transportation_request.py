from datetime import datetime

from .. import db


class TransportationRequest(db.Model):
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
        nullable=False,  # can this be null?
        default=datetime.utcnow().date())
    # Time Info
    initial_pickup_time = db.Column(db.Time,
                                    nullable=False,
                                    default=datetime.utcnow().time())
    appointment_time = db.Column(db.Time,
                                 nullable=False,
                                 default=datetime.utcnow().time())
    return_pickup_time = db.Column(db.Time,
                                   nullable=False,
                                   default=datetime.utcnow().time())
    drop_off_time = db.Column(db.Time,
                              nullable=False,
                              default=datetime.utcnow().time())
    is_date_time_flexible = db.Column(db.Boolean, nullable=False)
    duration_type_id = db.Column(db.Integer,
                                 db.ForeignKey('request_duration_type.id'),
                                 nullable=False)
    # Service Info
    service_category_id = db.Column(db.Integer,
                                    db.ForeignKey('service_category.id'),
                                    nullable=False)
    service_id = db.Column(db.Integer,
                           db.ForeignKey('service.id'),
                           nullable=False)
    # Location Info
    starting_address = db.Column(db.String(200), nullable=True)
    destination_address_id = db.Column(db.Integer,
                                       db.ForeignKey('address.id'),
                                       nullable=False)
    # Member Info
    # requesting_member_id = db.Column(db.Integer,
    #                                  db.ForeignKey('member.id'),
    #                                  nullable=False)
    # Misc.
    special_instructions = db.Column(db.Text, nullable=False)
    followup_date = db.Column(db.Date,
                              nullable=False,
                              default=datetime.utcnow().date())
    # Staffer Info
    responsible_staffer_id = db.Column(db.Integer, db.ForeignKey('staffer.id'))
    # Contact Info
    contact_log_priority_id = db.Column(
        db.Integer,
        db.ForeignKey('contact_log_priority_type.id'),
        nullable=False)
    cc_email = db.Column(db.String(120), unique=False, nullable=False)

    def __repr__(self):
        return f"TransportationRequest('{self.created_date}, '{self.cc_email}')"


class RequestDurationType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), unique=True, nullable=False)
    requests = db.relationship("TransportationRequest",
                               backref="request_duration_type",
                               lazy=True)

    @staticmethod
    def insert_types():
        duration_types = ['One Way', 'Round Trip']
        for dt in duration_types:
            duration_type = RequestDurationType.query.filter_by(
                name=dt).first()
            if duration_type is None:
                duration_type = RequestDurationType(name=dt)
            db.session.add(duration_type)
        db.session.commit()

    def __repr__(self):
        return f"transportation request duration type( '{self.name}')"


class RequestStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), unique=True, nullable=False)
    requests = db.relationship("TransportationRequest", backref="request_status", lazy=True)

    @staticmethod
    def insert_statuses():
        statuses = ['Requested', 'Confirmed', 'Completed', 'Cancelled']
        for i, s in enumerate(statuses):
            request_status = RequestStatus.query.filter_by(name=s).first()
            if request_status is None:
                request_status = RequestStatus(id=i, name=s)
            db.session.add(request_status)
        db.session.commit()

    def __repr__(self):
        return f"transportation request status( '{self.name}')"


class RequestType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), unique=True, nullable=False)
    requests = db.relationship("TransportationRequest", backref="request_type", lazy=True)
    service_categories = db.relationship("ServiceCategory",
                                         backref="request_type",
                                         lazy=True)

    @staticmethod
    def get_types():
        import pandas as pd
        request_types = []
        request_types_df = pd.read_csv('./app/data/out/request_types.csv')
        for row in request_types_df.iterrows():
            request_type_id, request_type_name = row[1]
            request_types.append((request_type_id, request_type_name))
        return request_types

    @staticmethod
    def insert_types():
        types = RequestType.get_types()
        for i, t in types:
            request_type = RequestType.query.filter_by(name=t).first()
            if request_type is None:
                request_type = RequestType(id=i, name=t)
            db.session.add(request_type)
        db.session.commit()

    def __repr__(self):
        return f"transportation request types( '{self.name}')"


class ContactLogPriorityType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), unique=True, nullable=False)
    requests = db.relationship("TransportationRequest",
                               backref="contact_log_priority_type",
                               lazy=True)

    @staticmethod
    def insert_types():
        priority_types = ['Urgent', 'High', 'Medium', 'Low']
        for pt in priority_types:
            priority_type = ContactLogPriorityType.query.filter_by(
                name=pt).first()
            if priority_type is None:
                priority_type = ContactLogPriorityType(name=pt)
            db.session.add(priority_type)
        db.session.commit()

    def __repr__(self):
        return f"transportation contact log priority type( '{self.name}')"
