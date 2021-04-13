from .. import db


class ProvidedService(db.Model):
    """
    Represents a single service provided by a single volunteer.
    """
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer,
                           db.ForeignKey('service.id'),
                           nullable=False)
    volunteer_id = db.Column(db.Integer,
                             db.ForeignKey('volunteer.id'),
                             nullable=False)

    def __repr__(self):
        return f"ProvidedService('{self.volunteer_status}')"
