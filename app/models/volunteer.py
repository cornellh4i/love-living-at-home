from flask import current_app
from .. import db

class Volunteer(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  first_name = db.Column(db.String(80), nullable=False)
  last_name = db.Column(db.String(80), nullable=False)
  gender = db.Column(db.String(80), nullable=False)
  birthdate = db.Column(db.Date(), nullable=False)
  preferred_name = db.Column(db.String(80), nullable=False)
  address_id = db.Column(db.Integer(), db.ForeignKey("address.id"), nullable=False)
  phone_number = db.Column(db.String(10), nullable=False)
  email_address = db.Column(db.String(80), nullable=False)
  company = db.Column(db.String(80), nullable=False)
  job_title = db.Column(db.String(80), nullable=False)
  type_id = db.Column(db.Integer(), db.ForeignKey("volunteer_type.id"), nullable=False)
  visibility_id = db.Column(db.Integer(), db.ForeignKey("visibility.id"), nullable=False)
  last_service_date = db.Column(db.Date(), nullable=False)
  rating = db.Column(db.Integer(), nullable=False)
  is_fully_vetted = db.Column(db.Boolean(), nullable=False)
  preferred_contact_method_id = db.Column(db.Integer(), db.ForeignKey("contact_method.id"), nullable=False)
  general_notes = db.Column(db.String(255), nullable=False)

  def __repr__(self):
        return f"Volunteer('{self.first_name}', '{self.last_name}')"