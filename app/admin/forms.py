from flask_wtf import FlaskForm
from wtforms import ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.fields import (
    PasswordField,
    StringField,
    SubmitField,
    RadioField,
    SelectField,
    TextAreaField
)
from wtforms.fields.html5 import EmailField, DateField, TimeField
from wtforms.validators import (
    Email,
    EqualTo,
    InputRequired,
    Length,
)

from app import db
from app.models import Role, User


class ChangeUserEmailForm(FlaskForm):
    email = EmailField(
        'New email', validators=[InputRequired(),
                                 Length(1, 64),
                                 Email()])
    submit = SubmitField('Update email')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')


class ChangeAccountTypeForm(FlaskForm):
    role = QuerySelectField(
        'New account type',
        validators=[InputRequired()],
        get_label='name',
        query_factory=lambda: db.session.query(Role).order_by('permissions'))
    submit = SubmitField('Update role')


class InviteUserForm(FlaskForm):
    role = QuerySelectField(
        'Account type',
        validators=[InputRequired()],
        get_label='name',
        query_factory=lambda: db.session.query(Role).order_by('permissions'))
    first_name = StringField(
        'First name', validators=[InputRequired(),
                                  Length(1, 64)])
    last_name = StringField(
        'Last name', validators=[InputRequired(),
                                 Length(1, 64)])
    email = EmailField(
        'Email', validators=[InputRequired(),
                             Length(1, 64),
                             Email()])
    submit = SubmitField('Invite')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')


class NewUserForm(InviteUserForm):
    password = PasswordField(
        'Password',
        validators=[
            InputRequired(),
            EqualTo('password2', 'Passwords must match.')
        ])
    password2 = PasswordField('Confirm password', validators=[InputRequired()])

    submit = SubmitField('Create')


class TransportationRequestForm(FlaskForm):
    requested_date = DateField('Requested Date',
        validators=[InputRequired()], format='%Y-%M-%D')
    initial_pickup = TimeField('Inital Pickup', format='%H:%M')
    appointment = TimeField('Appointment', format='%H:%M')
    return_pickup = TimeField('Return Pickup', format='%H:%M')
    drop_off = TimeField('Drop Off', format='%H:%M')
    time_flexible = RadioField('Is Date/Time Flexible?', choices=[('Yes',''),('No','')])
    priority =RadioField('High priority?', choices=[('Yes',''),('No','')])
    description=TextAreaField('Short description')
    service_category = SelectField('Service Category', choices = [('Yes',''),('No','')])
    service = SelectField('Service', choices = [('Yes',''),('No','')])
    starting_location = StringField('Starting Location')
    destination = StringField('Destination')

    submit = SubmitField('Save')
    cancel = SubmitField('Cancel')
