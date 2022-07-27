from datetime import time

from sqlalchemy.sql.elements import Null
from .. import db


class Availability(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Availabilites
    availability_monday_start = db.Column(db.Time)
    availability_monday_end = db.Column(db.Time)
    backup_monday_start = db.Column(db.Time)
    backup_monday_end = db.Column(db.Time)
    availability_tuesday_start = db.Column(db.Time)
    availability_tuesday_end = db.Column(db.Time)
    backup_tuesday_start = db.Column(db.Time)
    backup_tuesday_end = db.Column(db.Time)
    availability_wednesday_start = db.Column(db.Time)
    availability_wednesday_end = db.Column(db.Time)
    backup_wednesday_start = db.Column(db.Time)
    backup_wednesday_end = db.Column(db.Time)
    availability_thursday_start = db.Column(db.Time)
    availability_thursday_end = db.Column(db.Time)
    backup_thursday_start = db.Column(db.Time)
    backup_thursday_end = db.Column(db.Time)
    availability_friday_start = db.Column(db.Time)
    availability_friday_end = db.Column(db.Time)
    backup_friday_start = db.Column(db.Time)
    backup_friday_end = db.Column(db.Time)
    availability_saturday_start = db.Column(db.Time)
    availability_saturday_end = db.Column(db.Time)
    backup_saturday_start = db.Column(db.Time)
    backup_saturday_end = db.Column(db.Time)
    availability_sunday_start = db.Column(db.Time)
    availability_sunday_end = db.Column(db.Time)
    backup_sunday_start = db.Column(db.Time)
    backup_sunday_end = db.Column(db.Time)

    @staticmethod
    def generate_fake(count=5, **kwargs):
        """Generate fake availability data for testing."""
        from sqlalchemy.exc import IntegrityError

        for i in range(count):
            a = Availability(**kwargs)
            db.session.add(a)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    def __repr__(self):
        (f"Availability('{self.id}')")
