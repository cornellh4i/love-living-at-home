from .. import db


class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), unique=True, nullable=False)
    category_id = db.Column(db.Integer,
                            db.ForeignKey('service_category.id'),
                            nullable=False)
    requests = db.relationship("Request", backref="service", lazy=True)
    provided_services = db.relationship("ProvidedService",
                                        backref="service",
                                        lazy=True)

    @staticmethod
    def get_services():
        import pandas as pd
        services = []
        services_df = pd.read_csv('./app/data/out/services.csv')
        for row in services_df.iterrows():
            service_id, service_name, category_id = row[1]
            services.append((service_id, service_name, category_id))
        return services

    @staticmethod
    def insert_services():
        services = Service.get_services()
        for i, s, c_i in services:
            service = Service.query.filter_by(name=s).first()
            if service is None:
                service = Service(id=i, name=s, category_id=c_i)
            db.session.add(service)
        db.session.commit()

    def __repr__(self):
        return f"Service( '{self.name}', '{self.category_id}')"
