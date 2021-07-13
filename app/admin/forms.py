from datetime import date

from flask_wtf import FlaskForm
from wtforms import SelectMultipleField, ValidationError, widgets
from wtforms.ext.sqlalchemy.fields import (QuerySelectField,
                                           QuerySelectMultipleField)
from wtforms.fields import (BooleanField, IntegerField, PasswordField,
                            RadioField, SelectField, SelectMultipleField,
                            StringField, SubmitField, TextAreaField)
from wtforms.fields.html5 import DateField, EmailField, IntegerField, TimeField
from wtforms.validators import (DataRequired, Email, EqualTo, InputRequired,
                                Length, Optional)

from app import db
from app.models import (Address, ContactLogPriorityType, Member,
                        RequestDurationType, RequestStatus, RequestType, Role,
                        Service, ServiceCategory, Staffer, User, VolunteerType)

salutations = [("none", ""), ("sir", "Sir"), ("mrs", "Mrs"), ("ms", "Ms"),
               ("mr", "Mr")]
genders = [("female", "Female"), ("male", "Male"),
           ("unspecified", "Unspecified"),
           ("no_answer", "Does not wish to answer")]

countries = [('united_states', 'United States'), ('b', "B"), ('c', 'C')]
states = [("ny", "NY")]
time_zones = [("est", "Eastern Time (US & Canada) (UTC-05:00)"), ("b", "B"),
              ("c", "C")]
metro_areas = [("none", "<SELECT>"), ("a", "A"), ("b", "B"), ("c", "C")]


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
    request_type = SelectMultipleField('Request Type')
    request_status = SelectMultipleField('Request Status')
    service_category = SelectMultipleField('Service Category')
    requesting_member = SelectMultipleField('Requesting Member(s)')
    volunteer = SelectMultipleField('Volunteer(s)')
    local_resource = SelectMultipleField('Local Resource(s)')

    volunteer_type = QuerySelectMultipleField(
        'Volunteer Type',
        get_label='name',
        query_factory=lambda: db.session.query(VolunteerType).order_by('name'))

    show = RadioField('Show',
                      choices=[(0, 'Undated'), (1, 'Dated'), (2, 'Both')])

    time_period = SelectField('Time Period',
                              choices=[(0, 'Today'), (1, 'This Week'),
                                       (2, 'This Month'), (3, 'Future Dates')])

    start_date = DateField('Start Date',
                           format='%Y-%M-%D')
    end_date = DateField('End Date',
                         format='%Y-%M-%D')

    apply_filters = SubmitField('Apply Filters')

    # reset_filters = SubmitField('Reset Filters')

    def get_status(id):
        for i in range(len(request_status.choices)):
            if id == request_status.choices[i][0]:
                return request_status.choices[i][1]


