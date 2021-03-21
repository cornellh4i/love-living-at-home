from flask import Flask, render_template, url_for
app = Flask(__name__)

@app.route('/')
def main():
    return 'Welcome to Love Living at Home!'


# Add basic information about a LLH Member.
@app.route('/basic-info')
def basic_info():
    return render_template('base.html')


# Search for an existing service request.
@app.route('/search-request')
def search_request():
    return render_template('base.html')


# Create a new service request.
@app.route('/create-request')
def create_request():
    return render_template('base.html')
