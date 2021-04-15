from .. import db


class LocalResource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ## Representative Information
    contact_salutation = db.Column(db.String(20))
    contact_first_name = db.Column(db.String(80), nullable=False)
    contact_middle_initial = db.Column(db.String(5))
    contact_last_name = db.Column(db.String(80), nullable=False)
    organization_name = db.Column(db.String(80), nullable=False)
    ## Contact Information
    address_id = db.Column(db.Integer(),
                           db.ForeignKey("address.id"),
                           nullable=False)
    metro_area_id = db.Column(db.Integer, db.ForeignKey('metro_area.id'))

    phone_number = db.Column(db.String(10), nullable=False)
    email_address = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return f"Local Resource('{self.organization_name}')"