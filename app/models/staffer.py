from .. import db

class Staffer(db.Model):
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
        return f"Staffer('{self.created_date}, '{self.cc_email}')"