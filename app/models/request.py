from flask import current_app
from datetime import datetime


from .. import db

class Request(db.Model):
  id = db.Column(db.Integer, primary_key = True)
  type_id = db.Column(db.Integer, db.ForeignKey('request_type.id'), nullable = False)
  type = db.relationship("Type", backref="request", lazy = True)
  status_id = db.Column(db.Integer, db.ForeignKey('request_status.id'), nullable = False)
  status = db.relationship("Status", backref="request", lazy = True)
  created_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow().date())
  requested_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow().date())
  initial_pickup_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow().time())
  appointment_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow().time())
  return_pickup_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow().time())
  drop_off_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow().time())
  is_date_time_flexible = db.Column(db.Boolean, nullable = False)
  short_description = db.Column(db.Text, nullable = False)
  service_category_id = db.Column(db.Integer, db.ForeignKey('service_category.id'), nullable = False)
  service_category = db.relationship("Service Category", backref="request", lazy = True)
  service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable = False)
  service = db.relationship("Service", backref="request", lazy = True)
  starting_address_id = db.Column(db.Integer, db.ForeignKey('address.id'), nullable = False)
  starting_address = db.relationship("Starting Address", backref="request", lazy = True)
  destination_address_id = db.Column(db.Integer, db.ForeignKey('contact_method.id'), nullable = False)
  destination_address = db.relationship("Destination Address", backref="request", lazy = True)
  duration_type_id = db.Column(db.Integer, db.ForeignKey('request_duration_type.id'), nullable = False)
  duration_type = db.relationship("Duration Type", backref="request", lazy = True)
  modified_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow().date())
  requesting_member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable = False)
  requesting_member = db.relationship("Requesting Member", backref="request", lazy = True)
  special_instructions = db.Column(db.Text, nullable = False)
  followup_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow().date())
  responsible_staffer_id = db.Column(db.Integer, db.ForeignKey('staffer.id'), nullable = False)
  responsible_staffer = db.relationship("Responsible Staffer", backref="request", lazy = True)
  contact_log_priority_id = db.Column(db.Integer, db.ForeignKey('contact_log_priority_type.id'), nullable = False)
  contact_log_priority = db.relationship("Contact Log", backref="request", lazy = True)
  cc_email = db.Column(db.String(120), unique=True, nullable=False)

  def __repr__(self):
    return f"Request('{self.created_date}, '{self.cc_email}')"