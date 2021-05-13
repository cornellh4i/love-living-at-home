from flask_wtf import FlaskForm
from wtforms import SelectMultipleField, ValidationError, widgets
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField

from wtforms.fields import (BooleanField, IntegerField,
                            PasswordField, RadioField, SelectField, SelectMultipleField,
                            StringField, SubmitField, TextAreaField)
from wtforms.fields.html5 import DateField, EmailField, TimeField, IntegerField
from wtforms.validators import Email, EqualTo, InputRequired, Length, Optional, DataRequired

from app import db
from app.models import Role, User, ServiceCategory, Service, Staffer, RequestStatus, ContactLogPriorityType, Member, Address, RequestDurationType
from datetime import date

serviceCategories = [('Select', 'Select'),
                     ('Coronavirus Community Support',
                      'Coronavirus Community Support'),
                     ('Transportation', 'Transportation')]

covidServices = [('Select', 'Select'), ('General Errands', 'General Errands'),
                 ('Grocery Shopping', 'Grocery Shopping'),
                 ('Prescription Pickup', 'Prescription Pickup')]

transportationServices = [
    ('Select', 'Select'), ('Event Carpool', 'Event Carpool'),
    ('hack4impact test service', 'hack4impact test service'),
    ('Long Dist Non-Med Professional', 'Long Dist Non-Med Professional'),
    ('Long Dist. Med Professional', 'Long Dist Med Professional'),
    ('Vol Driver Family/Friend Visit', 'Vol Driver Family/Friend Visit'),
    ('Vol Driver LLH Programs/Events', 'Vol Driver LLH Programs/Events'),
    ('Vol Driver Local Medical Appt', 'Vol Driver Local Medical Appt'),
    ('Vol Driver Shopping/Errands', 'Vol Driver Shopping/Errands'),
    ('Vol Driver Local Bus/Airport', 'Vol Driver Local Bus/Airport'),
    ('Vol Driver Misc. Trip', 'Vol Driver Misc. Trip')
]

