from .. import db


class LocalResource(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # General Information
    contact_salutation = db.Column(db.String(20))
    contact_first_name = db.Column(db.String(80))
    contact_middle_initial = db.Column(db.String(5))
    contact_last_name = db.Column(db.String(80))
    company_name = db.Column(db.String(80))

    # Location Information
    address_id = db.Column(db.Integer(), db.ForeignKey("address.id"))

    # Contact Information
    primary_phone_number = db.Column(db.String(80))
    secondary_phone_number = db.Column(db.String(80))
    email_address = db.Column(db.String(80))
    preferred_contact_method = db.Column(db.String(80))
    website = db.Column(db.String(80))

    # Availability information
    availability_id = db.Column(db.Integer(), db.ForeignKey("availability.id"))

    @ staticmethod
    def get_local_resources():
        import pandas as pd
        local_resources = []
        local_resources_df = pd.read_csv('./app/data/out/local_resources.csv')
        for row in local_resources_df.iterrows():
            local_resources.append(dict(row[1]))
        return local_resources

    @ staticmethod
    def insert_local_resources():
        local_resources = LocalResource.get_local_resources()
        for local_resource_dict in local_resources:
            local_resource = LocalResource.query.filter_by(
                id=local_resource_dict['id']).first()
            if local_resource is None:
                local_resource_dict.pop('id', None)
                local_resource = LocalResource(**local_resource_dict)
            db.session.add(local_resource)
        db.session.commit()

    def __repr__(self):
        return f"Local Resource('{self.company_name}')"
