from datetime import date

from flask_wtf import FlaskForm
from wtforms import SelectMultipleField, ValidationError, widgets
from wtforms.ext.sqlalchemy.fields import (QuerySelectField,
                                           QuerySelectMultipleField)
from wtforms.fields import (BooleanField, IntegerField, PasswordField,
                            RadioField, SelectField, SelectMultipleField,
                            StringField, SubmitField, TextAreaField)
from wtforms.fields.html5 import DateField, EmailField, IntegerField, TimeField
from wtforms.validators import (Email, EqualTo, InputRequired,
                                Length, Optional, NumberRange)

from app import db
from app.models import (MetroArea, ContactLogPriorityType, Member, RequestStatus, RequestType, Role,
                        Service, ServiceCategory, Staffer, User, VolunteerType)

salutations = [("none", ""), ("sir", "Sir"), ("mrs", "Mrs"), ("ms", "Ms"),
               ("mr", "Mr")]
genders = [("female", "Female"), ("male", "Male"),
           ("unspecified", "Unspecified"),
           ("no_answer", "Does not wish to answer")]
time_zones = [("est", "Eastern Time (US & Canada) (UTC-05:00)"), ("b", "B"),
              ("c", "C")]
contact_methods = [('phone', "Phone"), ('email', "Email"), ('phone and email',
                                                            "Phone and Email")]


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


class GeneratePdfForm(FlaskForm):
    report_type = SelectField(
        'Report Type', coerce=int,
        choices=[(0, 'Completed Volunteer Services by Service Category')], validators=[InputRequired()])
    file_name = StringField('Report File Name', validators=[InputRequired()])
    submit = SubmitField('Run Report')


class SearchRequestForm(FlaskForm):
    request_type = SelectMultipleField('Request Type')
    request_status = SelectMultipleField('Request Status')
    service_category = SelectMultipleField('Service Category')
    requesting_member = SelectMultipleField('Requesting Member(s)')
    volunteer = SelectMultipleField('Volunteer(s)')
    local_resource = SelectMultipleField('Local Resource(s)')
    dated_filter = SelectMultipleField('Show...')
    volunteer_type = QuerySelectMultipleField(
        'Volunteer Type',
        get_label='name',
        query_factory=lambda: db.session.query(VolunteerType).order_by('name'))

    date_type = RadioField('Date Type:',
                           choices=[(0, 'Service Date'), (1, 'Created Date')],
                           default='0')
    time_period = SelectField('Time Period',
                              choices=[(0, 'Today'), (1, 'This Week'),
                                       (2, 'This Month'), (3, 'Future Dates')])

    start_date = DateField('Start Date', format='%Y-%M-%D')
    end_date = DateField('End Date', format='%Y-%M-%D')

    request_number = StringField('Request #')

    apply_filters = SubmitField('Apply Filters')

    # reset_filters = SubmitField('Reset Filters')


