from flask import current_app

from .. import db


class ServiceCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), unique=True, nullable=False)
    request_type_id = db.Column(db.Integer,
                                db.ForeignKey("request_type.id"),
                                nullable=False)
    services = db.relationship("Service",
                               backref="category",
                               lazy=True)
    requests = db.relationship("Request",
                               backref="category",
                               lazy=True)

    @staticmethod
    def get_categories():
        import pandas as pd
        categories = []
        categories_df = pd.read_csv('./app/data/out/service_categories.csv')
        for row in categories_df.iterrows():
            category_id, category_name, request_type_id = row[1]
            categories.append((category_id, category_name, request_type_id))
        return categories

    @staticmethod
    def insert_categories():
        categories = ServiceCategory.get_categories()
        for i, c, r_i in categories:
            category = ServiceCategory.query.filter_by(name=c).first()
            if category is None:
                category = ServiceCategory(id=i, name=c, request_type_id=r_i)
            db.session.add(category)
        db.session.commit()

    def __repr__(self):
        return f"Service Category('{self.name}')"
