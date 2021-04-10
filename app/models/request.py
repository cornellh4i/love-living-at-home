from flask import current_app
from datetime import datetime
from .. import db

class Request(db.Model):
  id = db.Column(db.Integer, primary_key = True)
  type_id = db.Column(db.Integer, db.ForeignKey('request_type.id'), nullable = False)
  status_id = db.Column(db.Integer, db.ForeignKey('request_status.id'), nullable = False)
  short_description = db.Column(db.Text, nullable = False)
  # Date Info
  created_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow().date())
  modified_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow().date())
  requested_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow().date())
  # Time Info
  initial_pickup_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow().time())
  appointment_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow().time())
  return_pickup_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow().time())
  drop_off_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow().time())
  is_date_time_flexible = db.Column(db.Boolean, nullable = False)
  duration_type_id = db.Column(db.Integer, db.ForeignKey('request_duration_type.id'), nullable = False)
  # Service Info
  service_category_id = db.Column(db.Integer, db.ForeignKey('service_category.id'), nullable = False)
  service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable = False)
  # Location Info
  starting_address_id = db.Column(db.Integer, db.ForeignKey('address.id'), nullable = False)
  destination_address_id = db.Column(db.Integer, db.ForeignKey('contact_method.id'), nullable = False)
  # Member Info
  requesting_member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable = False)
  # Misc.
  special_instructions = db.Column(db.Text, nullable = False)
  followup_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow().date())
  # Staffer Info
  responsible_staffer_id = db.Column(db.Integer, db.ForeignKey('staffer.id'), nullable = False)
  # Contact Info
  contact_log_priority_id = db.Column(db.Integer, db.ForeignKey('contact_log_priority_type.id'), nullable = False)
  cc_email = db.Column(db.String(120), unique=True, nullable=False)

  def __repr__(self):
    return f"Request('{self.created_date}, '{self.cc_email}')"

class RequestDurationType(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(), unique = True, nullable = False)
    requests = db.relationship("Request", backref = "request_duration_type", lazy = True)
    
    def __repr__(self):
        return f"request duration type( '{self.name}')"

class RequestStatus(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(), unique = True, nullable = False)
    requests = db.relationship("Request", backref = "request_status", lazy = True)
    
    def __repr__(self):
        return f"request status( '{self.name}')"

class RequestType(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(), unique = True, nullable = False)
    requests = db.relationship("Request", backref = "request_type", lazy = True)
    
    def __repr__(self):
        return f"request types( '{self.name}')"

class ContactLogPriorityType(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(), unique = True, nullable = False)
    requests = db.relationship("Request", backref = "contact_log_priority_type", lazy = True)

    def __repr__(self):
        return f"contact log priority type( '{self.name}')"