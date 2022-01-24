from .. import db


class Volunteer(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # General Information
    salutation = db.Column(db.String(20))
    first_name = db.Column(db.String(80), nullable=False)
    middle_initial = db.Column(db.String(5))
    last_name = db.Column(db.String(80), nullable=False)
    preferred_name = db.Column(db.String(80))
    gender = db.Column(db.String(80))
    birthdate = db.Column(db.Date, nullable=False)

    # Member ID infomration for member volunteers
    member_id = db.Column(db.Integer(), db.ForeignKey("member.id"))

    # Location Information
    primary_address_id = db.Column(db.Integer(),
                                   db.ForeignKey("address.id"),
                                   nullable=False)
    secondary_address_id = db.Column(db.Integer(), db.ForeignKey("address.id"))

    # Concat Information
    primary_phone_number = db.Column(db.String(64), nullable=False)
    secondary_phone_number = db.Column(db.String(10))
    email_address = db.Column(db.String(80))
    preferred_contact_method = db.Column(db.String(80), nullable=False)

    # Emergency Contact Information
    emergency_contact_name = db.Column(db.String(64))
    emergency_contact_phone_number = db.Column(db.String(64))
    emergency_contact_email_address = db.Column(db.String(64))
    emergency_contact_relationship = db.Column(db.String(64))

    # Volunteer-Specific Information
    is_member_volunteer = db.Column(
        db.Boolean(), nullable=False, default=False)
    is_fully_vetted = db.Column(db.Boolean(), nullable=False, default=False)
    vetting_notes = db.Column(db.Text, default='')
    availability_id = db.Column(db.Integer(), db.ForeignKey("availability.id"))

    general_notes = db.Column(db.String(255), nullable=False)

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
            v = Volunteer(first_name=fake.first_name(),
                          last_name=fake.last_name(),
                          birthdate=datetime.strptime(fake.date(),
                                                      "%Y-%m-%d").date(),
                          primary_address_id=randint(1, 200),
                          primary_phone_number=fake.phone_number(),
                          email_address=choice([fake.email(), None]),
                          is_member_volunteer=False,
                          preferred_contact_method=choice(
                              ['phone', 'email', 'phone and email']),
                          availability_id=i+1,
                          general_notes=fake.text(),
                          **kwargs)
            db.session.add(v)
            try:
                db.session.commit()
            except IntegrityError as e:
                print(f"ERROR MAKING VOLUNTEERS: {e}")
                db.session.rollback()

    def __repr__(self):
        return f"Volunteer('{self.first_name} {self.last_name}')"
