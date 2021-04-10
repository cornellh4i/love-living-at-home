from flask_wtf import FlaskForm
from wtforms import ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.fields import (
    PasswordField,
    StringField,
    SubmitField,
    SelectField,
    SelectMultipleField,
    RadioField
)

from wtforms.fields.html5 import IntegerField
from wtforms.fields.html5 import EmailField
from wtforms.validators import (
    Email,
    EqualTo,
    InputRequired,
    Length,
    DataRequired
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


class SearchRequestForm(FlaskForm):

    request_type = SelectMultipleField('Request Type', choices = [ (0,'Transportation Request'), 
    (1,'Member\'s Home Request'), (2, 'Office Time Request')], validators = [DataRequired()])


    request_status = SelectMultipleField('Request Status', choices = 
    [(0, 'Requested'), (1, 'Confirmed'), (2, 'Completed'), (3, 'Cancelled')], validators = [DataRequired()])

    service_category = SelectMultipleField('Service Category', choices =
    [(0, 'COVID Community Support'), (1, 'Professional Home/Garden Service'),
    (2, 'Professional In-Home Support'), (3, 'Technical Support'), 
    (4, 'Transportation'), (5, 'Village Admin'), (6, 'Volunteer Home/Garden Service'),
    (7, 'Volunteer In-Home Support')], validators = [DataRequired()])

    provider_type = SelectMultipleField('Provider Type', choices = 
    [(0, 'Non-Member Volunteer'), (1, 'Member Volunteer'), (2, 'Contractor')], validators = [DataRequired()])

    requesting_member = SelectField('Requesting Member', choices = [(0, 'Nat Peuly'), (1, 'Sohni Uthra')], validators=[DataRequired()])

    service_provider = SelectField('Service Provider', choices = [(0, 'Nat Peuly'), (1, 'Sohni Uthra')], validators=[DataRequired()])

    # """service_req_from = IntegerField('Service Req # from', default=0)
    # service_req_to = IntegerField('to', default=0)

    # priority = RadioField('High priority', choices=['Yes', 'No', 'Both'])
    # show = RadioField('Show', choices=['Undated', 'Dated', 'Both'])

    # search = SubmitField('Search')
    # reset = SubmitField('Reset')"""