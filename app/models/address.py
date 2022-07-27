from .. import db


class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    # The name of the person associated with the address
    name = db.Column(db.String(64))
    address1 = db.Column(db.String(64))
    address2 = db.Column(db.String(64))
    city = db.Column(db.String(64),)
    state = db.Column(db.String(64), default='New York')
    country = db.Column(db.String(64), default='United States')
    zipcode = db.Column(db.String(64))
    metro_area_id = db.Column(db.Integer, db.ForeignKey('metro_area.id'))

    @ staticmethod
    def get_addresses():
        import pandas as pd
        addresses = []
        addresses_df = pd.read_csv('./app/data/out/addresses.csv')
        for row in addresses_df.iterrows():
            addresses.append(dict(row[1]))
        return addresses

    @ staticmethod
    def insert_addresses():
        addresses = Address.get_addresses()
        for address_dict in addresses:
            address = Address.query.filter_by(
                id=address_dict['id']).first()
            if address is None:
                address_dict.pop('id', None)
                address = Address(**address_dict)
            db.session.add(address)
        db.session.commit()

    def __repr__(self):
        return (f"Address('{self.address1}',\
                         '{self.city}', '{self.state}', '{self.country}')")
