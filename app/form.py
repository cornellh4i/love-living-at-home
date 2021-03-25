from flask_wtf import FlaskForm
from wtforms.fields import (
    SelectField,
    SelectMultipleField,
    RadioField,
    SubmitField
)

from wtforms.fields.html5 import IntegerField

class SearchRequestForm(FlaskForm):
  request_type = SelectField('Request Type', choices = 
  ['Check All', 'Transportation Request', 'Member\'s Home Request'
  'Contractor Referral', 'Office Time Request'])

  request_status = SelectField('Request Status', choices = 
  ['Check All', 'Requested', 'Open Referral', 'Pending',
   'Confirmed', 'Completed', 'Cancelled'])

  service_category = SelectField('Service Category', choices =
  ['Check All', 'Coronavirus Community Support', 'Professional Home/Garden Service',
   'Professional In-Home Support', 'Technical Support', 
   'Transportation', 'Village Admin', 'Volunteer Home/Garden Service',
   'Volunteer In-Home Support'])

  provider_type = SelectField('Provider Type', choices = 
  ['Check All', 'Non-Member Volunteer', 'Member Volunteer', 'Contractor'])

  service_req_from = IntegerField('Service Req # from')
  service_req_to = IntegerField('to')

  priority = RadioField('High priority', choices=['Yes', 'No', 'Both'])
  show = RadioField('Show', choices=['Undated', 'Dated', 'Both'])

  search = SubmitField('Search')
  reset = SubmitField('Reset')



