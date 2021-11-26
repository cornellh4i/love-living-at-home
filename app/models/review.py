from .. import db


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reviewer_name = db.Column(db.String(80), nullable=False)
    rating = db.Column(db.Integer)
    review_text = db.Column(db.Text)
    lr_id = db.Column(db.Integer,
                      db.ForeignKey('local_resource.id'),
                      nullable=False)
    date_created = db.Column(db.Date, nullable=False)

    def __repr__(self):
        return (f"Review('{self.id}')")
