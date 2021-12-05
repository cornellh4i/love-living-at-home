from .. import db


class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    # The name of the person associated with the address
    name = db.Column(db.String(64), nullable=False)
    address1 = db.Column(db.String(64), nullable=False)
    address2 = db.Column(db.String(64))
    city = db.Column(db.String(64), nullable=False)
    state = db.Column(db.String(64), default='New York')
    country = db.Column(db.String(64), default='United States')
    zipcode = db.Column(db.String(64))
    metro_area_id = db.Column(db.Integer, db.ForeignKey('metro_area.id'))

    @staticmethod
    def generate_fake(count=200, **kwargs):
        """Generate a number of fake addresses for testing."""
        from sqlalchemy.exc import IntegrityError
        from random import seed, randint
        from faker import Faker

        fake = Faker()

        seed()
        for i in range(count):
            a = Address(name=fake.company(),
                        address1=fake.street_address(),
                        city=fake.city(),
                        metro_area_id=randint(1, 10),
                        **kwargs)
            db.session.add(a)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    def __repr__(self):
        return (f"Address('{self.address1}',\
                         '{self.city}', '{self.state}', '{self.country}')")