request_duration_type = []
# db.session.query(RequestDurationType).order_by('id')
# request_duration_type = [(t.name, t.name) for t in ]


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
    request_type = SelectMultipleField('Request Type', choices=[(-1, 'Select All'), (0, 'Transportation Request'),
                                                                (1, 'Member\'s Home Request'), (2, 'Office Time Request')], validators=[DataRequired()])

    request_status = SelectMultipleField('Request Status', choices=[(0, 'Requested'), (
        1, 'Confirmed'), (2, 'Completed'), (3, 'Cancelled')], validators=[DataRequired()])

    request_status = SelectMultipleField('Request Status', choices=[
                                         (-1, 'Select All'), (0, 'Requested'), (1, 'Confirmed'), (2, 'Completed'), (3, 'Cancelled')], validators=[DataRequired()])

    service_category = SelectMultipleField('Service Category', choices=[(-1, 'Select All'), (0, 'COVID Community Support'), (1, 'Professional Home/Garden Service'),
                                                                        (2, 'Professional In-Home Support'), (3, 'Technical Support'),
                                                                        (4, 'Transportation'), (5, 'Village Admin'), (6,
                                                                                                                      'Volunteer Home/Garden Service'),
                                                                        (7, 'Volunteer In-Home Support')], validators=[DataRequired()])

    provider_type = SelectMultipleField('Provider Type', choices=[
                                        (-1, 'Select All'), (0, 'Non-Member Volunteer'), (1, 'Member Volunteer'), (2, 'Contractor')], validators=[DataRequired()])

    requesting_member = SelectField('Requesting Member', choices=[(0, 'Nat Peuly'), (1, 'Sohni Uthra'), (2, 'Angela Jin'),
                                                                  (3, 'Alina Kim')], validators=[DataRequired()])

    service_provider = SelectField('Service Provider', choices=[(0, 'Nat Peuly'), (1, 'Sohni Uthra'), (2, 'Angela Jin'),
                                                                (3, 'Alina Kim')], validators=[DataRequired()])

    # """service_req_from = IntegerField('Service Req # from', default=0)
    # service_req_to = IntegerField('to', default=0)

    # priority = RadioField('High priority', choices=['Yes', 'No', 'Both'])
    show = RadioField('Show', choices=[(0, 'Undated'), (1, 'Dated')])

    time_period = SelectField('Time Period', choices=[(0, 'Today'), (1, 'This Week'), (
        2, 'This Month'), (3, 'Future Dates')], validators=[DataRequired()])

    start_date = DateField('Start Date', validators=[
                           InputRequired()], format='%Y-%M-%D')
    end_date = DateField('End Date', validators=[
                         InputRequired()], format='%Y-%M-%D')

    apply_filters = SubmitField('Apply Filters')
    reset_filters = SubmitField('Reset Filters')


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

    date_created = DateField('Date Created:', default=date.today,
                             render_kw={'readonly': True})
    requesting_member = QuerySelectMultipleField(
        'Requesting Member',
        validators=[InputRequired()],
        get_label='first_name',
        query_factory=lambda: db.session.query(Member).order_by('first_name'))
    requested_date = DateField('Requested Date',
                               validators=[InputRequired()])
    initial_pickup = TimeField('Inital Pickup:', format='%H:%M',
                               validators=[InputRequired()])
    appointment = TimeField('Appointment:', format='%H:%M',
                            validators=[InputRequired()])
    return_pickup = TimeField('Return Pickup:', format='%H:%M')
    drop_off = TimeField('Drop Off:', format='%H:%M')
    time_flexible = RadioField('Is Date/Time Flexible?',
                               choices=[('Yes', 'Yes'), ('No', 'No')])
    description = TextAreaField('Short description (included in email):')

    service_category = QuerySelectField(
        'Service Category:',
        validators=[InputRequired()],
        get_label='name',
        query_factory=selectedCategory)

    service = QuerySelectField(
        'Service:',
        validators=[InputRequired()],
        get_label='name',
        query_factory=services)

    starting_location = StringField('Starting Location:')

    special_instructions = TextAreaField('Special Instructions:')
    follow_up_date = DateField('Follow Up Date:',
                               validators=[InputRequired()])
    status = QuerySelectField(
        'Status:',
        validators=[InputRequired()],
        get_label='name',
        query_factory=statusQuery)
    responsible_staffer = SelectField(
        'Responsible Staffer:', choices=[('yes', 'yes')])
    contact_log_priority = QuerySelectField(
        'Contact Log Priority:',
        validators=[InputRequired()],
        get_label='name',
        query_factory=contactLogQuery)

    person_to_cc = EmailField('Person to cc',
                              validators=[Length(0, 64),
                                          Email(), Optional()])
    destination = QuerySelectField(
        'Destination:',
        validators=[InputRequired()],
        get_label='street_address',
        query_factory=lambda: db.session.query(Address).order_by('street_address'))
    # duration = RadioField('Duration:',
    #                            choices=request_duration_type)
    submit = SubmitField("Submit")


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class MemberManager(FlaskForm):
    first_name = StringField('First name *',
                             validators=[InputRequired(),
                                         Length(1, 64)])
    middle_initial = StringField('Middle Initial',
                                 validators=[Length(min=0, max=1)])
    last_name = StringField('Last name *',
                            validators=[InputRequired(),
                                        Length(1, 64)])
    preferred_name = StringField(
        'Preferred Name', validators=[Optional(),
                                      Length(min=1, max=30)])
    salutations = [("none", ""), ("sir", "Sir"), ("mrs", "Mrs"), ("ms", "Ms"),
                   ("mr", "Mr")]
    salutation = SelectField("Salutation", choices=salutations)

    birthday = DateField("Birthday ", validators=[
        InputRequired()])
    genders = [("female", "Female"), ("male", "Male"), ("unspecified",
                                                        "Unspecified"), ("no_answer", "Does not wish to answer")]
    gender = SelectField("Gender *", choices=genders,
                         validators=[InputRequired()])

    countries = [('united_states', 'United States'), ('b', "B"), ('c', 'C')]
    states = [("ny", "NY")]
    time_zones = [("est", "Eastern Time (US & Canada) (UTC-05:00)"),
                  ("b", "B"), ("c", "C")]
    metro_areas = [("none", "<SELECT>"), ("a", "A"), ("b", "B"), ("c", "C")]

    primary_country = SelectField('Country', choices=countries)
    primary_address1 = StringField('Street address or P.O. Box',
                                   validators=[InputRequired(),
                                               Length(max=200)])
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
    primary_phone = IntegerField('Phone Number',
                                 widget=widgets.Input(input_type="tel"),
                                 validators=[InputRequired()])

    secondary_as_primary_checkbox = BooleanField(
        'Use this address instead of the primary address',
        validators=[Optional()])
    secondary_country = SelectField('Country', choices=countries)
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
    secondary_phone = IntegerField('Phone Number',
                                   widget=widgets.Input(input_type="tel"),
                                   validators=[Optional()])

    home_phone_number = IntegerField('Home Phone #',
                                     widget=widgets.Input(input_type="tel"),
                                     validators=[Optional()])
    cell_number = IntegerField('Cell Phone Number',
                               widget=widgets.Input(input_type="tel"),
                               validators=[Optional()])
    email = EmailField('Email',
                       validators=[InputRequired(),
                                   Length(1, 64),
                                   Email()])

    preferred_contact_method = RadioField(choices=[(
        'phone', 'Phone'), ('email', 'Email'), ('phone_and_email', 'Phone and Email')])
    emergency_contact_name = StringField(
        'Contact Name', validators=[Optional(),
                                    Length(1, 64)])
    emergency_contact_relationship = StringField(
        'Relationship', validators=[Optional(), Length(1, 64)])
    emergency_contact_phone_number = IntegerField(
        'Phone Number',
        widget=widgets.Input(input_type="tel"),
        validators=[Optional()])
    emergency_contact_email_address = EmailField(
        'Email', validators=[Optional(),
                             Length(1, 64),
                             Email()])

    expiration_date = DateField("Member Expiration Date: ", validators=[
        InputRequired()])
    member_number = IntegerField(validators=[Optional()])
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
    salutations = [("", ""), ("sir", "Sir"), ("mrs", "Mrs"), ("ms", "Ms"),
                   ("mr", "Mr")]
    salutation = SelectField("Salutation", choices=salutations)

    gender = SelectField("Gender",
                         validators=[InputRequired()],
                         choices=[("male", "Male"), ('female', "Female"), ("unspecified", "Unspecified"), ("no_answer", "Do not wish to answer")])

    birthday = DateField("Birthday ", validators=[InputRequired()])
    # make this a stringfield or select field?
    preferred_name = StringField(
        'Preferred Name', validators=[Optional(),
                                      Length(min=1, max=30)])
    # address
    primary_address1 = StringField('Street address or P.O. Box',
                                   validators=[InputRequired(),
                                               Length(max=200)])
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
        'Contact Name', validators=[Optional(),
                                    Length(1, 64)])
    emergency_contact_relationship = StringField(
        'Relationship', validators=[Optional(), Length(1, 64)])
    emergency_contact_phone_number = IntegerField(
        'Phone Number',
        widget=widgets.Input(input_type="tel"),
        validators=[Optional()])
    emergency_contact_email_address = EmailField(
        'Email', validators=[Optional(),
                             Length(1, 64),
                             Email()])
    # now under contact info
    home_phone = IntegerField("Primary Phone Number", widget=widgets.Input(input_type="tel"),
                              validators=[InputRequired()])
    email = EmailField('Email',
                       validators=[InputRequired(),
                                   Length(1, 64),
                                   Email()])
    contact_preference = RadioField('Preferred Contact Method', choices=[(
        'phone', "Phone"), ('email', "Email"), ('phone_and_email', "Phone and Email")])

    notes = TextAreaField("Notes for Office Staff", validators=[Optional()])

    submit = SubmitField("Submit")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    submit = SubmitField("Submit")