class TransportationRequestForm(FlaskForm):
    def selectedCategory():
        return db.session.query(ServiceCategory).order_by().filter(
            ServiceCategory.request_type_id == 0)

    def transportation_services():
        return db.session.query(Service).order_by().filter(
            Service.category_id == 0)

    def stafferQuery():
        return db.session.query(Staffer).order_by()

    def statusQuery():
        return db.session.query(RequestStatus).order_by()

    def contactLogQuery():
        return db.session.query(ContactLogPriorityType).order_by()

    def specialInstructionsQuery():
        return db.session.query(Member).order_by()

    special_instructions_list = {}

    date_created = DateField('Date Created:',
                             default=date.today,
                             render_kw={'readonly': True})

    requesting_member = SelectMultipleField(
        'Requesting Member',
        render_kw={'onchange': "specialInstructions()"},
        id='member',
        validators=[InputRequired()],
        coerce=int)

    service_provider = SelectMultipleField('Service Provider',
                                           id='service_provider',
                                           validators=[InputRequired()],
                                           coerce=int)

    requested_date = DateField('Requested Date', validators=[InputRequired()])
    initial_pickup = TimeField('Inital Pickup:',
                               format='%H:%M',
                               validators=[InputRequired()])
    appointment = TimeField('Appointment:',
                            format='%H:%M',
                            validators=[InputRequired()])
    return_pickup = TimeField('Return Pickup:', format='%H:%M')
    drop_off = TimeField('Drop Off:', format='%H:%M')
    time_flexible = RadioField('Is Date/Time Flexible?',
                               choices=[(1, 'Yes'), (0, 'No')],
                               coerce=int)
    description = TextAreaField('Short description (included in email):')

    service_category = SelectField(
        'Service Category:',
        render_kw={'onchange': "serviceChoices()"},
        validators=[InputRequired()], coerce = int
    )

    transportation_service = SelectField(
        'Service:',
        id="services",
        validators=[Optional()], coerce = int)

    starting_location = StringField('Pickup Location:',
                                    validators=[InputRequired()])

    special_instructions = TextAreaField('Special Instructions:',
                                         id="special-instructions-text")

    follow_up_date = DateField('Follow Up Date:')
    status = QuerySelectField('Status:',
                              validators=[InputRequired()],
                              get_label='name',
                              query_factory=statusQuery)

    responsible_staffer = SelectField('Responsible Staffer:', coerce=int)

    contact_log_priority = QuerySelectField('Contact Log Priority:',
                                            validators=[InputRequired()],
                                            get_label='name',
                                            query_factory=contactLogQuery)

    person_to_cc = EmailField('Person to cc',
                              validators=[Length(0, 64),
                                          Optional()])
    destination = SelectField('Destination:',
                              validators=[InputRequired()],
                              coerce=int)
    duration = RadioField('Duration:', coerce=int)

    destination_name = StringField('Destination Name:')
    street_address1 = StringField('Street Address:')
    street_address2 = StringField('Apt, Unit, Building, Floor, etc:')
    city = StringField('City:')
    state = StringField('State/Province:')
    zip = StringField('Zip:')
    country = StringField('Country:')
    add_address = SubmitField('Add Address')

    submit = SubmitField("Submit")


class OfficeTimeRequestForm(FlaskForm):
    def selectedCategory():
        return db.session.query(ServiceCategory).order_by().filter(
            ServiceCategory.request_type_id == 1)

    def office_time_services():
        return db.session.query(Service).order_by().filter(
            Service.category_id == 6)

    def stafferQuery():
        return db.session.query(Staffer).order_by()

    def statusQuery():
        return db.session.query(RequestStatus).order_by()

    def contactLogQuery():
        return db.session.query(ContactLogPriorityType).order_by()

    def specialInstructionsQuery():
        return db.session.query(Member).order_by()

    special_instructions_list = {}

    date_created = DateField('Date Created:',
                             default=date.today,
                             render_kw={'readonly': True})
    requesting_member = SelectMultipleField(
        'Requesting Member',
        render_kw={'onchange': "specialInstructions()"},
        id='member',
        validators=[InputRequired()],
        coerce=int)

    service_provider = SelectMultipleField('Service Provider',
                                           id='service_provider',
                                           validators=[InputRequired()],
                                           coerce=int)

    requested_date = DateField('Date Requested', validators=[InputRequired()])
    start_time = TimeField('From:',
                           format='%H:%M',
                           validators=[InputRequired()])
    end_time = TimeField('Until:', format='%H:%M')
    high_priority = RadioField('Is high priority?',
                               choices=[(1, 'Yes'), (0, 'No')],
                               coerce=int)
    # add alerts
    description = TextAreaField('Short description (included in email):')

    service_category = SelectField(
        'Service Category:',
        render_kw={'onchange': "serviceChoices()"},
        validators=[InputRequired()], coerce=int)

    office_time_service = SelectField(
        'Service:',
        id="services",
        validators=[Optional()],
        coerce=int)

    special_instructions = TextAreaField('Special Instructions:',
                                         id="special-instructions-text")

    responsible_staffer = SelectField('Responsible Staffer:', coerce=int)

    status = QuerySelectField('Status:',
                              validators=[InputRequired()],
                              get_label='name',
                              query_factory=statusQuery)

    contact_log_priority = QuerySelectField('Contact Log Priority:',
                                            validators=[InputRequired()],
                                            get_label='name',
                                            query_factory=contactLogQuery)

    person_to_cc = TextAreaField('Person to cc',
                                 validators=[Length(0, 64),
                                             Optional()])

    submit = SubmitField("Submit")


