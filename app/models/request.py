from flask import current_app
from flask_login import AnonymousUserMixin, UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature, SignatureExpired
from werkzeug.security import check_password_hash, generate_password_hash

from .. import db, login_manager

from service.py import Service
from service_category.py import ServiceCategory
from request_type.py import RequestType
from request_status.py import RequestStatus
from request_duration_type.py import RequestDurationType
from contact_log_priority_types.py import ContactLogPriorityType

class Request(db.Model):
  __tablename__ = 'request'
  id = db.Column(db.Integer, primary_key = True)
  type_id = db.Column(db.Integer, nullable = False, db.ForeignKey('RequestType.id')
  status_id = db.Column(db.Integer, nullable = False, db.ForeignKey('RequestStatus.id') #are ids unique? nullable?
  created_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow.date) #should be date??
  requested_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow.date)
  initial_pickup_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow.time)
  appointment_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow.time)
  return_pickup_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow.time)
  drop_off_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow.time)
  is_date_time_flexible = db.Column(db.Boolean, nullable = False)
  short_description = db.Column(db.Text, nullable = False) #should this be nullable?
  service_category_id = db.Column(db.Integer, nullable = False, db.ForeignKey('ServiceCategory.id')
  service_id = db.Column(db.Integer, nullable = False, db.ForeignKey('Service.id')
  starting_address_id = db.Column(db.Integer, nullable = False)
  destination_address_id = db.Column(db.Integer, nullable = False)
  duration_type_id = db.Column(db.Integer, nullable = False, db.ForeignKey('RequestDurationType.id')
  modified_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow.date)
  requesting_member_id = db.Column(db.Integer, nullable = False)
  special_instructions = db.Column(db.Text, nullable = False) #should this be nullable?
  followup_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow.date)
  responsible_staffer_id = db.Column(db.Integer, nullable = False)
  contact_log_priority_id = db.Column(db.Integer, nullable = False, db.ForeignKey('ContactLogPriority.id')
  cc_email = db.Column(db.String(120), unique=True, nullable=False)

  def __repr__(self):
    return f"Request('{self.created_date}, '{self.cc_email}')" #are these the right fields?