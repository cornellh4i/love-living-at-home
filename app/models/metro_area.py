from .. import db


class MetroArea(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)

    @staticmethod
    def get_metro_areas():
        import pandas as pd
        metro_areas = []
        metro_areas_df = pd.read_csv('./app/data/out/metro_areas.csv')
        for row in metro_areas_df.iterrows():
            metro_area_id, metro_area_name = row[1]
            metro_areas.append((metro_area_id, metro_area_name))
        return metro_areas

    @staticmethod
    def insert_metro_areas():
        metro_areas = MetroArea.get_metro_areas()
        for i, ma in metro_areas:
            metro_area = MetroArea.query.filter_by(name=ma).first()
            if metro_area is None:
                metro_area = MetroArea(id=i, name=ma)
            db.session.add(metro_area)
        db.session.commit()

    def __repr__(self):
        return (f"Metro Area('{self.name}')")