class MembersHomeRequestForm(FlaskForm):

    def selectedCategory():
        return db.session.query(ServiceCategory).order_by().filter(
            ServiceCategory.request_type_id == 2)

    def covid_services():
        return db.session.query(Service).order_by().filter(
            Service.category_id == 1)

    def tech_service():
        return db.session.query(Service).order_by().filter(
            Service.category_id == 3)

    def prof_home():
        return db.session.query(Service).order_by().filter(
            Service.category_id == 4)

    def prof_support():
        return db.session.query(Service).order_by().filter(
            Service.category_id == 5)

    def vol_home():
        return db.session.query(Service).order_by().filter(
            Service.category_id == 7)

    def vol_support():
        return db.session.query(Service).order_by().filter(
            Service.category_id == 8)

    def stafferQuery():
        return db.session.query(Staffer).order_by()

    def statusQuery():
        return db.session.query(RequestStatus).order_by()

    def contactLogQuery():
        return db.session.query(ContactLogPriorityType).order_by()

    def specialInstructionsQuery():
        return db.session.query(Member).order_by()

    special_instructions_list = {}
    category_id = 2

    date_created = DateField('Date Created:',
                             default=date.today,
                             render_kw={'readonly': True})

    requesting_member = SelectMultipleField(
        'Requesting Member',
        render_kw={'onchange': "specialInstructions()"},
        id='member',
        validators=[InputRequired()],
        coerce=int)

    service_provider = SelectMultipleField('Service Provider',
                                           id='service_provider',
                                           validators=[InputRequired()],
                                           coerce=int)

    requested_date = DateField('Requested Date', validators=[InputRequired()])

    time_from = TimeField('From:',
                          format='%H:%M',
                          validators=[InputRequired()])

    time_until = TimeField('Until:',
                           format='%H:%M',
                           validators=[InputRequired()])

    time_flexible = RadioField('Is Date/Time Flexible?',
                               choices=[(1, 'Yes'), (0, 'No')],
                               coerce=int)

    description = TextAreaField('Short description (included in email):')

    service_category = SelectField(
        'Service Category:',
        render_kw={'onchange': "serviceChoices()"},
        validators=[InputRequired()],
        coerce=int)

    member_home_service = SelectField(
        'Service:',
        id="services",
        validators=[Optional()],
        coerce=int)

    home_location = SelectMultipleField(
        'Location',
        id='home_location',
        validators=[InputRequired()],
        coerce=int)

    special_instructions = TextAreaField('Special Instructions:',
                                         id="special-instructions-text")

    follow_up_date = DateField('Follow Up Date:')
    status = QuerySelectField('Status:',
                              validators=[InputRequired()],
                              get_label='name',
                              query_factory=statusQuery)

    responsible_staffer = SelectField('Responsible Staffer:', coerce=int)

    contact_log_priority = QuerySelectField('Contact Log Priority:',
                                            validators=[InputRequired()],
                                            get_label='name',
                                            query_factory=contactLogQuery)

    person_to_cc = EmailField('Person to cc',
                              validators=[Length(0, 64),
                                          Optional()])

    submit = SubmitField("Submit")


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class MemberManager(FlaskForm):
    # General Information
    first_name = StringField('First Name', validators=[
                             InputRequired(), Length(1, 64)])

    middle_initial = StringField('Middle Initial',
                                 validators=[Optional(), Length(min=0, max=1)])

    last_name = StringField('Last Name', validators=[InputRequired(),
                                                     Length(1, 64)])

    preferred_name = StringField('Preferred Name', validators=[Optional(),
                                                               Length(min=1, max=30)])

    member_number = IntegerField(validators=[InputRequired()])

    membership_expiration_date = DateField("Member Expiration Date: ",
                                           validators=[InputRequired()])

    salutation = SelectField("Salutation", choices=salutations)

    birthdate = DateField("Birthdate", validators=[InputRequired()])

    gender = SelectField("Gender", choices=genders,
                         validators=[InputRequired()])

    # Primary Address Information
    primary_address1 = StringField('Street address or P.O. Box',
                                   validators=[InputRequired(), Length(max=200)])

    primary_address2 = StringField('Apt, suite, unit, building, floor, etc.',
                                   validators=[Optional(), Length(max=200)])

    primary_city = StringField('City', validators=[InputRequired(),
                                                   Length(max=200)])

    primary_state = StringField(
        'State', validators=[InputRequired(), Length(max=200)], default='New York')

    primary_country = StringField('Country', validators=[
                                  InputRequired(), Length(max=200)], default='United States')

    primary_zip_code = StringField('Zip Code', validators=[
                                   InputRequired(), Length(max=45)])

    primary_metro_area = QuerySelectField('Metro Area',
                                          validators=[Optional()], allow_blank=True, get_label='name',
                                          query_factory=lambda: db.session.query(MetroArea).order_by('name'))

    # Secondary Address Information
    secondary_as_primary_checkbox = BooleanField(
        'Use this address instead of the primary address',
        validators=[Optional()])

    secondary_address1 = StringField('Street address or P.O. Box',
                                     validators=[Optional(), Length(max=200)])

    secondary_address2 = StringField('Apt, suite, unit, building, floor, etc.',
                                     validators=[Optional(), Length(max=200)])

    secondary_city = StringField('City', validators=[Optional(),
                                                     Length(max=200)])

    secondary_state = StringField('State', validators=[Optional(),
                                                       Length(max=200)])

    secondary_country = StringField('Country', validators=[Optional(),
                                                           Length(max=200)])

    secondary_zip_code = StringField('Zip Code', validators=[Optional(),
                                                             Length(max=45)])

    secondary_metro_area = QuerySelectField('Metro Area',
                                            validators=[Optional()], allow_blank=True, get_label='name',
                                            query_factory=lambda: db.session.query(MetroArea).order_by('name'))

    # Contact Information
    primary_phone_number = StringField('Primary Phone Number',
                                       widget=widgets.Input(input_type="tel"),
                                       validators=[InputRequired()])

    secondary_phone_number = StringField('Secondary Phone Number',
                                         widget=widgets.Input(input_type="tel"), validators=[Optional()])

    email_address = EmailField('Email', validators=[Optional(),
                                                    Length(1, 64), Email()])

    preferred_contact_method = RadioField('Preferred Contact Method *',
                                          choices=contact_methods)

    # Emergency Contact Information
    emergency_contact_name = StringField(
        'Contact Name', validators=[Optional(), Length(1, 64)])

    emergency_contact_relationship = StringField(
        'Relationship to Member', validators=[Optional(), Length(1, 64)])

    emergency_contact_phone_number = IntegerField('Phone Number of Contact',
                                                  widget=widgets.Input(input_type="tel"), validators=[Optional()])

    emergency_contact_email_address = EmailField(
        'Email Address of Contact', validators=[Optional(), Length(1, 64), Email()])

    # Member Notes
    volunteer_notes = TextAreaField('Notes for Volunteers',
                                    validators=[Optional(), Length(max=500)])

    staffer_notes = TextAreaField('Notes for Office Staff',
                                  validators=[Optional(), Length(max=500)])

    submit = SubmitField("Submit")


