from flask import Flask, render_template, url_for, redirect
from .forms import BasicMemberInformation
app = Flask(__name__)


@app.route('/')
def main():
    return 'Welcome to Love Living at Home!'


# Add basic information about a LLH Member.
@app.route('/basic-info', methods=['GET', 'POST'])
def basic_info():
    form = BasicMemberInformation()
    if form.validate_on_submit():
        return redirect(url_for('main'))
    return render_template('basic_info.html',
                           title='Basic Member Information',
                           form=form)


# Search for an existing service request.
@app.route('/search-request')
def search_request():
    return render_template('base.html')


# Create a new service request.
@app.route('/create-request')
def create_request():
    return render_template('base.html')
