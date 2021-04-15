from .. import db


class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ## Name
    salutation = db.Column(db.String(20))
    first_name = db.Column(db.String(64), nullable=False)
    middle_initial = db.Column(db.String(1))
    last_name = db.Column(db.String(64), nullable=False)
    preferred_name = db.Column(db.String(64))
    gender = db.Column(db.String(64))
    ## Location
    primary_address_id = db.Column(db.Integer,
                                   db.ForeignKey('address.id'),
                                   nullable=False)
    secondary_address_id = db.Column(db.Integer, db.ForeignKey('address.id'))
    ## Contact Information
    phone_number = db.Column(db.String(64))
    email_address = db.Column(db.String(64), nullable=False)
    ## Emergency Contact Information
    emergency_contact_name = db.Column(db.String(64))
    emergency_contact_phone_number = db.Column(db.String(64))
    emergency_contact_email_address = db.Column(db.String(64))
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
            member_without_phone = Member(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                primary_address_id=-1,
                email_address=fake.email(),
                membership_expiration_date=datetime.strptime(
                    fake.date(), "%Y-%m-%d").date(),
                volunteer_notes=fake.text(),
                staffer_notes=fake.text(),
                **kwargs)
            member_with_phone = Member(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                primary_address_id=-1,
                phone_number=fake.phone_number(),
                email_address=fake.email(),
                membership_expiration_date=datetime.strptime(
                    fake.date(), "%Y-%m-%d").date(),
                volunteer_notes=fake.text(),
                staffer_notes=fake.text(),
                **kwargs)
            m = choice([member_without_phone, member_with_phone])
            db.session.add(m)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    def __repr__(self):
        return f"Member('{self.first_name}' , '{self.last_name}','{self.email_address}')"
