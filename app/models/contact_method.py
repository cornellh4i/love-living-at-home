from flask import current_app
from .. import db

class ContactMethod(db.model):
  __tablename__ = "contact_methods"
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(80), nullable=False)
  volunteers = db.relationship("Volunteer", backref="contact_method", lazy=True)