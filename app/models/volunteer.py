from flask import current_app

from .. import db


class Volunteer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ## Personal Information
    first_name = db.Column(db.String(80), nullable=False)
    middle_initial = db.Column(db.String(5))
    last_name = db.Column(db.String(80), nullable=False)
    preferred_name = db.Column(db.String(80))
    gender = db.Column(db.String(80), nullable=False)
    birthdate = db.Column(db.Date(), nullable=False)

    ## Contact Information
    address_id = db.Column(db.Integer(),
                           db.ForeignKey("address.id"),
                           nullable=False)
    phone_number = db.Column(db.String(10), nullable=False)
    email_address = db.Column(db.String(80), nullable=False)

    ## Volunteer-Specific Information
    type_id = db.Column(db.Integer(),
                        db.ForeignKey("volunteer_type.id"),
                        nullable=False)
    last_service_date = db.Column(db.Date(), nullable=False)  # Is this useful?
    rating = db.Column(db.Integer(), nullable=False)
    is_fully_vetted = db.Column(db.Boolean(), nullable=False)
    preferred_contact_method_id = db.Column(db.Integer(),
                                            db.ForeignKey("contact_method.id"),
                                            nullable=False)
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
                gender=choice(['Female', 'Male', 'Other',
                               'Prefer Not to Say']),
                birthdate=datetime.strptime(fake.date(), "%Y-%m-%d").date(),
                address_id=-1,
                phone_number=fake.phone_number(),
                email_address=fake.email(),
                type_id=-1,
                last_service_date=datetime.strptime(
                    fake.date(),
                    "%Y-%m-%d").date(),  # would they like this to be required?
                rating=random() * 5.0,  # would they like this to be required?
                is_fully_vetted=choice([True, False]),
                preferred_contact_method_id=-1,
                general_notes=fake.text(),
                **kwargs)
            db.session.add(v)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    def __repr__(self):
        return f"Volunteer('{self.first_name}', '{self.last_name}')"


class VolunteerType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    volunteers = db.relationship("Volunteer",
                                 backref="volunteer_type",
                                 lazy=True)

    @staticmethod
    def insert_types():
        types = ['Member Volunteer', 'Non-Member Volunteer']
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
    )  # one of ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
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


# For Creating Services
class ContactMethod(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    volunteers = db.relationship("Volunteer",
                                 backref="contact_method",
                                 lazy=True)

    def __repr__(self):
        return f"ContactMethod('{self.name}')"
