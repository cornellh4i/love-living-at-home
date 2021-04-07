from flask_wtf import FlaskForm
from wtforms.fields import (
    SelectField,
    SelectMultipleField,
    RadioField,
    SubmitField
)

from wtforms.fields.html5 import IntegerField

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



