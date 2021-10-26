from .. import db


class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    # A name for the address (i.e., 'Wegmans Food Market')
    name = db.Column(db.String(64), nullable=False)
    address1 = db.Column(db.String(64), nullable=False)
    address2 = db.Column(db.String(64))
    city = db.Column(db.String(64), nullable=False)
    state = db.Column(db.String(64), default='New York')
    country = db.Column(db.String(64), default='United States')
    zipcode = db.Column(db.String(64))
    # metro_area = db.Column(db.String(64))

    @staticmethod
    def generate_fake(count=200, **kwargs):
        """Generate a number of fake addresses for testing."""
        from sqlalchemy.exc import IntegrityError
        from random import seed, choice, random
        from faker import Faker
        from datetime import datetime

        fake = Faker()

        seed()
        for i in range(count):
            a = Address(name=fake.company(),
                        address1=fake.street_address(),
                        city=fake.city(),
                        **kwargs)
            db.session.add(a)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    def __repr__(self):
        return (f"Address('{self.street_address}',\
                         '{self.city}', '{self.state}', '{self.country}')")