class TransportationRequestForm(FlaskForm):
    categoryId = 0

    def selectedCategory():
        return db.session.query(ServiceCategory).order_by().filter(
            ServiceCategory.request_type_id == 0)

    def covid_services():
        return db.session.query(Service).order_by().filter(
            Service.category_id == 1)

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
        
    service_provider = SelectMultipleField(
        'Service Provider',
        id='service_provider',
        validators=[InputRequired()], coerce=int)

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
                               choices=[(True, 'Yes'), (False, 'No')],
                               coerce=lambda x: x == 'True')
    description = TextAreaField('Short description (included in email):')

    service_category = QuerySelectField(
        'Service Category:',
        render_kw={'onchange': "serviceChoices()"},
        validators=[InputRequired()],
        get_label='name',
        query_factory=selectedCategory)

    covid_service = QuerySelectField(
        'Service:',
        id="covid_service",
        render_kw={'onchange': "serviceChoices()"},
        validators=[Optional()],
        get_label='name',
        query_factory=covid_services)

    transportation_service = QuerySelectField(
        'Service:',
        render_kw={'onchange': "serviceChoices()"},
        id="transportation_service",
        validators=[Optional()],
        get_label='name',
        query_factory=transportation_services)

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


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class MemberManager(FlaskForm):
    first_name = StringField('First Name',
                             validators=[InputRequired(),
                                         Length(1, 64)])
    middle_initial = StringField('Middle Initial',
                                 validators=[Length(min=0, max=1)])
    last_name = StringField('Last Name',
                            validators=[InputRequired(),
                                        Length(1, 64)])
    preferred_name = StringField(
        'Preferred Name', validators=[Optional(),
                                      Length(min=1, max=30)])

    salutation = SelectField("Salutation", choices=salutations)

    birthdate = DateField("Birthdate", validators=[InputRequired()])

    gender = SelectField("Gender",
                         choices=genders,
                         validators=[InputRequired()])

    primary_country = StringField('Country', default="United States")

    # One Address object:
    primary_address1 = StringField(
        'Street address or P.O. Box',
        validators=[InputRequired(), Length(max=200)])
    primary_address2 = StringField('Apt, suite, unit, building, floor, etc.',
                                   validators=[Optional(),
                                               Length(max=200)])
    primary_city = StringField('City',
                               validators=[InputRequired(),
                                           Length(max=200)])
    primary_state = SelectField('State', choices=states)
    primary_zip_code = StringField('Zip Code',
                                   validators=[Optional(),
                                               Length(max=45)])
    primary_metro_area = SelectField('Metro Area',
                                     choices=metro_areas,
                                     validators=[Optional()])

    secondary_as_primary_checkbox = BooleanField(
        'Use this address instead of the primary address',
        validators=[Optional()])
    secondary_country = StringField('Country', default="United States")
    secondary_address1 = StringField('Street address or P.O. Box',
                                     validators=[Optional(),
                                                 Length(max=200)])
    secondary_address2 = StringField('Apt, suite, unit, building, floor, etc.',
                                     validators=[Optional(),
                                                 Length(max=200)])
    secondary_city = StringField('City',
                                 validators=[Optional(),
                                             Length(max=200)])
    secondary_state = SelectField('State', choices=states)
    secondary_zip_code = StringField('Zip Code',
                                     validators=[Optional(),
                                                 Length(max=45)])
    secondary_metro_area = SelectField('Metro Area',
                                       choices=metro_areas,
                                       validators=[Optional()])

    # Contact Information
    primary_phone_number = StringField('Primary Phone Number',
                                       widget=widgets.Input(input_type="tel"),
                                       validators=[InputRequired()])
    secondary_phone_number = StringField(
        'Secondary Phone Number',
        widget=widgets.Input(input_type="tel"),
        validators=[Optional()])
    email = EmailField('Email',
                       validators=[Optional(),
                                   Length(1, 64),
                                   Email()])
    preferred_contact_method = RadioField('Preferred Contact Method *',
                                          choices=[('phone', 'Phone'),
                                                   ('email', 'Email'),
                                                   ('phone and email',
                                                    'Phone and Email')])

    # Emergency Contact Information
    emergency_contact_name = StringField(
        'Contact Name', validators=[Optional(), Length(1, 64)])
    emergency_contact_relationship = StringField(
        'Relationship to Member', validators=[Optional(),
                                              Length(1, 64)])
    emergency_contact_phone_number = IntegerField(
        'Phone Number of Contact',
        widget=widgets.Input(input_type="tel"),
        validators=[Optional()])
    emergency_contact_email_address = EmailField(
        'Email Address of Contact',
        validators=[Optional(), Length(1, 64),
                    Email()])

    membership_expiration_date = DateField("Member Expiration Date: ",
                                           validators=[InputRequired()])
    member_number = IntegerField(validators=[InputRequired()])
    volunteer_notes = TextAreaField('Notes for Volunteers',
                                    validators=[Optional(),
                                                Length(max=500)])

    staffer_notes = TextAreaField('Notes for Office Staff',
                                  validators=[Optional(),
                                              Length(max=500)])

    submit = SubmitField("Submit")


class VolunteerManager(FlaskForm):
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
                         choices=[("male", "Male"), ('female', "Female"),
                                  ("unspecified", "Unspecified"),
                                  ("no_answer", "Do not wish to answer")])

    birthdate = DateField("Birthdate ", validators=[InputRequired()])
    # make this a stringfield or select field?
    preferred_name = StringField(
        'Preferred Name', validators=[Optional(),
                                      Length(min=1, max=30)])
    # address
    primary_address1 = StringField(
        'Street address or P.O. Box',
        validators=[InputRequired(), Length(max=200)])
    primary_address2 = StringField('Apt, suite, unit, building, floor, etc.',
                                   validators=[Optional(),
                                               Length(max=200)])
    primary_city = StringField('City',
                               validators=[InputRequired(),
                                           Length(max=200)])
    primary_state = StringField('State',
                                validators=[InputRequired(),
                                            Length(max=200)])
    primary_zip_code = StringField('Zip Code',
                                   validators=[Optional(),
                                               Length(max=45)])
    # emergency contact
    emergency_contact_name = StringField(
        'Contact Name', validators=[Optional(), Length(1, 64)])
    emergency_contact_relationship = StringField(
        'Relationship', validators=[Optional(), Length(1, 64)])
    emergency_contact_phone_number = StringField(
        'Phone Number',
        widget=widgets.Input(input_type="tel"),
        validators=[Optional()])
    emergency_contact_email_address = EmailField(
        'Email', validators=[Optional(), Length(1, 64),
                             Email()])
    # now under contact info
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
    preferred_contact_method = RadioField('Preferred Contact Method',
                                          choices=[('phone', "Phone"),
                                                   ('email', "Email"),
                                                   ('phone and email',
                                                    "Phone and Email")])

    notes = TextAreaField("Notes for Office Staff", validators=[Optional()])

    submit = SubmitField("Submit")


