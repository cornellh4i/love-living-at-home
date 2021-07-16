from .. import db

class Availability(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ## Availabilites
    availability_monday = db.Column(db.String(64))
    backup_monday = db.Column(db.String(64), default='Unavailable')
    availability_tuesday = db.Column(db.String(64))
    backup_tuesday = db.Column(db.String(64))
    availability_wednesday = db.Column(db.String(64))
    backup_wednesday = db.Column(db.String(64))
    availability_thursday = db.Column(db.String(64))
    backup_thursday = db.Column(db.String(64))
    availability_friday = db.Column(db.String(64))
    backup_friday = db.Column(db.String(64))
    availability_saturday = db.Column(db.String(64))
    backup_saturday = db.Column(db.String(64))
    availability_sunday = db.Column(db.String(64))
    backup_sunday = db.Column(db.String(64))

    @staticmethod
    def generate_fake (count=5, **kwargs):
        """Generate fake availability data for testing."""
        from sqlalchemy.exc import IntegrityError

        for i in range(count):
            a = Availability(
                availability_monday = "7am-6pm",
                availability_tuesday = "7am-6pm",
                availability_friday = "7am-6pm",
                availability_sunday = "7am-6pm",
                **kwargs)
            db.session.add(a)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    def __repr__(self):
        (f"Availability('{self.id}')")

