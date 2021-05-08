from flask_wtf import FlaskForm
from wtforms import SelectMultipleField, ValidationError, widgets
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField

from wtforms.fields import (BooleanField, DateTimeField, IntegerField,
                            PasswordField, RadioField, SelectField, SelectMultipleField,
                            StringField, SubmitField, TextAreaField)
from wtforms.fields.html5 import DateField, EmailField, TimeField, IntegerField
from wtforms.validators import Email, EqualTo, InputRequired, Length, Optional, DataRequired

from app import db
from app.models import Role, User, ServiceCategory, Service, Staffer, RequestStatus, ContactLogPriorityType, Member, Address, RequestDurationType
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
    request_type = SelectMultipleField('Request Type', choices = [(-1, 'Select All'),(0,'Transportation Request'), 
    (1,'Member\'s Home Request'), (2, 'Office Time Request')], validators = [DataRequired()])


    request_status = SelectMultipleField('Request Status', choices = 
    [(-1, 'Select All'),(0, 'Requested'), (1, 'Confirmed'), (2, 'Completed'), (3, 'Cancelled')], validators = [DataRequired()])

    service_category = SelectMultipleField('Service Category', choices =
    [(-1, 'Select All'),(0, 'COVID Community Support'), (1, 'Professional Home/Garden Service'),
    (2, 'Professional In-Home Support'), (3, 'Technical Support'), 
    (4, 'Transportation'), (5, 'Village Admin'), (6, 'Volunteer Home/Garden Service'),
    (7, 'Volunteer In-Home Support')], validators = [DataRequired()])

    provider_type = SelectMultipleField('Provider Type', choices = 
    [(-1, 'Select All'), (0, 'Non-Member Volunteer'), (1, 'Member Volunteer'), (2, 'Contractor')], validators = [DataRequired()])

    requesting_member = SelectField('Requesting Member', choices = [(0, 'Nat Peuly'), (1, 'Sohni Uthra'), (2, 'Angela Jin'), 
    (3, 'Alina Kim')], validators=[DataRequired()])

    service_provider = SelectField('Service Provider', choices = [(0, 'Nat Peuly'), (1, 'Sohni Uthra'), (2, 'Angela Jin'), 
    (3, 'Alina Kim')], validators=[DataRequired()])

    show = RadioField('Show', choices=[(0,'Undated'), (1,'Dated')])

    time_period = SelectField('Time Period', choices = [(0, 'Today'), (1, 'This Week'), (2, 'This Month'), (3, 'Future Dates')], validators = [DataRequired()])

    start_date = DateField('Start Date', validators=[InputRequired()], format='%Y-%M-%D')
    end_date = DateField('End Date', validators=[InputRequired()], format='%Y-%M-%D')

    apply_filters = SubmitField('Apply Filters')
    reset_filters = SubmitField('Reset Filters')


class TransportationRequestForm(FlaskForm):
    categoryId = 0
    def selectedCategory():
        return db.session.query(ServiceCategory).order_by().filter(ServiceCategory.request_type_id == 0)

    def covid_services():
        return db.session.query(Service).order_by().filter(Service.category_id == 1)

    def transportation_services():
        return db.session.query(Service).order_by().filter(Service.category_id == 0)

    def stafferQuery():
        return db.session.query(Staffer).order_by()

    def statusQuery():
        return db.session.query(RequestStatus).order_by()

    def contactLogQuery():
        return db.session.query(ContactLogPriorityType).order_by()

    def specialInstructionsQuery():
        return db.session.query(Member).order_by()

    special_instructions_list = []

    date_created = DateField('Date Created:', default = date.today, 
        render_kw={'readonly': True})
    requesting_member = SelectMultipleField(
        'Requesting Member',
        id = 'member',
        validators=[InputRequired()],
        coerce = int)
    requested_date = DateField('Requested Date',
                               validators=[InputRequired()])
    initial_pickup = TimeField('Inital Pickup:', format='%H:%M',
        validators=[InputRequired()])
    appointment = TimeField('Appointment:', format='%H:%M', 
    validators=[InputRequired()])
    return_pickup = TimeField('Return Pickup:', format='%H:%M')
    drop_off = TimeField('Drop Off:', format='%H:%M')
    time_flexible = RadioField('Is Date/Time Flexible?',
                               choices=[(True, 'Yes'), (False, 'No')],  coerce=lambda x: x == 'True')
    description = TextAreaField('Short description (included in email):')

    service_category = QuerySelectField(
        'Service Category:',
        render_kw={'onchange': "serviceChoices()"},
        validators=[InputRequired()],
        get_label='name',
        query_factory=selectedCategory)

    covid_service = QuerySelectField(
        'Service:',
        id = "covid_service",
        render_kw={'onchange': "serviceChoices()"},
        validators=[Optional()],
        get_label='name',
        query_factory=covid_services)

    transportation_service = QuerySelectField(
        'Service:',
        render_kw={'onchange': "serviceChoices()"},
        id = "transportation_service",
        validators=[Optional()],
        get_label='name',
        query_factory=transportation_services)

    starting_location = SelectField(
        'Destination:',
        validators=[InputRequired()], coerce=int)

    special_instructions = TextAreaField('Special Instructions:')

    follow_up_date = DateField('Follow Up Date:')
    status = QuerySelectField(
        'Status:',
        validators=[InputRequired()],
        get_label='name',
        query_factory=statusQuery)
    responsible_staffer = SelectField('Responsible Staffer:', 
        choices = [(1, 'yes'), (2, 'no')],
        coerce=int)
    contact_log_priority = QuerySelectField(
        'Contact Log Priority:',
        validators=[InputRequired()],
        get_label='name',
        query_factory=contactLogQuery)
    
    person_to_cc = EmailField('Person to cc',
                       validators=[Length(0, 64), Optional()])
    destination = SelectField(
        'Destination:',
        validators=[InputRequired()], coerce=int)
    duration = RadioField('Duration:', coerce=int)
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

    pronoun = StringField("Pronoun *",
                          validators=[InputRequired(),
                                      Length(min=1, max=30)])

    countries = [('united_states', 'United States'), ('b', "B"), ('c', 'C')]
    states = [('none', ""), ("ny", "NY")]
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
                                 validators=[Optional()])

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
    volunteer_notes = TextAreaField('Notes for Volunteers',
                                    validators=[Optional(),
                                                Length(max=500)])

    staffer_notes = TextAreaField('Notes for Office Staff',
                                  validators=[Optional(),
                                              Length(max=500)])

    submit = SubmitField("Submit")



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
    # make a history of completed and pending services
    notes = TextAreaField("Notes for Office Staff", validators=[Optional()])

    submit = SubmitField("Submit")



