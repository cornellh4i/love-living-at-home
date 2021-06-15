from .. import db

NUM_VOLUNTEERS=100

class Volunteer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ## Personal Information
    salutation = db.Column(db.String(20))
    first_name = db.Column(db.String(80), nullable=False)
    middle_initial = db.Column(db.String(5))
    last_name = db.Column(db.String(80), nullable=False)
    preferred_name = db.Column(db.String(80))
    gender = db.Column(db.String(80))
    birthdate = db.Column(db.Date, nullable=False)
    ## Contact Information
    primary_address_id = db.Column(db.Integer(),
                          db.ForeignKey("address.id"),
                          nullable=False)
    secondary_address_id = db.Column(db.Integer(),
                          db.ForeignKey("address.id"))
    metro_area_id = db.Column(db.Integer, db.ForeignKey('metro_area.id'))

    primary_phone_number = db.Column(db.String(80), nullable=False)
    secondary_phone_number = db.Column(db.String(80))

    #organization_name = db.Column(db.String(80))
    email_address = db.Column(db.String(80))
    preferred_contact_method = db.Column(db.String(80), nullable=False) # One of: ['phone', 'email', 'phone and email'], implement as checkboxes

    ## Volunteer-Specific Information
    type_id = db.Column(db.Integer(),
                        db.ForeignKey("volunteer_type.id"),
                        nullable=False)
                    
    rating = db.Column(db.Float(), nullable=False)
    is_fully_vetted = db.Column(db.Boolean(), nullable=False)
    vettings = db.Column(db.Text)
    
    ## Emergency Contact Information
    emergency_contact_name = db.Column(db.String(64))
    emergency_contact_phone_number = db.Column(db.String(64))
    emergency_contact_email_address = db.Column(db.String(64))
    emergency_contact_relation = db.Column(db.String(64)) 

    general_notes = db.Column(db.String(255), nullable=False)

    @staticmethod
    def generate_fake(count=NUM_VOLUNTEERS, **kwargs):
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
                primary_address_id=1,
                primary_phone_number=fake.phone_number(),
                email_address=choice([fake.email(), None]),
                type_id=choice([0, 1]),
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
    )  # one of ['Mon', 'Tues', 'Wed', 'Thurs', 'Fri', 'Sat', 'Sun']
    start_hour = db.Column(db.Integer, nullable=False) # 24-hour time [0-23] (e.g., if '13', then this entry is for 1-2pm).
    end_hour = db.Column(db.Integer, nullable=False) # same as start_hour: should be in range [0, 23]
    availability_status_id = db.Column(db.Integer,
                                       db.ForeignKey('availability_status.id'),
                                       nullable=False)

    @staticmethod
    def import_fake (**kwargs):
        """Generate a number of fake users for testing."""
        from sqlalchemy.exc import IntegrityError
        import pandas as pd

        availability_df = pd.read_csv('./app/data/out/fake_volunteer_availabilities.csv')
        num_rows = len(availability_df)
        print(num_rows)
        for i in range(num_rows):
            row = availability_df.iloc[i]
            a = VolunteerAvailability(
                volunteer_id=int(row['volunteer_id']),
                day_of_week=row['day_of_week'],
                start_hour=int(row['start_hour']),
                end_hour=int(row['end_hour']),
                availability_status_id=int(row['availability_status_id']),
                **kwargs)
            print(a)
            db.session.add(a)
            try:
                db.session.commit()
                print("Committed " + str(i))
            except IntegrityError:
                db.session.rollback()
            

    def __repr__(self):
        return f"VolunteerAvailability('{self.day_of_week}: {self.start_hour} - {self.end_hour}')"


class AvailabilityStatus(db.Model):
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    name = db.Column(db.String(64), nullable=False)

    @staticmethod
    def insert_statuses():
        statuses = ['Available', 'Available for Backup']
        for s in statuses:
            availability_status = AvailabilityStatus.query.filter_by(
                name=s).first()
            if availability_status is None:
                availability_status = AvailabilityStatus(name=s)
            db.session.add(availability_status)
        db.session.commit()

    def __repr__(self):
        return f"AvailabilityStatus('[{self.id}] {self.name}')"



# For Vacation Calendar
class VolunteerVacationDay(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    volunteer_id = db.Column(db.Integer,
                             db.ForeignKey('volunteer.id'),
                             nullable=False)
    date = db.Column(db.Date, nullable=False)

    def __repr__(self):
        return f"VolunteerVacationDay('{self.date}')"

