from flask_wtf from FlaskForm
from wtforms import StringField, DateField, SelectField, TextAreaField, RadioField, IntegerField
from wtforms.validators import Length, InputRequired

class GeneralInformation(FlaskForm):
    member_number = StringField('Member Number',
                                validators=[ InputRequired(), Length(min=1, max=30)])
    salutations=["Sir", "Mrs", "Ms", "Mr"]
    salutation = SelectField("Salutation", choices = salutations)
    first_name = StringField('First Name',
                                validators=[InputRequired(), Length(min=1, max=30)])
    middle_initial = StringField('Middle Initial',
                                validators=[Length(min=0, max=1)])
    last_name = StringField('Last Name'
                                validators=[InputRequired(), Length(min=1, max=30)])
    #maybe use select field here
    gender = RadioField(u"Gender", choices=[("male", "Male"), ('female', "Female")])
    birthday = DateField('Birthday', format='%Y-%m-%d')
    preferred_name = StringField('Preferred Name',
                                validators=[Length(min=1,max=30)])
    mailing_name = String('Mailing Name',
                                validators=[Length(min=1, max=30)])

class SpouseInformation(FlaskForm):
    first_name = StringField('First Name', validators=[Length(min=1, max=30)])
    last_name = StringField('Last Name', validators=[Length(min=1, max=30)])

/** 
* TODO: 
* - find an array of all timezones
* - find an array of all timezones 
*/
class PrimaryAddress(FlaskForm):
    countries = ['United States', 'Afghanistan', 'Albania', 'Algeria', 
    'American Samoa', 'Andorra', 'Angola', 'Anguilla', 'Antarctica', 
    'Antigua And Barbuda', 'Argentina', 'Armenia', 'Aruba', 'Australia', 
    'Austria', 'Azerbaijan', 'Bahamas', 'Bahrain', 'Bangladesh', 'Barbados', 
    'Belarus', 'Belgium', 'Belize', 'Benin', 'Bermuda', 'Bhutan', 'Bolivia', 
    'Bosnia And Herzegowina', 'Botswana', 'Bouvet Island', 'Brazil', 
    'Brunei Darussalam', 'Bulgaria', 'Burkina Faso', 'Burundi', 'Cambodia', 
    'Cameroon', 'Canada', 'Cape Verde', 'Cayman Islands', 'Central African Rep', 
    'Chad', 'Chile', 'China', 'Christmas Island', 'Cocos Islands', 'Colombia', 
    'Comoros', 'Congo', 'Cook Islands', 'Costa Rica', 'Cote D`ivoire', 'Croatia', 
    'Cuba', 'Cyprus', 'Czech Republic', 'Denmark', 'Djibouti', 'Dominica', 
    'Dominican Republic', 'East Timor', 'Ecuador', 'Egypt', 'El Salvador', 
    'Equatorial Guinea', 'Eritrea', 'Estonia', 'Ethiopia', 
    'Falkland Islands (Malvinas)', 'Faroe Islands', 'Fiji', 
    'Finland', 'France', 'French Guiana', 'French Polynesia', 
    'French S. Territories', 'Gabon', 'Gambia', 'Georgia', 
    'Germany', 'Ghana', 'Gibraltar', 'Greece', 'Greenland', 
    'Grenada', 'Guadeloupe', 'Guam', 'Guatemala', 'Guinea', 
    'Guinea-bissau', 'Guyana', 'Haiti', 'Honduras', 'Hong Kong', 
    'Hungary', 'Iceland', 'India', 'Indonesia', 'Iran', 'Iraq', 
    'Ireland', 'Israel', 'Italy', 'Jamaica', 'Japan', 'Jordan', 
    'Kazakhstan', 'Kenya', 'Kiribati', 'Korea (North)', 'Korea (South)', 
    'Kuwait', 'Kyrgyzstan', 'Laos', 'Latvia', 'Lebanon', 'Lesotho', 'Liberia', 
    'Libya', 'Liechtenstein', 'Lithuania', 'Luxembourg', 'Macau', 'Macedonia', 
    'Madagascar', 'Malawi', 'Malaysia', 'Maldives', 'Mali', 'Malta', 
    'Marshall Islands', 'Martinique', 'Mauritania', 'Mauritius', 'Mayotte', 
    'Mexico', 'Micronesia', 'Moldova', 'Monaco', 'Mongolia', 'Montserrat', 
    'Morocco', 'Mozambique', 'Myanmar', 'Namibia', 'Nauru', 'Nepal', 
    'Netherlands', 'Netherlands Antilles', 'New Caledonia', 'New Zealand', 
    'Nicaragua', 'Niger', 'Nigeria', 'Niue', 'Norfolk Island', 
    'Northern Mariana Islands', 'Norway', 'Oman', 'Pakistan', 'Palau', 
    'Panama', 'Papua New Guinea', 'Paraguay', 'Peru', 'Philippines', 'Pitcairn', 
    'Poland', 'Portugal', 'Puerto Rico', 'Qatar', 'Reunion', 'Romania', 
    'Russian Federation', 'Rwanda', 'Saint Kitts And Nevis', 'Saint Lucia', 
    'St Vincent/Grenadines', 'Samoa', 
    'San Marino', 'Sao Tome', 'Saudi Arabia', 'Senegal', 'Seychelles', 'Sierra Leone', 
    'Singapore', 'Slovakia', 'Slovenia', 'Solomon Islands', 'Somalia', 'South Africa', 
    'Spain', 'Sri Lanka', 'St. Helena', 'St.Pierre', 'Sudan', 'Suriname', 'Swaziland', 
    'Sweden', 'Switzerland', 'Syrian Arab Republic', 'Taiwan', 'Tajikistan', 'Tanzania', 
    'Thailand', 'Togo', 'Tokelau', 'Tonga', 'Trinidad And Tobago', 'Tunisia', 'Turkey', 
    'Turkmenistan', 'Tuvalu', 'Uganda', 'Ukraine', 'United Arab Emirates', 
    'United Kingdom', 'Uruguay', 'Uzbekistan', 'Vanuatu', 'Vatican City State', 
    'Venezuela', 'Viet Nam', 'Virgin Islands (British)', 'Virgin Islands (U.S.)', 
    'Western Sahara', 'Yemen', 'Yugoslavia', 'Zaire', 'Zambia', 'Zimbabwe']

    country = SelectField('Country', choices = countries)
    address1 = TextAreaField('Address 1', validators = [Length(max = 200)])
    address2 = TextAreaField('Address 2', validators = [Length(max = 200)])
    city = TextAreaField('City', validators = [Length(max = 200)])

    states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA", 
          "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", 
          "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", 
          "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", 
          "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]

    state = SelectField('State', choices = states)
    zip_code = TextAreaField('Zip Code', validators = [Length(max = 45)])
    

    time_zones = ["a", "b", "c"]
    time_zone = SelectField('Time Zone', choices = time_zones)

    metro_areas = ["a", "b", "c"]
    metro_area = SelectField('Metro Area', choices = metro_areas)
    home_phone = IntegerField(widget = widgets.Input(input_type = "tel"))
    