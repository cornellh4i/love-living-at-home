from flask_wtf import FlaskForm
from wtforms import SelectMultipleField, ValidationError, widgets
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from wtforms.fields import (BooleanField, DateTimeField, IntegerField,
                            PasswordField, RadioField, SelectField, SelectMultipleField,
                            StringField, SubmitField, TextAreaField)
from wtforms.fields.html5 import DateField, EmailField, TimeField, IntegerField
from wtforms.validators import Email, EqualTo, InputRequired, Length, Optional, DataRequired

from app import db
from app.models import Role, User, ServiceCategory, Service, Staffer, RequestStatus, ContactLogPriorityType, Member
from datetime import date;


class ChangeUserEmailForm(FlaskForm):
    email = EmailField('New email',
                       validators=[InputRequired(),
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
    first_name = StringField('First name',
                             validators=[InputRequired(),
                                         Length(1, 64)])
    last_name = StringField('Last name',
                            validators=[InputRequired(),
                                        Length(1, 64)])
    email = EmailField('Email',
                       validators=[InputRequired(),
                                   Length(1, 64),
                                   Email()])
    submit = SubmitField('Invite')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')


class NewUserForm(InviteUserForm):
    password = PasswordField('Password',
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

    
class TransportationRequestForm(FlaskForm):
    categoryId = 0
    def selectedCategory():
        return db.session.query(ServiceCategory).order_by().filter(ServiceCategory.request_type_id == 0)

    def services():
        return db.session.query(Service).order_by()

    def stafferQuery():
        return db.session.query(Staffer).order_by()

    def statusQuery():
        return db.session.query(RequestStatus).order_by()

    def contactLogQuery():
        return db.session.query(ContactLogPriorityType).order_by()

    def specialInstructionsQuery():
         return db.session.query(Member).order_by()

    date_created = StringField('Date Created:', default = date.today,  render_kw={'readonly': True})
    requested_date = DateField('Requested Date',
                               validators=[InputRequired()],
                               format='%Y-%M-%D')
    initial_pickup = TimeField('Inital Pickup:', format='%H:%M')
    appointment = TimeField('Appointment:', format='%H:%M')
    return_pickup = TimeField('Return Pickup:', format='%H:%M')
    drop_off = TimeField('Drop Off:', format='%H:%M')
    time_flexible = RadioField('Is Date/Time Flexible?',
                               choices=[('Yes', 'Yes'), ('No', 'No')])
    priority = RadioField('High priority?',
                          choices=[('Yes', 'Yes'), ('No', 'No')])
    description = TextAreaField('Short description (included in email):')

    service_category = QuerySelectField(
        'Service Category:',
        validators=[InputRequired()],
        get_label='name',
        query_factory=selectedCategory)

    service =  QuerySelectField(
        'Service:',
        validators=[InputRequired()],
        get_label='name',
        query_factory=services)

    starting_location = StringField('Starting Location:')
    destination = StringField('Destination:')

    special_instructions = TextAreaField('Special Instructions:')
    follow_up_date = DateField('Follow Up Date:',
                               validators=[InputRequired()],
                               format='%Y-%M-%D')
    status =  QuerySelectField(
        'Status:',
        validators=[InputRequired()],
        get_label='name',
        query_factory=statusQuery)
    responsible_staffer = QuerySelectField(
        'Responsible Staffer:',
        validators=[InputRequired()],
        get_label='name',
        query_factory=stafferQuery)
    contact_log_priority = QuerySelectField(
        'Contact Log Priority:',
        validators=[InputRequired()],
        get_label='name',
        query_factory=contactLogQuery)
    person_to_cc = StringField('Person to Cc:',
     default = "Enter email address(es) separated by comma")

    submit = SubmitField('Save')
    cancel = SubmitField('Cancel')


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class MemberManager(FlaskForm):
    first_name = StringField('First name',
                             validators=[InputRequired(),
                                         Length(1, 64)])
    middle_initial = StringField('Middle Initial',
                                 validators=[Length(min=0, max=1)])
    last_name = StringField('Last name',
                            validators=[InputRequired(),
                                        Length(1, 64)])
    preferred_name = StringField(
        'Preferred Name', validators=[Optional(),
                                      Length(min=1, max=30)])
    salutations = [("none", ""), ("sir", "Sir"), ("mrs", "Mrs"), ("ms", "Ms"),
                   ("mr", "Mr")]
    salutation = SelectField("Salutation", choices=salutations)

    pronoun = StringField("Pronoun",
                          validators=[InputRequired(),
                                      Length(min=1, max=30)])

    countries = [('united_states', 'United States'), ('b', "B"), ('c', 'C')]
    states = [('none', ""), ("ny", "NY")]
    time_zones = [("est", "Eastern Time (US & Canada) (UTC-05:00)"),
                  ("b", "B"), ("c", "C")]
    metro_areas = [("none", "<SELECT>"), ("a", "A"), ("b", "B"), ("c", "C")]

    primary_country = SelectField('Country', choices=countries)
    primary_address1 = StringField('Address 1',
                                   validators=[Optional(),
                                               Length(max=200)])
    primary_address2 = StringField('Address 2',
                                   validators=[Optional(),
                                               Length(max=200)])
    primary_city = StringField('City',
                               validators=[Optional(),
                                           Length(max=200)])
    primary_state = SelectField('State', choices=states)
    primary_zip_code = StringField('Zip Code',
                                   validators=[Optional(),
                                               Length(max=45)])
    primary_time_zone = SelectField('Timezone',
                                    choices=time_zones,
                                    validators=[Optional()])
    primary_metro_area = SelectField('Metro Area',
                                     choices=metro_areas,
                                     validators=[Optional()])
    primary_phone = IntegerField('Phone Number',
                                 widget=widgets.Input(input_type="tel"),
                                 validators=[Optional()])

    secondary_as_primary_checkbox = BooleanField(
        'Use this address instead of the primary address',
        validators=[Optional()])
    secondary_country = SelectField('Country', choices=countries)
    secondary_address1 = StringField('Address 1',
                                     validators=[Optional(),
                                                 Length(max=200)])
    secondary_address2 = StringField('Address 2',
                                     validators=[Optional(),
                                                 Length(max=200)])
    secondary_city = StringField('City',
                                 validators=[Optional(),
                                             Length(max=200)])
    secondary_state = SelectField('State', choices=states)
    secondary_zip_code = TextAreaField('Zip Code',
                                       validators=[Optional(),
                                                   Length(max=45)])
    secondary_time_zone = SelectField('Timezone',
                                      choices=time_zones,
                                      validators=[Optional()])
    secondary_metro_area = SelectField('Metro Area',
                                       choices=metro_areas,
                                       validators=[Optional()])
    secondary_phone = IntegerField('Phone Number',
                                   widget=widgets.Input(input_type="tel"),
                                   validators=[Optional()])

    phone_number = IntegerField('Phone Number',
                                widget=widgets.Input(input_type="tel"),
                                validators=[Optional()])
    cell_number = IntegerField('Cell Phone Number',
                               widget=widgets.Input(input_type="tel"),
                               validators=[Optional()])
    email = EmailField('Email',
                       validators=[InputRequired(),
                                   Length(1, 64),
                                   Email()])

    emergency_contact_name = StringField(
        'Contact Name', validators=[InputRequired(),
                                    Length(1, 64)])
    emergency_contact_relationship = StringField(
        'Relationship', validators=[Optional(), Length(1, 64)])
    emergency_contact_phone_number = IntegerField(
        'Phone Number',
        widget=widgets.Input(input_type="tel"),
        validators=[Optional()])
    emergency_contact_email_address = EmailField(
        'Email', validators=[InputRequired(),
                             Length(1, 64),
                             Email()])

    volunteer_notes = TextAreaField('Notes for Volunteers',
                                    validators=[Optional(),
                                                Length(max=500)])

    staffer_notes = TextAreaField('Notes for Office Staff',
                                  validators=[Optional(),
                                              Length(max=500)])

    submit = SubmitField("Submit")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')


class VolunteerManager(FlaskForm):
    salutations = [("", ""), ("sir", "Sir"), ("mrs", "Mrs"), ("ms", "Ms"),
                   ("mr", "Mr")]
    salutation = SelectField("Salutation", choices=salutations)
    first_name = StringField(
        'First Name', validators=[InputRequired(),
                                  Length(min=1, max=30)])
    middle_initial = StringField('Middle Initial',
                                 validators=[Length(min=0, max=1)])
    last_name = StringField(
        'Last Name', validators=[InputRequired(),
                                 Length(min=1, max=30)])
    gender = SelectField("Gender",
                         validators=[InputRequired()],
                         choices=[("male", "Male"), ('female', "Female")])

    # make this a stringfield or select field?
    pronoun = StringField("Pronouns",
                          validators=[InputRequired(),
                                      Length(min=1, max=30)])
    preferred_name = StringField(
        'Preferred Name', validators=[Optional(),
                                      Length(min=1, max=30)])
    primary_address1 = StringField(
        'Address', validators=[InputRequired(),
                               Length(max=200)])

    # now under contact info
    home_phone = IntegerField(widget=widgets.Input(input_type="tel"),
                              validators=[InputRequired()])
    email = EmailField('Email',
                       validators=[InputRequired(),
                                   Length(1, 64),
                                   Email()])

    # What is another way to say Services willing to do
    files = [("alarm", "Alarm/Locks/Security"),
             ("bill", "Bill Paying/Paperwork"), ("auto", "Auto Repair"),
             ("remote", "Coronavirus Remote Assistance")]
    services = MultiCheckboxField('Services willing to do', choices=files)
    times = [("morning 8-11", "Morning 8-11"),
             ("morning 11-2", "Lunchtime 11-2"),
             ("afternoon 2-5", "Afternoon 2-5"),
             ("evening 5-8", "Evening 5-8"),
             ("night 8-midnight", "Night 8-Midnight")]
    availability_time = MultiCheckboxField('Availability Time', choices=times)
    days = [("monday", "Monday"), ("tuesday", "Tuesday"),
            ("wednesday", "Wednesday"), ("thursday", "Thursday"),
            ("friday", "Friday"), ("saturday", "Saturday"),
            ("sunday", "Sunday")]
    availability_day = MultiCheckboxField('Availability Day', choices=days)
    vettings = TextAreaField("Vettings", validators=[Optional()])

    # make a history of completed and pending services
    notes = TextAreaField("Notes for Office Staff", validators=[Optional()])

    submit = SubmitField("Submit")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    submit = SubmitField("Submit")


class ContractorManager(FlaskForm):
    organization_name = StringField(
        'Organization Name',
        validators=[InputRequired(), Length(min=1, max=30)])
    address = StringField('Address', validators=[Optional(), Length(max=200)])
    phone_number = IntegerField('Phone Number',
                                widget=widgets.Input(input_type="tel"),
                                validators=[Optional()])
    email = EmailField('Email',
                       validators=[InputRequired(),
                                   Length(1, 64),
                                   Email()])

    # Is there a better way to record availability in one variable
    times = [("morning 8-11", "Morning 8-11"),
             ("morning 11-2", "Lunchtime 11-2"),
             ("afternoon 2-5", "Afternoon 2-5"),
             ("evening 5-8", "Evening 5-8"),
             ("night 8-midnight", "Night 8-Midnight")]
    availability_time = MultiCheckboxField('Availability Time', choices=times)
    days = [("monday", "Monday"), ("tuesday", "Tuesday"),
            ("wednesday", "Wednesday"), ("thursday", "Thursday"),
            ("friday", "Friday"), ("saturday", "Saturday"),
            ("sunday", "Sunday")]
    availability_day = MultiCheckboxField('Availability Day', choices=days)
    reviews = TextAreaField('Reviews',
                            validators=[Optional(),
                                        Length(max=500)])

    submit = SubmitField("Submit")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')
