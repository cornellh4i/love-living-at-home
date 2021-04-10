from flask_wtf import FlaskForm
from wtforms.validators import Length, InputRequired, Optional
from wtforms import ValidationError, SelectMultipleField, widgets
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.fields import (
    PasswordField,
    StringField,
    SubmitField,
    SelectField,
    TextAreaField,
    RadioField,
    IntegerField,
    SubmitField,
    BooleanField,
    DateTimeField
)
from wtforms.fields.html5 import EmailField, DateField
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


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class MemberManager(FlaskForm):
    first_name = StringField(
        'First name', validators=[InputRequired(),
                                  Length(1, 64)])
    middle_initial = StringField('Middle Initial',
                                 validators=[Length(min=0, max=1)])
    last_name = StringField(
        'Last name', validators=[InputRequired(),
                                 Length(1, 64)])
    preferred_name = StringField('Preferred Name',
                                 validators=[Optional(), Length(min=1, max=30)])
    salutations = [("none", ""), ("sir", "Sir"),
                   ("mrs", "Mrs"), ("ms", "Ms"), ("mr", "Mr")]
    salutation = SelectField("Salutation", choices=salutations)

    pronoun = StringField("Pronoun", validators=[
        InputRequired(), Length(min=1, max=30)])

    countries = [('united_states', 'United States'), ('b', "B"), ('c', 'C')]
    states = [('none', ""), ("ny", "NY")]
    time_zones = [("est", "Eastern Time (US & Canada) (UTC-05:00)"),
                  ("b", "B"), ("c", "C")]
    metro_areas = [("none", "<SELECT>"), ("a", "A"), ("b", "B"), ("c", "C")]

    primary_country = SelectField('Country', choices=countries)
    primary_address1 = StringField('Address 1', validators=[
        Optional(), Length(max=200)])
    primary_address2 = StringField('Address 2', validators=[
        Optional(), Length(max=200)])
    primary_city = StringField(
        'City', validators=[Optional(), Length(max=200)])
    primary_state = SelectField('State', choices=states)
    primary_zip_code = StringField('Zip Code', validators=[
        Optional(), Length(max=45)])
    primary_time_zone = SelectField(
        'Timezone', choices=time_zones, validators=[Optional()])
    primary_metro_area = SelectField(
        'Metro Area', choices=metro_areas, validators=[Optional()])
    primary_phone = IntegerField('Phone Number', widget=widgets.Input(
        input_type="tel"), validators=[Optional()])

    secondary_as_primary_checkbox = BooleanField(
        'Use this address instead of the primary address', validators=[Optional()])
    secondary_country = SelectField('Country', choices=countries)
    secondary_address1 = StringField('Address 1', validators=[
        Optional(), Length(max=200)])
    secondary_address2 = StringField('Address 2', validators=[
        Optional(), Length(max=200)])
    secondary_city = StringField(
        'City', validators=[Optional(), Length(max=200)])
    secondary_state = SelectField('State', choices=states)
    secondary_zip_code = TextAreaField('Zip Code', validators=[
        Optional(), Length(max=45)])
    secondary_time_zone = SelectField(
        'Timezone', choices=time_zones, validators=[Optional()])
    secondary_metro_area = SelectField(
        'Metro Area', choices=metro_areas, validators=[Optional()])
    secondary_phone = IntegerField('Phone Number', widget=widgets.Input(
        input_type="tel"), validators=[Optional()])

    phone_number = IntegerField('Phone Number', widget=widgets.Input(
        input_type="tel"), validators=[Optional()])
    cell_number = IntegerField('Cell Phone Number', widget=widgets.Input(
        input_type="tel"), validators=[Optional()])
    email = EmailField(
        'Email', validators=[InputRequired(),
                             Length(1, 64),
                             Email()])

    emergency_contact_name = StringField(
        'Contact Name', validators=[InputRequired(),
                                    Length(1, 64)])
    emergency_contact_relationship = StringField(
        'Relationship', validators=[Optional(),
                                    Length(1, 64)])
    emergency_contact_phone_number = IntegerField('Phone Number', widget=widgets.Input(
        input_type="tel"), validators=[Optional()])
    emergency_contact_email_address = EmailField(
        'Email', validators=[InputRequired(),
                             Length(1, 64),
                             Email()])

    volunteer_notes = TextAreaField(
        'Notes for Volunteers', validators=[Optional(), Length(max=500)])

    staffer_notes = TextAreaField(
        'Notes for Office Staff', validators=[Optional(), Length(max=500)])

    submit = SubmitField("Submit")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')


