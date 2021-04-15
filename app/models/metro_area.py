from .. import db


class MetroArea(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)

    def __repr__(self):
        return (f"Metro Area('{self.name}')")
