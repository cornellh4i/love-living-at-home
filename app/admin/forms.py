from datetime import date

from flask_wtf import FlaskForm
from sqlalchemy.sql.elements import Null
from wtforms import SelectMultipleField, ValidationError, widgets
from wtforms.ext.sqlalchemy.fields import (QuerySelectField,
                                           QuerySelectMultipleField)
from wtforms.fields import (BooleanField, IntegerField, PasswordField,
                            RadioField, SelectField, SelectMultipleField,
                            StringField, SubmitField, TextAreaField, FieldList,
                            HiddenField)
from wtforms.fields.html5 import DateField, EmailField, IntegerField, TimeField
from wtforms.validators import (Email, EqualTo, InputRequired,
                                Length, Optional, NumberRange)

from app import db
from app.models import (MetroArea, ContactLogPriorityType, Member, RequestStatus, RequestType, Role,
                        Service, ServiceCategory, Staffer, User)

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
    volunteer_type = SelectMultipleField(
        'Volunteer Type',
        choices=[(0, 'Member Volunteer'), (1, 'Non-Member Volunteer')])

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
        'Requesting Member:',
        render_kw={'onchange': "specialInstructions()"},
        id='member',
        validators=[InputRequired()],
        coerce=int)

    service_provider = SelectMultipleField('Service Provider',
                                           id='service-provider',
                                           validators=[InputRequired()],
                                           coerce=int)

    requested_date = DateField(
        'Requested Date', id='requested-date', validators=[InputRequired()])
    initial_pickup = TimeField('Inital Pickup:', id='initial-pickup', format='%H:%M',
                               validators=[InputRequired()])
    appointment = TimeField('Appointment:', id='appointment',
                            format='%H:%M',
                            validators=[InputRequired()])
    return_pickup = TimeField(
        'Return Pickup:', id='return-pickup', format='%H:%M')
    drop_off = TimeField('Drop Off:', id='dropoff', format='%H:%M')
    time_flexible = RadioField('Is Date/Time Flexible?',
                               choices=[(1, 'Yes'), (0, 'No')], id='time-flexible',
                               coerce=int)
    description = TextAreaField(
        'Short description (included in email):', id='description')

    service_category = SelectField(
        'Service Category:',
        render_kw={'onchange': "serviceChoices()"},
        validators=[InputRequired()], coerce=int
    )

    transportation_service = SelectField(
        'Service:',
        id="services",
        render_kw={'onchange': "providerChoices()"},
        validators=[Optional()], coerce=int)

    starting_location = StringField('Pickup Location:', id='starting-location',
                                    validators=[InputRequired()])

    special_instructions = TextAreaField('Special Instructions:',
                                         id="special-instructions-text")

    follow_up_date = DateField('Follow Up Date:')
    status = QuerySelectField('Status:',
                              id='status',
                              validators=[InputRequired()],
                              get_label='name',
                              query_factory=statusQuery)

    responsible_staffer = SelectField('Responsible Staffer:', coerce=int)

    contact_log_priority = QuerySelectField('Contact Log Priority:',
                                            validators=[InputRequired()],
                                            get_label='name',
                                            query_factory=contactLogQuery)

    person_to_cc = EmailField('Person to cc:',
                              validators=[Length(0, 64),
                                          Optional()])
    destination = SelectField('Destination:',
                              validators=[InputRequired()],
                              id='destination',
                              coerce=int)
    duration = RadioField('Duration:', coerce=int, id='duration')

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
        'Requesting Member:',
        render_kw={'onchange': "specialInstructions()"},
        id='member',
        validators=[InputRequired()],
        coerce=int)

    service_provider = SelectMultipleField('Service Provider',
                                           id='service-provider',
                                           validators=[InputRequired()],
                                           coerce=int)

    requested_date = DateField(
        'Date Requested', id='requested-date', validators=[InputRequired()])

    start_time = TimeField('From:',
                           format='%H:%M',
                           id='starting-time',
                           validators=[InputRequired()])
    end_time = TimeField('Until:', id='ending-time', format='%H:%M')
    high_priority = RadioField('Is high priority?', id='high-priority',
                               choices=[(1, 'Yes'), (0, 'No')],
                               coerce=int)
    # add alerts
    description = TextAreaField(
        'Short description (included in email):', id='description')

    service_category = SelectField(
        'Service Category:',
        render_kw={'onchange': "serviceChoices()"},
        validators=[InputRequired()], coerce=int)

    office_time_service = SelectField(
        'Service:',
        id="services",
        render_kw={'onchange': "providerChoices()"},
        validators=[Optional()],
        coerce=int)

    special_instructions = TextAreaField('Special Instructions:',
                                         id="special-instructions-text")

    responsible_staffer = SelectField('Responsible Staffer:', coerce=int)

    status = QuerySelectField('Status:',
                              validators=[InputRequired()],
                              id='status',
                              get_label='name',
                              query_factory=statusQuery)

    contact_log_priority = QuerySelectField('Contact Log Priority:',
                                            validators=[InputRequired()],
                                            get_label='name',
                                            query_factory=contactLogQuery)

    person_to_cc = EmailField('Person to cc:',
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
        'Requesting Member:',
        render_kw={'onchange': "specialInstructions()"},
        id='member',
        validators=[InputRequired()],
        coerce=int)

    service_provider = SelectMultipleField('Service Provider',
                                           id='service-provider',
                                           validators=[InputRequired()],
                                           coerce=int)

    requested_date = DateField(
        'Requested Date', id='requested-date', validators=[InputRequired()])

    time_from = TimeField('From:',
                          format='%H:%M',
                          id='starting-time',
                          validators=[InputRequired()])

    time_until = TimeField('Until:',
                           format='%H:%M',
                           id='ending-time',
                           validators=[InputRequired()])

    time_flexible = RadioField('Is Date/Time Flexible?',
                               choices=[(1, 'Yes'), (0, 'No')], id='time-flexible',
                               coerce=int)

    description = TextAreaField(
        'Short description (included in email):', id='description')

    service_category = SelectField(
        'Service Category:',
        render_kw={'onchange': "serviceChoices()"},
        validators=[InputRequired()],
        coerce=int)

    member_home_service = SelectField(
        'Service:',
        id="services",
        render_kw={'onchange': "providerChoices()"},
        validators=[Optional()],
        coerce=int)

    home_location = SelectMultipleField(
        'Location:',
        id='home_location',
        validators=[InputRequired()],
        coerce=int)

    special_instructions = TextAreaField('Special Instructions:',
                                         id="special-instructions-text")

    follow_up_date = DateField('Follow Up Date:')
    status = QuerySelectField('Status:', id='status',
                              validators=[InputRequired()],
                              get_label='name',
                              query_factory=statusQuery)

    responsible_staffer = SelectField('Responsible Staffer:', coerce=int)

    contact_log_priority = QuerySelectField('Contact Log Priority:',
                                            validators=[InputRequired()],
                                            get_label='name',
                                            query_factory=contactLogQuery)

    person_to_cc = EmailField('Person to cc:',
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

    # Volunteer ID infomration for member volunteers
    member_id = HiddenField('Member ID', validators=[Optional()])

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


class AddMemberVolunteer(FlaskForm):
    member = StringField('Member', validators=[InputRequired()])
    submit = SubmitField("Submit")


class AddAvailability(FlaskForm):
    availability_identity = TextAreaField()
    availability_monday_start = TimeField('Availability Start:',
                                          format='%H:%M', validators=[Optional()])
    availability_monday_end = TimeField('Availability End:',
                                        format='%H:%M', validators=[Optional()])
    backup_monday_start = TimeField('Availability Start:',
                                    format='%H:%M', validators=[Optional()])
    backup_monday_end = TimeField('Availability End:',
                                  format='%H:%M', validators=[Optional()])
    availability_tuesday_start = TimeField('Availability Start:',
                                           format='%H:%M', validators=[Optional()])
    availability_tuesday_end = TimeField('Availability End:',
                                         format='%H:%M', validators=[Optional()])
    backup_tuesday_start = TimeField('Availability Start:',
                                     format='%H:%M', validators=[Optional()])
    backup_tuesday_end = TimeField('Availability End:',
                                   format='%H:%M', validators=[Optional()])
    availability_wednesday_start = TimeField('Availability Start:',
                                             format='%H:%M', validators=[Optional()])
    availability_wednesday_end = TimeField('Availability End:',
                                           format='%H:%M', validators=[Optional()])
    backup_wednesday_start = TimeField('Availability Start:',
                                       format='%H:%M', validators=[Optional()])
    backup_wednesday_end = TimeField('Availability End:',
                                     format='%H:%M', validators=[Optional()])
    availability_thursday_start = TimeField('Availability Start:',
                                            format='%H:%M', validators=[Optional()])
    availability_thursday_end = TimeField('Availability End:',
                                          format='%H:%M', validators=[Optional()])
    backup_thursday_start = TimeField('Availability Start:',
                                      format='%H:%M', validators=[Optional()])
    backup_thursday_end = TimeField('Availability End:',
                                    format='%H:%M', validators=[Optional()])
    availability_friday_start = TimeField('Availability Start:',
                                          format='%H:%M', validators=[Optional()])
    availability_friday_end = TimeField('Availability End:',
                                        format='%H:%M', validators=[Optional()])
    backup_friday_start = TimeField('Availability Start:',
                                    format='%H:%M', validators=[Optional()])
    backup_friday_end = TimeField('Availability End:',
                                  format='%H:%M', validators=[Optional()])
    availability_saturday_start = TimeField('Availability Start:',
                                            format='%H:%M', validators=[Optional()])
    availability_saturday_end = TimeField('Availability End:',
                                          format='%H:%M', validators=[Optional()])
    backup_saturday_start = TimeField('Availability Start:',
                                      format='%H:%M', validators=[Optional()])
    backup_saturday_end = TimeField('Availability End:',
                                    format='%H:%M', validators=[Optional()])
    availability_sunday_start = TimeField('Availability Start:',
                                          format='%H:%M', validators=[Optional()])
    availability_sunday_end = TimeField('Availability End:',
                                        format='%H:%M', validators=[Optional()])
    backup_sunday_start = TimeField('Availability Start:',
                                    format='%H:%M', validators=[Optional()])
    backup_sunday_end = TimeField('Availability End:',
                                  format='%H:%M', validators=[Optional()])
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


class MakeIndividualCopiesForm(FlaskForm):
    number_of_individual_copies = IntegerField(
        'Number of individual copies', validators=[InputRequired(), NumberRange(min=1)], default=1)
    new_service_dates = FieldList(
        DateField('New Service Date'), min_entries=1, max_entries=10)
    new_service_times = FieldList(
        TimeField('at', format='%H:%M'), min_entries=1, max_entries=10)
    include_selected_service_providers = BooleanField(
        'Include Selected Service Provider(s)',
        validators=[Optional()])
    include_service_request_status = BooleanField(
        'Include Service Request Status',
        validators=[Optional()])
    submit1 = SubmitField('Copy Service Request')


class MakeDailyRepeatingCopiesForm(FlaskForm):
    new_service_date = DateField('New Service Date')
    new_service_time = TimeField('at', format='%H:%M')
    every_number_of_days = IntegerField(
        'Every', validators=[Optional(), NumberRange(min=1)])
    every_weekday = HiddenField(default=0)
    include_selected_service_providers = BooleanField(
        'Include Selected Service Provider(s)',
        validators=[Optional()])
    include_service_request_status = BooleanField(
        'Include Service Request Status',
        validators=[Optional()])
    end_after_2_1 = IntegerField('End after', validators=[
                                 Optional(), NumberRange(min=1, max=50)])
    end_by_2_1 = DateField('End by', validators=[
        Optional()], render_kw={'disabled': ''},)
    submit2_1 = SubmitField('Copy Service Request')


class MakeWeeklyRepeatingCopiesForm(FlaskForm):
    new_service_date = DateField('New Service Date')
    new_service_time = TimeField('at', format='%H:%M')
    number_of_weeks = IntegerField('Every', validators=[NumberRange(min=1)])
    day_of_week = MultiCheckboxField(
        coerce=int,
        choices=[
            (0, 'Monday'),
            (1, 'Tuesday'),
            (2, 'Wednesday'),
            (3, 'Thursday'),
            (4, 'Friday'),
            (5, 'Saturday'),
            (6, 'Sunday')
        ], validators=[InputRequired()])
    include_selected_service_providers = BooleanField(
        'Include Selected Service Provider(s)',
        validators=[Optional()])
    include_service_request_status = BooleanField(
        'Include Service Request Status',
        validators=[Optional()])
    end_after_2_2 = IntegerField('End after', validators=[
                                 Optional(), NumberRange(min=1, max=52)])
    end_by_2_2 = DateField('End by', validators=[
        Optional()], render_kw={'disabled': ''},)
    submit2_2 = SubmitField('Copy Service Request')


class MakeMonthlyRepeatingCopiesForm(FlaskForm):
    new_service_date = DateField('New Service Date')
    new_service_time = TimeField('at', format='%H:%M')

    is_day_of_every_selected = HiddenField(default=1)
    # Ex. Day 1 of every 2 month(s)
    nth_day = SelectField('Day',
                          choices=[(i, i) for i in range(1, 32)], coerce=int)
    of_every_nth_month = SelectField(
        'of every', choices=[(i, i) for i in range(1, 13)], coerce=int)

    # Ex. The First Sunday of every 1 month(s)
    week_choice = SelectField('The',
                              choices=[(1, 'First'), (2, 'Second'),
                                       (3, 'Third'), (4, 'Fourth'), (-1, 'Last')],
                              validators=[Optional()], render_kw={'disabled': ''}, coerce=int)
    weekday_choice = SelectField('', choices=[
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday')
    ], validators=[Optional()], render_kw={'disabled': ''}, coerce=int)
    month_choice = SelectField('of every', choices=[(
        i, i) for i in range(1, 13)], validators=[Optional()], render_kw={'disabled': ''}, coerce=int)

    include_selected_service_providers = BooleanField(
        'Include Selected Service Provider(s)',
        validators=[Optional()])
    include_service_request_status = BooleanField(
        'Include Service Request Status',
        validators=[Optional()])
    end_after_2_3 = IntegerField('End after', validators=[
                                 Optional(), NumberRange(min=1, max=24)])
    end_by_2_3 = DateField('End by', validators=[
        Optional()], render_kw={'disabled': ''},)
    submit2_3 = SubmitField('Copy Service Request')


class MakeYearlyRepeatingCopiesForm(FlaskForm):
    new_service_date = DateField('New Service Date')
    new_service_time = TimeField('at', format='%H:%M')
    is_yearly_day_of_every_selected = HiddenField(default=1)
    # Ex. Every January 1
    every_month_choice = SelectField('Every', choices=[
        (1, 'January'),
        (2, 'February'),
        (3, 'March'),
        (4, 'April'),
        (5, 'May'),
        (6, 'June'),
        (7, 'July'),
        (8, 'August'),
        (9, 'September'),
        (10, 'October'),
        (11, 'November'),
        (12, 'December')
    ], validators=[Optional()], coerce=int)
    day_choice = SelectField('', choices=[(i, i) for i in range(
        1, 32)], validators=[Optional()], coerce=int)

    # Ex. The First Sunday of January
    yearly_week_choice = SelectField('The',
                                     choices=[(1, 'First'), (2, 'Second'),
                                              (3, 'Third'), (4, 'Fourth'), (-1, 'Last')],
                                     validators=[Optional()], coerce=int, render_kw={'disabled': ''})
    yearly_weekday_choice = SelectField('', choices=[
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday')
    ], validators=[Optional()], coerce=int, render_kw={'disabled': ''})
    yearly_month_choice = SelectField('of', choices=[
        (1, 'January'),
        (2, 'February'),
        (3, 'March'),
        (4, 'April'),
        (5, 'May'),
        (6, 'June'),
        (7, 'July'),
        (8, 'August'),
        (9, 'September'),
        (10, 'October'),
        (11, 'November'),
        (12, 'December')
    ], validators=[Optional()], coerce=int, render_kw={'disabled': ''})

    include_selected_service_providers = BooleanField(
        'Include Selected Service Provider(s)',
        validators=[Optional()])
    include_service_request_status = BooleanField(
        'Include Service Request Status',
        validators=[Optional()])
    end_after_2_4 = IntegerField('End after', validators=[
                                 Optional(), NumberRange(min=1, max=24)])
    end_by_2_4 = DateField('End by', validators=[
        Optional()], render_kw={'disabled': ''},)
    submit2_4 = SubmitField('Copy Service Request')


class MakeCopiesWithoutDateForm(FlaskForm):
    number_of_copies = IntegerField(
        'Number of copies', validators=[InputRequired(), NumberRange(min=1)])
    include_selected_service_providers = BooleanField(
        'Include Selected Service Provider(s)',
        validators=[Optional()])
    include_service_request_status = BooleanField(
        'Include Service Request Status',
        validators=[Optional()])
    submit3 = SubmitField('Copy Service Request')