class VolunteerManager(FlaskForm):
    salutations = [("", ""), ("sir", "Sir"), ("mrs", "Mrs"),
                   ("ms", "Ms"), ("mr", "Mr")]
    salutation = SelectField("Salutation", choices=salutations)
    first_name = StringField('First Name',
                             validators=[InputRequired(), Length(min=1, max=30)])
    middle_initial = StringField('Middle Initial',
                                 validators=[Length(min=0, max=1)])
    last_name = StringField('Last Name',
                            validators=[InputRequired(), Length(min=1, max=30)])
    gender = SelectField("Gender", validators=[InputRequired()], choices=[
                         ("male", "Male"), ('female', "Female")])

    # make this a stringfield or select field?
    pronoun = StringField("Pronouns", validators=[
        InputRequired(), Length(min=1, max=30)])
    preferred_name = StringField('Preferred Name',
                                 validators=[Optional(), Length(min=1, max=30)])
    primary_address1 = StringField('Address', validators=[
        InputRequired(), Length(max=200)])

    # now under contact info
    home_phone = IntegerField(widget=widgets.Input(
        input_type="tel"), validators=[InputRequired()])
    email = EmailField(
        'Email', validators=[InputRequired(),
                             Length(1, 64),
                             Email()])

    # What is another way to say Services willing to do
    files = [("alarm", "Alarm/Locks/Security"), ("bill", "Bill Paying/Paperwork"),
             ("auto", "Auto Repair"), ("remote", "Coronavirus Remote Assistance")]
    services = MultiCheckboxField('Services willing to do', choices=files)
    times = [("morning 8-11", "Morning 8-11"), ("morning 11-2", "Lunchtime 11-2"),
             ("afternoon 2-5", "Afternoon 2-5"), ("evening 5-8", "Evening 5-8"), ("night 8-midnight", "Night 8-Midnight")]
    availability_time = MultiCheckboxField('Availability Time', choices=times)
    days = [("monday", "Monday"), ("tuesday", "Tuesday"), ("wednesday", "Wednesday"), ("thursday",
                                                                                       "Thursday"), ("friday", "Friday"), ("saturday", "Saturday"), ("sunday", "Sunday")]
    availability_day = MultiCheckboxField(
        'Availability Day', choices=days)
    vettings = TextAreaField("Vettings", validators=[Optional()])

    # make a history of completed and pending services
    notes = TextAreaField("Notes for Office Staff", validators=[Optional()])

    submit = SubmitField("Submit")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')
    submit = SubmitField("Submit")


class ContractorManager(FlaskForm):
    organization_name = StringField('Organization Name',
                                    validators=[InputRequired(), Length(min=1, max=30)])
    address = StringField('Address', validators=[
        Optional(), Length(max=200)])
    phone_number = IntegerField('Phone Number', widget=widgets.Input(
        input_type="tel"), validators=[Optional()])
    email = EmailField('Email', validators=[
                       InputRequired(), Length(1, 64), Email()])

    # Is there a better way to record availability in one variable
    times = [("morning 8-11", "Morning 8-11"), ("morning 11-2", "Lunchtime 11-2"),
             ("afternoon 2-5", "Afternoon 2-5"), ("evening 5-8", "Evening 5-8"), ("night 8-midnight", "Night 8-Midnight")]
    availability_time = MultiCheckboxField('Availability Time', choices=times)
    days = [("monday", "Monday"), ("tuesday", "Tuesday"), ("wednesday", "Wednesday"), ("thursday",
                                                                                       "Thursday"), ("friday", "Friday"), ("saturday", "Saturday"), ("sunday", "Sunday")]
    availability_day = MultiCheckboxField(
        'Availability Day', choices=days)
    reviews = TextAreaField('Reviews', validators=[
                            Optional(), Length(max=500)])

    submit = SubmitField("Submit")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')