class AddServiceVetting(FlaskForm):
    vetting_types = [("none", "Select"), ("a", "a"), ("b", "b")]
    vetting_users = [("cheryl", "Cheryl"), ("a", "a"), ("b", "b")]
    vetting_type = SelectField('Type: ',
                               choices=vetting_types,
                               validators=[InputRequired()])
    vetting_date = DateField("Date: ", validators=[
                             InputRequired()], format='%Y-%M-%D')
    vetting_expiration = DateField('Date Expired: ',
                                   validators=[InputRequired()],
                                   format='%Y-%M-%D')
    vetting_additional_data = TextAreaField("Additional Data: ", validators=[
                                            InputRequired()])
    vetting_notes = TextAreaField("Notes: ", validators=[Optional()])
    vetting_who_entered = SelectField('Who Entered: ',
                                      choices=vetting_users,
                                      validators=[InputRequired()])
    submit = SubmitField("Save")


class IsFullyVetted(FlaskForm):
    volunteer_fully_vetted_checkbox = BooleanField(
        'Check this box to confirm that this volunteer has been fully vetted',
        validators=[InputRequired()])
    vetting_users = [("cheryl", "Cheryl"), ("a", "a"), ("b", "b")]
    vetting_who_entered = SelectField('Who Entered: ',
                                      choices=vetting_users,
                                      validators=[InputRequired()])
    submit = SubmitField("Save")


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
    submit = SubmitField("Submit")

class Reviews(FlaskForm):
    reviewer_name = StringField('Name of Reviewer',
                                validators=[InputRequired(), Length(min=1, max=30)])
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=500)])
    submit = SubmitField("Save")


class AddAvailability(FlaskForm):
    availability_options = [("not available", "Not Available"), (
        "most likely available", "Most Likely Available"), ("available", "Available")]
    availability_m1 = SelectField('', choices=availability_options)
    availability_m2 = SelectField('', choices=availability_options)
    availability_m3 = SelectField('', choices=availability_options)
    availability_m4 = SelectField('', choices=availability_options)
    availability_m5 = SelectField('', choices=availability_options)
    availability_t1 = SelectField('', choices=availability_options)
    availability_t2 = SelectField('', choices=availability_options)
    availability_t3 = SelectField('', choices=availability_options)
    availability_t4 = SelectField('', choices=availability_options)
    availability_t5 = SelectField('', choices=availability_options)
    availability_w1 = SelectField('', choices=availability_options)
    availability_w2 = SelectField('', choices=availability_options)
    availability_w3 = SelectField('', choices=availability_options)
    availability_w4 = SelectField('', choices=availability_options)
    availability_w5 = SelectField('', choices=availability_options)
    availability_th1 = SelectField('', choices=availability_options)
    availability_th2 = SelectField('', choices=availability_options)
    availability_th3 = SelectField('', choices=availability_options)
    availability_th4 = SelectField('', choices=availability_options)
    availability_th5 = SelectField('', choices=availability_options)
    availability_f1 = SelectField('', choices=availability_options)
    availability_f2 = SelectField('', choices=availability_options)
    availability_f3 = SelectField('', choices=availability_options)
    availability_f4 = SelectField('', choices=availability_options)
    availability_f5 = SelectField('', choices=availability_options)
    submit = SubmitField("Save")


class EditServiceForm(FlaskForm):
    name = StringField('Service Name', validators=[InputRequired(), Length(1, 200)])
    category = QuerySelectField(
        'Category Name',
        validators=[InputRequired()],
        get_label='name',
        query_factory=lambda: db.session.query(ServiceCategory).order_by('name'))
    submit = SubmitField('Save Service Information')