class AddServiceVetting(FlaskForm):
    vetting_notes = TextAreaField("",
                                  render_kw={
                                      "rows": 15,
                                      "cols": 105
                                  },
                                  validators=[Optional()])
    volunteer_fully_vetted_checkbox = BooleanField('Is Fully Vetted?',
                                                   validators=[Optional()])
    submit = SubmitField("Save")


class ContractorManager(FlaskForm):
    first_name = StringField('First name',
                             validators=[InputRequired(),
                                         Length(1, 64)])
    middle_initial = StringField('Middle Initial',
                                 validators=[Length(min=0, max=1)])
    last_name = StringField('Last name',
                            validators=[InputRequired(),
                                        Length(1, 64)])
    salutations = [("none", ""), ("sir", "Sir"), ("mrs", "Mrs"), ("ms", "Ms"),
                   ("mr", "Mr")]
    salutation = SelectField("Salutation", choices=salutations)
    company_name = StringField('Company',
                               validators=[Optional(),
                                           Length(min=1, max=30)])

    countries = [('united_states', 'United States'), ('b', "B"), ('c', 'C')]
    states = [('none', ""), ("ny", "NY")]
    time_zones = [("est", "Eastern Time (US & Canada) (UTC-05:00)"),
                  ("b", "B"), ("c", "C")]
    metro_areas = [("none", "<SELECT>"), ("a", "A"), ("b", "B"), ("c", "C")]

    primary_country = SelectField('Country', choices=countries)
    primary_address1 = StringField('Street address or P.O. Box',
                                   validators=[Optional(),
                                               Length(max=200)])
    primary_address2 = StringField('Apt, suite, unit, building, floor, etc.',
                                   validators=[Optional(),
                                               Length(max=200)])
    primary_city = StringField('City',
                               validators=[Optional(),
                                           Length(max=200)])
    primary_state = SelectField('State', choices=states)
    primary_zip_code = StringField('Zip Code',
                                   validators=[Optional(),
                                               Length(max=45)])
    primary_metro_area = SelectField('Metro Area',
                                     choices=metro_areas,
                                     validators=[Optional()])
    primary_phone_number = IntegerField('Primary Phone Number',
                                        widget=widgets.Input(input_type="tel"),
                                        validators=[InputRequired()])
    secondary_phone_number = IntegerField(
        'Secondary Phone Number',
        widget=widgets.Input(input_type="tel"),
        validators=[Optional()])
    email = EmailField('Email',
                       validators=[Optional(),
                                   Length(1, 64),
                                   Email()])

    preferred_contact_method = RadioField(
        choices=[('phone',
                  'Phone'), ('email',
                             'Email'), ('phone_and_email', 'Phone and Email')])

    website = StringField('Website',
                          validators=[Optional(),
                                      Length(min=1, max=30)])
    submit = SubmitField("Submit")


class Reviews(FlaskForm):
    reviewer_name = StringField(
        'Name of Reviewer',
        validators=[InputRequired(), Length(min=1, max=30)])
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=500)])
    submit = SubmitField("Save")


