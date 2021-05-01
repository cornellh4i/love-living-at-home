from .. import db


class Volunteer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ## Personal Information
    first_name = db.Column(db.String(80), nullable=False)
    middle_initial = db.Column(db.String(5))
    last_name = db.Column(db.String(80), nullable=False)
    preferred_name = db.Column(db.String(80))
    gender = db.Column(db.String(80))
    birthdate = db.Column(db.Date(), nullable=False)
    ## Contact Information
    primary_address_id = db.Column(db.Integer(),
                           db.ForeignKey("address.id"),
                           nullable=False)
    secondary_address_id = db.Column(db.Integer(),
                           db.ForeignKey("address.id"))
    metro_area_id = db.Column(db.Integer, db.ForeignKey('metro_area.id'))

    primary_phone_number = db.Column(db.String(10), nullable=False)
    secondary_phone_number = db.Column(db.String(10))

    organization_name = db.Column(db.String(80))
    email_address = db.Column(db.String(80))

    ## Volunteer-Specific Information
    type_id = db.Column(db.Integer(),
                        db.ForeignKey("volunteer_type.id"),
                        nullable=False)
    rating = db.Column(db.Integer(), nullable=False)
    is_fully_vetted = db.Column(db.Boolean(), nullable=False)
    vettings = db.Column(db.Text)
    preferred_contact_method = db.Column(db.String(80), nullable=False) # One of: ['phone', 'email', 'phone and email'], implement as checkboxes
    
    ## Emergency Contact Information
    emergency_contact_name = db.Column(db.String(64))
    emergency_contact_phone_number = db.Column(db.String(64))
    emergency_contact_email_address = db.Column(db.String(64))
    emergency_contact_relation = db.Column(db.String(64)) 

    general_notes = db.Column(db.String(255), nullable=False)

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
            v = Volunteer(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                birthdate=datetime.strptime(
                    fake.date(), "%Y-%m-%d").date(),
                primary_address_id=-1,
                primary_phone_number=fake.phone_number(),
                email_address=choice([fake.email(), None]),
                type_id=choice([0, 1, 2]),
                rating=random() * 5.0,  
                is_fully_vetted=choice([True, False]),
                vettings=choice([fake.text(), None]),
                preferred_contact_method=choice(['phone', 'email', 'phone and email']),
                general_notes=fake.text(),
                **kwargs)
            db.session.add(v)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    def __repr__(self):
        return f"Volunteer('{self.first_name} {self.last_name}')"


class VolunteerType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    volunteers = db.relationship("Volunteer",
                                 backref="volunteer_type",
                                 lazy=True)

    @staticmethod
    def insert_types():
        types = ['Member Volunteer', 'Non-Member Volunteer', 'Local Resource']
        for t in types:
            volunteer_type = VolunteerType.query.filter_by(name=t).first()
            if volunteer_type is None:
                volunteer_type = VolunteerType(name=t)
            db.session.add(volunteer_type)
        db.session.commit()

    def __repr__(self):
        return f"VolunteerType('{self.name}')"


# For Availability
class VolunteerAvailability(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    volunteer_id = db.Column(db.Integer,
                             db.ForeignKey('volunteer.id'),
                             nullable=False)
    day_of_week = db.Column(
        db.String(20), nullable=False
    )  # one of ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    time_period_id = db.Column(db.Integer,
                               db.ForeignKey('time_period.id'),
                               unique=True,
                               nullable=False)
    availability_status_id = db.Column(db.Integer,
                                       db.ForeignKey('availability_status.id'),
                                       unique=True,
                                       nullable=False)

    def __repr__(self):
        return f"VolunteerAvailability('{self.day}')"


class AvailabilityStatus(db.Model):
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    name = db.Column(db.String(64), nullable=False)

    @staticmethod
    def insert_statuses():
        statuses = [
            'Most likely available', 'Not available',
            'Backup - might be available', 'Call me if really desperate'
        ]
        for s in statuses:
            availability_status = AvailabilityStatus.query.filter_by(
                name=s).first()
            if availability_status is None:
                availability_status = AvailabilityStatus(name=s)
            db.session.add(availability_status)
        db.session.commit()

    def __repr__(self):
        return f"AvailabilityStatus('{self.name}')"


class TimePeriod(db.Model):
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    name = db.Column(db.String(64), nullable=False)

    @staticmethod
    def insert_time_periods():
        time_periods = [
            'Morning 8-11', 'Lunchtime 11-2', 'Afternoon 2-5', 'Evening 5-8',
            'Night 8-Midnight'
        ]
        for tp in time_periods:
            time_period = TimePeriod.query.filter_by(name=tp).first()
            if time_period is None:
                time_period = TimePeriod(name=tp)
            db.session.add(time_period)
        db.session.commit()

    def __repr__(self):
        return f"TimePeriod('{self.name}')"


# For Vacation Calendar
class VolunteerVacationDay(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    volunteer_id = db.Column(db.Integer,
                             db.ForeignKey('volunteer.id'),
                             nullable=False)
    date = db.Column(db.Date, nullable=False)

    def __repr__(self):
        return f"VolunteerVacationDay('{self.date}')"

