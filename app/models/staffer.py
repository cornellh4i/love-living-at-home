from .. import db


class Staffer(db.Model):
    """
    A Love Living at Home Office Staff who is responsible for 
      creating/editing requests. 
    NOTE: Some staffers (but not all) are volunteers, so 
      we may need to add a boolean (i.e., `is_volunteer`) and connection 
      between Volunteer and Staffer that is nullable.
    """
    id = db.Column(db.Integer, primary_key=True)
    ## Personal Information
    first_name = db.Column(db.String(80), nullable=False)
    middle_initial = db.Column(db.String(5))
    last_name = db.Column(db.String(80), nullable=False)
    ## Contact Information
    phone_number = db.Column(db.String(10))
    email_address = db.Column(db.String(80), nullable=False)

    requests_created = db.relationship("Request", backref="staffer", lazy=True)

    def __repr__(self):
        return f"Staffer('{self.last_name}, '{self.first_name}')"
