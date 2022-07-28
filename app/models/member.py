from math import isnan

from .. import db


class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # General Information
    salutation = db.Column(db.String(20))
    first_name = db.Column(db.String(64), nullable=False)
    middle_initial = db.Column(db.String(5))
    last_name = db.Column(db.String(64), nullable=False)
    preferred_name = db.Column(db.String(64))
    gender = db.Column(db.String(64), nullable=False)
    birthdate = db.Column(db.Date)

    # Volunteer ID infomration for member volunteers
    volunteer_id = db.Column(db.Integer(), db.ForeignKey("volunteer.id"))

    # Membership Information
    member_number = db.Column(db.Integer)
    membership_expiration_date = db.Column(db.Date)

    # Location Information
    primary_address_id = db.Column(db.Integer, db.ForeignKey("address.id"))
    secondary_address_id = db.Column(db.Integer, db.ForeignKey("address.id"))

    # Contact Information
    primary_phone_number = db.Column(db.String(80))
    secondary_phone_number = db.Column(db.String(80))
    email_address = db.Column(db.String(64))
    preferred_contact_method = db.Column(db.String(80))

    # Emergency Contact Information
    emergency_contact_name = db.Column(db.String(64))
    emergency_contact_phone_number = db.Column(db.String(64))
    emergency_contact_email_address = db.Column(db.String(64))
    emergency_contact_relationship = db.Column(db.String(64))

    # Service Notes
    # Notes about this member that volunteers can see.
    volunteer_notes = db.Column(db.Text)
    # Notes about this member that only the staffers can see.
    staffer_notes = db.Column(db.Text)

    @staticmethod
    def get_members():
        import pandas as pd

        members = []
        members_df = pd.read_csv("./app/data/out/members.csv")
        for row in members_df.iterrows():
            members.append(dict(row[1]))
        return members

    @staticmethod
    def insert_members():
        members = Member.get_members()
        for member_dict in members:
            for key in member_dict:
                try:
                    if isnan(member_dict[key]):
                        member_dict[key] = None
                except:
                    pass
            member = Member.query.filter_by(id=member_dict["id"]).first()
            if member is None:
                member_dict.pop("id", None)
                member = Member(**member_dict)
            db.session.add(member)
        db.session.commit()

    def __repr__(self):
        return f"Member('{self.member_number}')"
