from .. import db


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Float)
    review_text = db.Column(db.Text)
    local_resource_id = db.Column(db.Integer,
                                  db.ForeignKey('local_resource.id'),
                                  nullable=False)
    member_id = db.Column(db.Integer,
                          db.ForeignKey('member.id'),
                          nullable=False)
    date_created = db.Column(db.Date, nullable=False)

    def __repr__(self):
        return (f"Review('{self.name}')")
