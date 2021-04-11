from flask import current_app
from .. import db

class VolunteerType(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(80), nullable=False)
  volunteers = db.relationship("Volunteer", backref="volunteer_type", lazy=True)

  def __repr__(self):
        return f"VolunteerType('{self.name}')"