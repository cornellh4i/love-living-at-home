import os

from flask import render_template
from flask_mail import Message

from app import create_app, mail


def send_email(recipient, subject, template, cc, **kwargs):
    app = create_app(os.getenv('FLASK_CONFIG') or 'default')
    with app.app_context():
        msg = Message(app.config['EMAIL_SUBJECT_PREFIX'] + ' ' + subject,
                        cc= [] if cc=='' else [cc],
                      sender=app.config['EMAIL_SENDER'],
                      recipients=[recipient])
        msg.body = render_template(template + '.txt', **kwargs)
        msg.html = render_template(template + '.html', **kwargs)
        mail.send(msg)
