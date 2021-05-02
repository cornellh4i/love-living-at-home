from .. import db


class LocalResource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ## Representative Information
    contact_salutation = db.Column(db.String(20))
    contact_first_name = db.Column(db.String(80), nullable=False)
    contact_middle_initial = db.Column(db.String(5))
    contact_last_name = db.Column(db.String(80), nullable=False)
    company_name = db.Column(db.String(80))
    ## Location Information
    address_id = db.Column(db.Integer(),
                           db.ForeignKey("address.id"))
    metro_area_id = db.Column(db.Integer, db.ForeignKey('metro_area.id'))
    ## Contact Information
    primary_phone_number = db.Column(db.String(10), nullable=False)
    secondary_phone_number = db.Column(db.String(10))
    email_address = db.Column(db.String(80))
    preferred_contact_method=db.Column(db.String(80))
    website = db.Column(db.String(80))
    reviews_received = db.relationship('Review', backref='local_resource', lazy='dynamic')

    def __repr__(self):
        return f"Local Resource('{self.organization_name}')"