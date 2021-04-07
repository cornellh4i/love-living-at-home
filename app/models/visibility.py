from flask import current_app
from .. import db

class Visibility(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(80), nullable=False)
  volunteers = db.relationship("Volunteer", backref="visibility", lazy=True)

  def __repr__(self):
        return f"Visibility('{self.name}')"