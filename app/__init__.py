from flask import Flask, render_template, url_for
from form import SearchRequestForm
app = Flask(__name__)

app.config['SECRET_KEY'] = '579asldfi38042njfadf'

@app.route('/')
def main():
    return 'Welcome to Love Living at Home!'


# Add basic information about a LLH Member.
@app.route('/basic-info')
def basic_info():
    return render_template('base.html')


# Search for an existing service request.
@app.route('/search-request', methods=['POST','GET'])
def search_request():
    form = SearchRequestForm()
    return render_template('search_request.html', title = 'Search Request', form = form)


# Create a new service request.
@app.route('/create-request')
def create_request():
    return render_template('base.html')

if __name__ == '__main__':
    app.run(debug=True)
