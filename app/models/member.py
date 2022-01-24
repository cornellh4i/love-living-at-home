from .. import db


class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # General Information
    salutation = db.Column(db.String(20))
    first_name = db.Column(db.String(64), nullable=False)
    middle_initial = db.Column(db.String(1))
    last_name = db.Column(db.String(64), nullable=False)
    preferred_name = db.Column(db.String(64))
    gender = db.Column(db.String(64), nullable=False)
    birthdate = db.Column(db.Date, nullable=False)

    # Volunteer ID infomration for member volunteers
    volunteer_id = db.Column(db.Integer(), db.ForeignKey("volunteer.id"))

    # Membership Information
    member_number = db.Column(db.Integer, nullable=False)
    membership_expiration_date = db.Column(db.Date, nullable=False)

    # Location Information
    primary_address_id = db.Column(db.Integer,
                                   db.ForeignKey('address.id'),
                                   nullable=False)
    secondary_address_id = db.Column(db.Integer, db.ForeignKey('address.id'))

    # Contact Information
    primary_phone_number = db.Column(db.String(80), nullable=False)
    secondary_phone_number = db.Column(db.String(80))
    email_address = db.Column(db.String(64))
    preferred_contact_method = db.Column(db.String(80), nullable=False)

    # Emergency Contact Information
    emergency_contact_name = db.Column(db.String(64))
    emergency_contact_phone_number = db.Column(db.String(64))
    emergency_contact_email_address = db.Column(db.String(64))
    emergency_contact_relationship = db.Column(db.String(64))

    # Service Notes
    # Notes about this member that volunteers can see.
    volunteer_notes = db.Column(db.Text)
    # Notes about this member that only the staffers can see.
    staffer_notes = db.Column(db.Text)

    @staticmethod
    def generate_fake(count=100, **kwargs):
        """Generate a number of fake users for testing."""
        from sqlalchemy.exc import IntegrityError
        from random import seed, choice, randint
        from faker import Faker
        from datetime import datetime

        fake = Faker()

        seed()
        for i in range(count):
            m = Member(
                member_number=i,
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                gender=choice([
                    'Male', 'Female', 'Unspecified', 'Does Not Wish to Answer'
                ]),
                birthdate=datetime.strptime(fake.date(), "%Y-%m-%d").date(),
                primary_address_id=randint(1, 200),
                primary_phone_number=fake.phone_number(),
                secondary_phone_number=choice([fake.phone_number(), None]),
                email_address=choice([fake.email(), None]),
                preferred_contact_method=choice(
                    ['phone', 'email', 'phone and email']),
                membership_expiration_date=datetime.strptime(
                    fake.date(), "%Y-%m-%d").date(),
                volunteer_notes=fake.text(),
                staffer_notes=fake.text(),
                **kwargs)
            db.session.add(m)
            try:
                db.session.commit()
            except IntegrityError:
                print("ERROR")
                db.session.rollback()

    def __repr__(self):
        return f"Member('{self.member_number}')"
