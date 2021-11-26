from .. import db


class Vacation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    v_id = db.Column(db.Integer,
                     db.ForeignKey('volunteer.id'),
                     nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)

    def __repr__(self):
        return (f"V('{self.id}')")