class VolunteerManager(FlaskForm):
    # General Information
    first_name = StringField(
        'First Name', validators=[InputRequired(),
                                  Length(min=1, max=30)])

    middle_initial = StringField('Middle Initial',
                                 validators=[Optional(), Length(min=0, max=1)])

    last_name = StringField('Last Name', validators=[InputRequired(),
                                                     Length(min=1, max=30)])

    preferred_name = StringField('Preferred Name', validators=[Optional(),
                                                               Length(min=1, max=30)])

    salutation = SelectField("Salutation", choices=salutations)

    gender = SelectField("Gender", choices=genders,
                         validators=[InputRequired()])

    birthdate = DateField("Birthdate ", validators=[InputRequired()])

    # Primary Address Information
    primary_address1 = StringField('Street address or P.O. Box',
                                   validators=[InputRequired(), Length(max=200)])

    primary_address2 = StringField('Apt, suite, unit, building, floor, etc.',
                                   validators=[Optional(), Length(max=200)])

    primary_city = StringField('City',
                               validators=[InputRequired(),
                                           Length(max=200)])

    primary_state = StringField('State',
                                validators=[InputRequired(),
                                            Length(max=200)], default='New York')

    primary_country = StringField('Country',
                                  validators=[InputRequired(),
                                              Length(max=200)], default='United States')

    primary_zip_code = StringField('Zip Code',
                                   validators=[InputRequired(),
                                               Length(max=45)])

    primary_metro_area = QuerySelectField('Metro Area',
                                          validators=[Optional()], allow_blank=True, get_label='name',
                                          query_factory=lambda: db.session.query(MetroArea).order_by('name'))

    # Secondary Address Information
    secondary_as_primary_checkbox = BooleanField(
        'Use this address instead of the primary address',
        validators=[Optional()])

    secondary_address1 = StringField('Street address or P.O. Box',
                                     validators=[Optional(),
                                                 Length(max=200)])

    secondary_address2 = StringField('Apt, suite, unit, building, floor, etc.',
                                     validators=[Optional(),
                                                 Length(max=200)])

    secondary_city = StringField('City',
                                 validators=[Optional(),
                                             Length(max=200)])

    secondary_state = StringField('State',
                                  validators=[Optional(),
                                              Length(max=200)])

    secondary_country = StringField('Country',
                                    validators=[Optional(),
                                                Length(max=200)])

    secondary_zip_code = StringField('Zip Code',
                                     validators=[Optional(),
                                                 Length(max=45)])

    secondary_metro_area = QuerySelectField('Metro Area',
                                            validators=[Optional()], allow_blank=True, get_label='name',
                                            query_factory=lambda: db.session.query(MetroArea).order_by('name'))

    # Contact Information
    primary_phone_number = StringField("Primary Phone Number",
                                       widget=widgets.Input(input_type="tel"),
                                       validators=[InputRequired()])
    secondary_phone_number = StringField(
        "Secondary Phone Number",
        widget=widgets.Input(input_type="tel"),
        validators=[Optional()])

    email_address = EmailField('Email',
                               validators=[Optional(),
                                           Length(1, 64),
                                           Email()])

    preferred_contact_method = RadioField('Preferred Contact Method *',
                                          choices=contact_methods)

    # Emergency Contact Information
    emergency_contact_name = StringField(
        'Contact Name', validators=[Optional(), Length(1, 64)])

    emergency_contact_relationship = StringField(
        'Relationship to Volunteer', validators=[Optional(), Length(1, 64)])

    emergency_contact_phone_number = StringField(
        'Phone Number of Contact',
        widget=widgets.Input(input_type="tel"),
        validators=[Optional()])

    emergency_contact_email_address = EmailField(
        'Email Address of Contact', validators=[Optional(), Length(1, 64),
                                                Email()])

    # Additional Information
    general_notes = TextAreaField("General Notes", validators=[Optional()])

    submit = SubmitField("Submit")


