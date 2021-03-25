from flask import Flask, render_template, url_for
from .forms import GeneralInformation, SpouseInformation, PrimaryAddress
app = Flask(__name__)
app.config['SECRET_KEY'] = 'ff44bd981ac737ac4264f7104fa68c2d1a6be086cb1a8c334d03617dd5d7039a'


@app.route('/')
def main():
    return 'Welcome to Love Living at Home!'


# Add basic information about a LLH Member.
@app.route('/basic-info')
def basic_info():
    form1 = GeneralInformation()
    form2 = SpouseInformation()
    form3 = PrimaryAddress()
    return render_template('basic_info.html',
                           title='Basic Member Information',
                           GeneralInfo=form1,
                           SpouseInfo=form2,
                           PrimaryAddress=form3)


# Search for an existing service request.
@app.route('/search-request')
def search_request():
    return render_template('base.html')


# Create a new service request.
@app.route('/create-request')
def create_request():
    return render_template('base.html')
