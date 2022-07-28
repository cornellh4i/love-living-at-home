#!/usr/bin/env python
import os
import subprocess

from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Server, Shell
from redis import Redis
from rq import Connection, Queue, Worker

from app import create_app, db
from app.models import *
from config import Config
from manage_helper import *

app = create_app(os.getenv("FLASK_CONFIG") or "default")
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)


manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command("db", MigrateCommand)
manager.add_command("runserver", Server(host="0.0.0.0"))


@manager.command
def test():
    """Run the unit tests."""
    import unittest

    tests = unittest.TestLoader().discover("tests")
    unittest.TextTestRunner(verbosity=2).run(tests)


@manager.command
def recreate_db():
    """
    Recreates a local database. You probably should not use this on
    production.
    """
    drop_everything(db)
    db.drop_all()
    db.create_all()
    db.session.commit()


@manager.command
def setup_dev():
    """Runs the set-up needed for local development."""
    setup_general()


@manager.command
def setup_prod():
    """Runs the set-up needed for production."""
    setup_general()


def setup_general():
    """Runs the set-up needed for both local development and production.
    Also sets up first admin user."""
    Role.insert_roles()
    # Request related
    RequestDurationType.insert_types()
    RequestStatus.insert_statuses()
    RequestType.insert_types()
    ContactLogPriorityType.insert_types()
    ServiceCategory.insert_categories()
    CancellationReason.insert_reasons()
    # Volunteer - Request
    RequestVolunteerStatus.insert_statuses()
    # Service related
    Service.insert_services()
    MetroArea.insert_metro_areas()
    Member.insert_members()
    Availability.generate_fake(count=159)
    LocalResource.insert_local_resources()
    Volunteer.insert_volunteers()
    Address.insert_addresses()

    # Set up first admin user
    admin_query = Role.query.filter_by(name="Administrator")
    if admin_query.first() is not None:
        if User.query.filter_by(email=Config.ADMIN_EMAIL).first() is None:
            user = User(
                first_name="Admin",
                last_name="Account",
                password=Config.ADMIN_PASSWORD,
                confirmed=True,
                email=Config.ADMIN_EMAIL,
            )
            db.session.add(user)
            db.session.commit()
            print("Added administrator {}".format(user.full_name()))


@manager.command
def run_worker():
    """Initializes a slim rq task queue."""
    listen = ["default"]
    conn = Redis(
        host=app.config["RQ_DEFAULT_HOST"],
        port=app.config["RQ_DEFAULT_PORT"],
        db=0,
        password=app.config["RQ_DEFAULT_PASSWORD"],
    )

    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()


@manager.command
def format():
    """Runs the yapf and isort formatters over the project."""
    isort = "isort -rc *.py app/"
    yapf = "yapf -r -i *.py app/"

    print("Running {}".format(isort))
    subprocess.call(isort, shell=True)

    print("Running {}".format(yapf))
    subprocess.call(yapf, shell=True)


if __name__ == "__main__":
    manager.run()
