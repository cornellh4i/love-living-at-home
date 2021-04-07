from flask_wtf import FlaskForm
from wtforms import ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.fields import (
    PasswordField,
    StringField,
    SubmitField,
    RadioField,
    SelectField,
    TextAreaField,
    SelectMultipleField

)
from wtforms.fields.html5 import EmailField, DateField, TimeField, IntegerField
from wtforms.validators import (
    Email,
    EqualTo,
    InputRequired,
    Length,
)


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

    
class SearchRequestForm(FlaskForm):

  request_type = SelectMultipleField('Request Type', choices = [(0,'Check All'),
   (1,'Transportation Request'), (2,'Member\'s Home Request'),
   (3,'Contractor Referral'), (4,'Office Time Request')])


  request_status = SelectMultipleField('Request Status', choices = 
  [(0, 'Check All'), (1, 'Requested'), (2, 'Open Referral'), (3, 'Pending'),
   (4, 'Confirmed'), (5, 'Completed'), (6, 'Cancelled')])

  service_category = SelectMultipleField('Service Category', choices =
  [(0, 'Check All'), (1, 'Coronavirus Community Support'), (2, 'Professional Home/Garden Service'),
   (3, 'Professional In-Home Support'), (4, 'Technical Support'), 
   (5, 'Transportation'), (6, 'Village Admin'), (7, 'Volunteer Home/Garden Service'),
   (8, 'Volunteer In-Home Support')])

  provider_type = SelectMultipleField('Provider Type', choices = 
  [(0, 'Check All'), (1, 'Non-Member Volunteer'), (2, 'Member Volunteer'), (3, 'Contractor')])

  service_req_from = IntegerField('Service Req # from', default=0)
  service_req_to = IntegerField('to', default=0)

  priority = RadioField('High priority', choices=['Yes', 'No', 'Both'])
  show = RadioField('Show', choices=['Undated', 'Dated', 'Both'])

  search = SubmitField('Search')
  reset = SubmitField('Reset')