class AddServiceVetting(FlaskForm):
    vetting_notes = TextAreaField(
        "", render_kw={"rows": 15, "cols": 105}, validators=[Optional()])
    volunteer_fully_vetted_checkbox = BooleanField(
        'Is Fully Vetted?',
        validators=[Optional()])
    submit = SubmitField("Save")


class ContractorManager(FlaskForm):
    first_name = StringField('First name *',
                             validators=[InputRequired(),
                                         Length(1, 64)])
    middle_initial = StringField('Middle Initial',
                                 validators=[Length(min=0, max=1)])
    last_name = StringField('Last name *',
                            validators=[InputRequired(),
                                        Length(1, 64)])
    salutations = [("none", ""), ("sir", "Sir"), ("mrs", "Mrs"), ("ms", "Ms"),
                   ("mr", "Mr")]
    salutation = SelectField("Salutation", choices=salutations)
    company_name = StringField(
        'Company',
        validators=[Optional(), Length(min=1, max=30)])

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
    secondary_phone_number = IntegerField('Secondary Phone Number',
                                          widget=widgets.Input(
                                              input_type="tel"),
                                          validators=[Optional()])
    email = EmailField('Email',
                       validators=[Optional(),
                                   Length(1, 64),
                                   Email()])

    preferred_contact_method = RadioField(choices=[(
        'phone', 'Phone'), ('email', 'Email'), ('phone_and_email', 'Phone and Email')])

    website = StringField(
        'Website',
        validators=[Optional(), Length(min=1, max=30)])
    submit = SubmitField("Submit")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')


class Reviews(FlaskForm):
    reviewer_name = StringField('Name of Reviewer',
                                validators=[InputRequired(), Length(min=1, max=30)])
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=500)])
    submit = SubmitField("Save")


