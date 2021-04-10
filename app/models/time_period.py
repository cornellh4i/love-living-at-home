from .. import db


class TimePeriod(db.Model):
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    name = db.Column(db.String(64), nullable=False)

    def __repr__(self):
        return f"TimePeriod('{self.name}')"