class LocalResourceManager(FlaskForm):
    # General Information
    first_name = StringField('First name',
                             validators=[InputRequired(),
                                         Length(1, 64)])

    middle_initial = StringField('Middle Initial',
                                 validators=[Optional(), Length(min=0, max=1)])

    last_name = StringField('Last name',
                            validators=[InputRequired(),
                                        Length(1, 64)])

    salutation = SelectField('Salutation', choices=salutations)

    company_name = StringField('Company', validators=[InputRequired(),
                                                      Length(min=1, max=64)])

    # Address Information
    primary_address1 = StringField('Street address or P.O. Box',
                                   validators=[InputRequired(), Length(max=200)])

    primary_address2 = StringField('Apt, suite, unit, building, floor, etc.',
                                   validators=[Optional(), Length(max=200)])

    primary_city = StringField('City', validators=[InputRequired(),
                                                   Length(max=200)])

    primary_state = StringField('State', validators=[InputRequired(),
                                                     Length(max=200)], default='New York')

    primary_country = StringField('Country', validators=[InputRequired(),
                                                         Length(max=200)], default='United States')

    primary_zip_code = StringField('Zip Code', validators=[InputRequired(),
                                                           Length(max=45)])

    primary_metro_area = QuerySelectField('Metro Area',
                                          validators=[Optional()], allow_blank=True, get_label='name',
                                          query_factory=lambda: db.session.query(MetroArea).order_by('name'))

    # Contact Information
    primary_phone_number = IntegerField('Primary Phone Number',
                                        widget=widgets.Input(input_type="tel"),
                                        validators=[InputRequired()])

    secondary_phone_number = IntegerField('Secondary Phone Number',
                                          widget=widgets.Input(input_type="tel"), validators=[Optional()])

    email_address = EmailField('Email', validators=[Optional(),
                                                    Length(1, 64), Email()])

    preferred_contact_method = RadioField('Preferred Contact Method *',
                                          choices=contact_methods)

    website = StringField('Website',
                          validators=[Optional(),
                                      Length(min=1, max=80)])
    submit = SubmitField("Submit")