class AddAvailability(FlaskForm):
    availability_times = [
        ("7 am", "7 am"), ("8 am", "8 am"), ("9 am", "9 am"),
        ("10 am", "10 am"), ("11 am", "11 am"), ("12 pm", "12 pm"),
        ("1 pm", "1 pm"), ("2 pm", "2 pm"), ("3 pm", "3 pm"), ("4 pm", "4 pm"),
        ("5 pm", "5 pm"), ("6 pm", "6 pm"), ("7-8 am", "7-8 am"),
        ("7-9 am", "7-9 am"), ("7-10 am", "7-10 am"), ("7-11 am", "7-11 am"),
        ("7 am-12 pm", "7 am-12 pm"), ("7 am-1 pm", "7 am-1 pm"),
        ("7 am-2 pm", "7 am-2 pm"), ("7 am-3 pm", "7 am-3 pm"),
        ("7 am-4 pm", "7 am-4 pm"), ("7 am-5 pm", "7 am-5 pm"),
        ("7 am-6 pm", "7 am-6 pm"), ("8-9 am", "8-9 am"),
        ("8-10 am", "8-10 am"), ("8-11 am", "8-11 am"),
        ("8 am-12 pm", "8 am-12 pm"), ("8 am-1 pm", "8 am-1 pm"),
        ("8 am-2 pm", "8 am-2 pm"), ("8 am-3 pm", "8 am-3 pm"),
        ("8 am-4 pm", "8 am-4 pm"), ("8 am-5 pm", "8 am-5 pm"),
        ("8 am-6 pm", "8 am-6 pm"), ("9-10 am", "9-10 am"),
        ("9-11 am", "9-11 am"), ("9 am-12 pm", "9 am-12 pm"),
        ("9 am-1 pm", "9 am-1 pm"), ("9 am-2 pm", "9 am-2 pm"),
        ("9 am-3 pm", "9 am-3 pm"), ("9 am-4 pm", "9 am-4 pm"),
        ("9 am-5 pm", "9 am-5 pm"), ("9 am-6 pm", "9 am-6 pm"),
        ("10-11 am", "10-11 am"), ("10 am-12 pm", "10 am-12 pm"),
        ("10 am-1 pm", "10 am-1 pm"), ("10 am-2 pm", "10 am-2 pm"),
        ("10 am-3 pm", "10 am-3 pm"), ("10 am-4 pm", "10 am-4 pm"),
        ("10 am-5 pm", "10 am-5 pm"), ("10 am-6 pm", "10 am-6 pm"),
        ("11 am-12 pm", "11 am-12 pm"), ("11 am-1 pm", "11 am-1 pm"),
        ("11 am-2 pm", "11 am-2 pm"), ("11 am-3 pm", "11 am-3 pm"),
        ("11 am-4 pm", "11 am-4 pm"), ("11 am-5 pm", "11 am-5 pm"),
        ("11 am-6 pm", "11 am-6 pm"), ("12-1 pm", "12-1 pm"),
        ("12-2 pm", "12-2 pm"), ("12-3 pm", "12-3 pm"), ("12-4 pm", "12-4 pm"),
        ("12-5 pm", "12-5 pm"), ("12-6 pm", "12-6 pm"), ("1-2 pm", "1-2 pm"),
        ("1-3 pm", "1-3 pm"), ("1-4 pm", "1-4 pm"), ("1-5 pm", "1-5 pm"),
        ("1-6 pm", "1-6 pm"), ("2-3 pm", "2-3 pm"), ("2-4 pm", "2-4 pm"),
        ("2-5 pm", "2-5 pm"), ("2-6 pm", "2-6 pm"), ("3-4 pm", "3-4 pm"),
        ("3-5 pm", "3-5 pm"), ("3-6 pm", "3-6 pm"), ("4-5 pm", "4-5 pm"),
        ("4-6 pm", "4-6 pm"), ("5-6 pm", "5-6 pm")
    ]
    availability_monday = SelectMultipleField('', choices=availability_times)
    backup_monday = SelectMultipleField('', choices=availability_times)
    availability_tuesday = SelectMultipleField('', choices=availability_times)
    backup_tuesday = SelectMultipleField('', choices=availability_times)
    availability_wednesday = SelectMultipleField('',
                                                 choices=availability_times)
    backup_wednesday = SelectMultipleField('', choices=availability_times)
    availability_thursday = SelectMultipleField('', choices=availability_times)
    backup_thursday = SelectMultipleField('', choices=availability_times)
    availability_friday = SelectMultipleField('', choices=availability_times)
    backup_friday = SelectMultipleField('', choices=availability_times)
    availability_saturday = SelectMultipleField('', choices=availability_times)
    backup_saturday = SelectMultipleField('', choices=availability_times)
    availability_sunday = SelectMultipleField('', choices=availability_times)
    backup_sunday = SelectMultipleField('', choices=availability_times)
    submit = SubmitField("Save")


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


class EditMetroAreaForm(FlaskForm):
    name = StringField('Metro Area Name',
                       validators=[InputRequired(),
                                   Length(1, 200)])
    submit = SubmitField('Save Metro Area Information')


class AddServiceToVolunteer(FlaskForm):
    submit = SubmitField('Save')
