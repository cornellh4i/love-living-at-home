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
    phone_number = db.Column(db.String(80))
    email_address = db.Column(db.String(80), nullable=False)

    requests_created = db.relationship("Request", backref="staffer", lazy=True)

    @staticmethod
    def generate_fake(count=100, **kwargs):
        """Generate a number of fake users for testing."""
        from sqlalchemy.exc import IntegrityError
        from random import seed, choice, random
        from faker import Faker
        from datetime import datetime

        fake = Faker()

        seed()
        for i in range(count):
            a = Staffer(first_name=fake.first_name(),
                        last_name=fake.last_name(),
                        phone_number=fake.phone_number(),
                        email_address=fake.email(),
                        **kwargs)
            db.session.add(a)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    def __repr__(self):
        return f"Staffer('{self.last_name}, '{self.first_name}')"