class AddAvailability(FlaskForm):
    availability_times = [("Unavailable", "Unavailable"),
                          ("7am-8am", "7am-8am"), ("7am-9am", "7am-9am"),
                          ("7am-10am", "7am-10am"), ("7am-11am", "7am-11am"),
                          ("7am-12pm", "7am-12pm"), ("7am-1pm", "7am-1pm"),
                          ("7am-2pm", "7am-2pm"), ("7am-3pm", "7am-3pm"),
                          ("7am-4pm", "7am-4pm"), ("7am-5pm", "7am-5pm"),
                          ("7am-6pm", "7am-6pm"), ("8am-9am", "8am-9am"),
                          ("8am-10am", "8am-10am"), ("8am-11am", "8am-11am"),
                          ("8am-12pm", "8am-12pm"), ("8am-1pm", "8am-1pm"),
                          ("8am-2pm", "8am-2pm"), ("8am-3pm", "8am-3pm"),
                          ("8am-4pm", "8am-4pm"), ("8am-5pm", "8am-5pm"),
                          ("8am-6pm", "8am-6pm"), ("9am-10am", "9am-10am"),
                          ("9am-11am", "9am-11am"), ("9am-12pm", "9am-12pm"),
                          ("9am-1pm", "9am-1pm"), ("9am-2pm", "9am-2pm"),
                          ("9am-3pm", "9am-3pm"), ("9am-4pm", "9am-4pm"),
                          ("9am-5pm", "9am-5pm"), ("9am-6pm", "9am-6pm"),
                          ("10am-11am", "10am-11am"),
                          ("10am-12pm", "10am-12pm"), ("10am-1pm", "10am-1pm"),
                          ("10am-2pm", "10am-2pm"), ("10am-3pm", "10am-3pm"),
                          ("10am-4pm", "10am-4pm"), ("10am-5pm", "10am-5pm"),
                          ("10am-6pm", "10am-6pm"), ("11am-12pm", "11am-12pm"),
                          ("11am-1pm", "11am-1pm"), ("11am-2pm", "11am-2pm"),
                          ("11am-3pm", "11am-3pm"), ("11am-4pm", "11am-4pm"),
                          ("11am-5pm", "11am-5pm"), ("11am-6pm", "11am-6pm"),
                          ("12pm-1pm", "12pm-1pm"), ("12pm-2pm", "12pm-2pm"),
                          ("12pm-3pm", "12pm-3pm"), ("12pm-4pm", "12pm-4pm"),
                          ("12pm-5pm", "12pm-5pm"), ("12pm-6pm", "12pm-6pm"),
                          ("1pm-2pm", "1pm-2pm"), ("1pm-3pm", "1pm-3pm"),
                          ("1pm-4pm", "1pm-4pm"), ("1pm-5pm", "1pm-5pm"),
                          ("1pm-6pm", "1pm-6pm"), ("2pm-3pm", "2pm-3pm"),
                          ("2pm-4pm", "2pm-4pm"), ("2pm-5pm", "2pm-5pm"),
                          ("2pm-6pm", "2pm-6pm"), ("3pm-4pm", "3pm-4pm"),
                          ("3pm-5pm", "3pm-5pm"), ("3pm-6pm", "3pm-6pm"),
                          ("4pm-5pm", "4pm-5pm"), ("4pm-6pm", "4pm-6pm"),
                          ("5pm-6pm", "5pm-6pm")]
    availability_identity = TextAreaField()
    availability_monday = SelectField('', choices=availability_times)
    backup_monday = SelectField('', choices=availability_times)
    availability_tuesday = SelectField('', choices=availability_times)
    backup_tuesday = SelectField('', choices=availability_times)
    availability_wednesday = SelectField('', choices=availability_times)
    backup_wednesday = SelectField('', choices=availability_times)
    availability_thursday = SelectField('', choices=availability_times)
    backup_thursday = SelectField('', choices=availability_times)
    availability_friday = SelectField('', choices=availability_times)
    backup_friday = SelectField('', choices=availability_times)
    availability_saturday = SelectField('', choices=availability_times)
    backup_saturday = SelectField('', choices=availability_times)
    availability_sunday = SelectField('', choices=availability_times)
    backup_sunday = SelectField('', choices=availability_times)
    submit = SubmitField("Save")


