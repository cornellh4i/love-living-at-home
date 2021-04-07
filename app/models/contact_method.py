from flask import current_app
from .. import db

class ContactMethod(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(80), nullable=False)
  volunteers = db.relationship("Volunteer", backref="contact_method", lazy=True)

  def __repr__(self):
        return f"ContactMethod('{self.name}')"