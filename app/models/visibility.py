from flask import current_app
from .. import db

class Visibility(db.model):
  __tablename__ = "visibilities"
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(80), nullable=False)
  volunteers = db.relationship("Volunteer", backref="visibility", lazy=True)