class AddVetting(FlaskForm):
    vetting_identity = TextAreaField()
    is_fully_vetted = BooleanField('Is Fully Vetted?',
                                   validators=[Optional()])
    vetting_notes = TextAreaField(
        "", render_kw={"rows": 15, "cols": 105}, validators=[Optional()])
    submit = SubmitField("Save")


class EditServicesVolunteerCanProvide(FlaskForm):
    provided_services = MultiCheckboxField(
        'Services Volunteer can Provide', coerce=int)
    submit = SubmitField("Save")


class AddReview(FlaskForm):
    review_identity = TextAreaField()
    reviewer_name = StringField(
        'Name of Reviewer',
        validators=[InputRequired(), Length(min=1, max=30)])
    rating = IntegerField(validators=[Optional()])
    review_text = TextAreaField('Review Text', validators=[
                                Optional(), Length(max=1000)])
    date_created = DateField(
        'Date Created', default=date.today)
    submit = SubmitField('Save')


class AddVacation(FlaskForm):
    vacation_identity = TextAreaField()
    start_date = DateField('Start Date')
    end_date = DateField('End Date')
    submit = SubmitField('Set As Not Available')


class EditServiceForm(FlaskForm):
    name = StringField('Service Name',
                       validators=[InputRequired(),
                                   Length(1, 200)])
    category = QuerySelectField('Category Name',
                                validators=[InputRequired()],
                                get_label='name',
                                query_factory=lambda: db.session.query(
                                    ServiceCategory).order_by('name'))
    submit = SubmitField('Save Service Information')


class EditServiceCategoryForm(FlaskForm):
    name = StringField('Service Category Name', validators=[
                       InputRequired(), Length(1, 200)])
    request_type = QuerySelectField('Request Type', validators=[InputRequired(
    )], get_label='name', query_factory=lambda: db.session.query(RequestType).order_by('name'))
    submit = SubmitField('Save Service Category Information')


class EditMetroAreaForm(FlaskForm):
    name = StringField('Metro Area Name',
                       validators=[InputRequired(),
                                   Length(1, 200)])
    submit = SubmitField('Save Metro Area Information')


class EditDestinationAddressForm(FlaskForm):
    name = StringField('Destination Address Name',
                       validators=[InputRequired(),
                                   Length(1, 200)])
    address1 = StringField('Street address or P.O. Box',
                           validators=[InputRequired(),
                                       Length(max=200)])

    address2 = StringField('Apt, suite, unit, building, floor, etc.',
                           validators=[Optional(),
                                       Length(max=200)])
    city = StringField('City',
                       validators=[InputRequired(),
                                   Length(max=200)])
    state = StringField('State',
                        validators=[InputRequired(),
                                    Length(max=200)])
    country = StringField('Country', default="United States")
    zip_code = StringField('Zip Code',
                           validators=[Optional(),
                                       Length(max=45)])
    submit = SubmitField('Save Destination Address Information')


class CompleteServiceRequestForm(FlaskForm):
    rating = IntegerField('Rating', validators=[Optional()])
    member_comments = TextAreaField('Member Comments', id="member_comments",
                                    validators=[Optional(),
                                                Length(max=1000)])
    provider_comments = TextAreaField('Provider Comments', id="provider_comments",
                                      validators=[Optional(), Length(max=1000)])
    duration_hours = IntegerField(
        '', validators=[Optional(), NumberRange(min=0, max=99)])
    duration_minutes = IntegerField(
        '', validators=[Optional(), NumberRange(min=0, max=99)])
    number_of_trips = IntegerField('# of Trips', validators=[
                                   Optional(), NumberRange(min=0)])
    mileage = IntegerField('Mileage', validators=[
                           Optional(), NumberRange(min=0)])
    expenses = IntegerField('Expenses ($)', validators=[
                            Optional(), NumberRange(min=0)])
    verified_by = SelectField('Verified by', coerce=int)
    submit = SubmitField('Save')