class AddAvailability(FlaskForm):
    availability_times = [("7 am", "7 am"), ("8 am", "8 am"), ("9 am", "9 am"), 
    ("10 am", "10 am"), ("11 am", "11 am"), ("12 pm", "12 pm"), ("1 pm", "1 pm"), 
    ("2 pm", "2 pm"), ("3 pm", "3 pm"), ("4 pm", "4 pm"), ("5 pm", "5 pm"), ("6 pm", "6 pm"),
    ("7-8 am", "7-8 am"), ("7-9 am", "7-9 am"), ("7-10 am", "7-10 am"), ("7-11 am", "7-11 am"), 
    ("7 am-12 pm", "7 am-12 pm"), ("7 am-1 pm", "7 am-1 pm"), ("7 am-2 pm", "7 am-2 pm"), 
    ("7 am-3 pm", "7 am-3 pm"), ("7 am-4 pm", "7 am-4 pm"), ("7 am-5 pm", "7 am-5 pm"), 
    ("7 am-6 pm", "7 am-6 pm"), ("8-9 am", "8-9 am"), ("8-10 am", "8-10 am"), ("8-11 am", "8-11 am"), 
    ("8 am-12 pm", "8 am-12 pm"), ("8 am-1 pm", "8 am-1 pm"), ("8 am-2 pm", "8 am-2 pm"), 
    ("8 am-3 pm", "8 am-3 pm"), ("8 am-4 pm", "8 am-4 pm"), ("8 am-5 pm", "8 am-5 pm"), 
    ("8 am-6 pm", "8 am-6 pm"), ("9-10 am", "9-10 am"), ("9-11 am", "9-11 am"), 
    ("9 am-12 pm", "9 am-12 pm"), ("9 am-1 pm", "9 am-1 pm"), ("9 am-2 pm", "9 am-2 pm"), 
    ("9 am-3 pm", "9 am-3 pm"), ("9 am-4 pm", "9 am-4 pm"), ("9 am-5 pm", "9 am-5 pm"), 
    ("9 am-6 pm", "9 am-6 pm"), ("10-11 am", "10-11 am"), ("10 am-12 pm", "10 am-12 pm"), 
    ("10 am-1 pm", "10 am-1 pm"), ("10 am-2 pm", "10 am-2 pm"), ("10 am-3 pm", "10 am-3 pm"), 
    ("10 am-4 pm", "10 am-4 pm"), ("10 am-5 pm", "10 am-5 pm"), ("10 am-6 pm", "10 am-6 pm"), 
    ("11 am-12 pm", "11 am-12 pm"), ("11 am-1 pm", "11 am-1 pm"), ("11 am-2 pm", "11 am-2 pm"), 
    ("11 am-3 pm", "11 am-3 pm"), ("11 am-4 pm", "11 am-4 pm"), ("11 am-5 pm", "11 am-5 pm"), 
    ("11 am-6 pm", "11 am-6 pm"), ("12-1 pm", "12-1 pm"), ("12-2 pm", "12-2 pm"), ("12-3 pm", "12-3 pm"), 
    ("12-4 pm", "12-4 pm"), ("12-5 pm", "12-5 pm"), ("12-6 pm", "12-6 pm"), ("1-2 pm", "1-2 pm"), 
    ("1-3 pm", "1-3 pm"), ("1-4 pm", "1-4 pm"), ("1-5 pm", "1-5 pm"), ("1-6 pm", "1-6 pm"),
    ("2-3 pm", "2-3 pm"), ("2-4 pm", "2-4 pm"), ("2-5 pm", "2-5 pm"), ("2-6 pm", "2-6 pm"),
    ("3-4 pm", "3-4 pm"), ("3-5 pm", "3-5 pm"), ("3-6 pm", "3-6 pm"), ("4-5 pm", "4-5 pm"), 
    ("4-6 pm", "4-6 pm"), ("5-6 pm", "5-6 pm")] 
    availability_monday = SelectMultipleField('', choices=availability_times)
    backup_monday = SelectMultipleField('', choices=availability_times)
    availability_tuesday = SelectMultipleField('', choices=availability_times)
    backup_tuesday = SelectMultipleField('', choices=availability_times)
    availability_wednesday = SelectMultipleField('', choices=availability_times)
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
    name = StringField('Service Name', validators=[
                       InputRequired(), Length(1, 200)])
    category = QuerySelectField(
        'Category Name',
        validators=[InputRequired()],
        get_label='name',
        query_factory=lambda: db.session.query(ServiceCategory).order_by('name'))
    submit = SubmitField('Save Service Information')


class EditMetroAreaForm(FlaskForm):
    name = StringField('Metro Area Name', validators=[
                       InputRequired(), Length(1, 200)])
    submit = SubmitField('Save Metro Area Information')
