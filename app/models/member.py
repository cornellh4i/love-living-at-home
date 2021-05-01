from .. import db


class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ## Name
    salutation = db.Column(db.String(20))
    member_number = db.Column(db.Integer) #NEW
    first_name = db.Column(db.String(64), nullable=False)
    middle_initial = db.Column(db.String(1))
    last_name = db.Column(db.String(64), nullable=False)
    preferred_name = db.Column(db.String(64))
    gender = db.Column(db.String(64), nullable=False) # Dropdown: [Female, Male, Unspecified, Does not wish to answer]
    birthdate = db.Column(db.Date, nullable=False) #NEW
    ## Location
    primary_address_id = db.Column(db.Integer,
                                   db.ForeignKey('address.id'),
                                   nullable=False)
    secondary_address_id = db.Column(db.Integer, db.ForeignKey('address.id'))
    metro_area_id = db.Column(db.Integer, db.ForeignKey('metro_area.id'))
    ## Contact Information
    primary_phone_number = db.Column(db.String(64), nullable=False) #NAME CHANGE
    secondary_phone_number = db.Column(db.String(64)) #NEW
    email_address = db.Column(db.String(64))
    ## Emergency Contact Information
    emergency_contact_name = db.Column(db.String(64))
    emergency_contact_phone_number = db.Column(db.String(64))
    emergency_contact_email_address = db.Column(db.String(64))
    emergency_contact_relation = db.Column(db.String(64)) #NEW
    ## Membership Info
    membership_expiration_date = db.Column(db.Date, nullable=False)
    ## Service Notes
    # Notes about this member that volunteers can see.
    volunteer_notes = db.Column(db.Text)
    # Notes about this member that only the staffers can see.
    staffer_notes = db.Column(db.Text)
    requests = db.relationship('Request', backref='member', lazy='dynamic')

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
            m = Member(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                gender=choice(['Male', 'Female', 'Unspecified', 'Does Not Wish to Answer']),
                birthdate=datetime.strptime(
                    fake.date(), "%Y-%m-%d").date(),
                primary_address_id=-1,
                primary_phone_number=fake.phone_number(),
                secondary_phone_number=choice([fake.phone_number(), None]),
                email_address=choice([fake.email(), None]),
                membership_expiration_date=datetime.strptime(
                    fake.date(), "%Y-%m-%d").date(),
                volunteer_notes=fake.text(),
                staffer_notes=fake.text(),
                **kwargs)
            db.session.add(m)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    def __repr__(self):
        return f"Member('{self.first_name}' , '{self.last_name}','{self.email_address}')"
