from math import isnan

from .. import db


class Volunteer(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # General Information
    salutation = db.Column(db.String(20))
    first_name = db.Column(db.String(80), nullable=False)
    middle_initial = db.Column(db.String(5))
    last_name = db.Column(db.String(80), nullable=False)
    preferred_name = db.Column(db.String(80))
    gender = db.Column(db.String(80))
    birthdate = db.Column(db.Date)

    # Member ID infomration for member volunteers
    member_id = db.Column(db.Integer(), db.ForeignKey("member.id"))

    # Location Information
    primary_address_id = db.Column(db.Integer(), db.ForeignKey("address.id"))
    secondary_address_id = db.Column(db.Integer(), db.ForeignKey("address.id"))

    # Concat Information
    primary_phone_number = db.Column(db.String(64))
    secondary_phone_number = db.Column(db.String(10))
    email_address = db.Column(db.String(80))
    preferred_contact_method = db.Column(db.String(80), nullable=False)

    # Emergency Contact Information
    emergency_contact_name = db.Column(db.String(64))
    emergency_contact_phone_number = db.Column(db.String(64))
    emergency_contact_email_address = db.Column(db.String(64))
    emergency_contact_relationship = db.Column(db.String(64))

    # Volunteer-Specific Information
    is_member_volunteer = db.Column(db.Boolean(), nullable=False, default=False)
    is_fully_vetted = db.Column(db.Boolean(), nullable=False, default=False)
    vetting_notes = db.Column(db.Text, default="")
    availability_id = db.Column(db.Integer(), db.ForeignKey("availability.id"))

    general_notes = db.Column(db.String(255))

    @staticmethod
    def get_volunteers():
        import pandas as pd

        volunteers = []
        volunteer_df = pd.read_csv("./app/data/out/volunteers.csv")
        for row in volunteer_df.iterrows():
            volunteers.append(dict(row[1]))
        return volunteers

    @staticmethod
    def insert_volunteers():
        volunteers = Volunteer.get_volunteers()
        for volunteer_dict in volunteers:
            for key in volunteer_dict:
                try:
                    if isnan(volunteer_dict[key]):
                        volunteer_dict[key] = None
                except:
                    pass
            volunteer = Volunteer.query.filter_by(id=volunteer_dict["id"]).first()
            if volunteer is None:
                volunteer_dict.pop("id", None)
                volunteer = Volunteer(**volunteer_dict)
            db.session.add(volunteer)
        db.session.commit()

    def __repr__(self):
        return f"Volunteer('{self.first_name} {self.last_name}')"
