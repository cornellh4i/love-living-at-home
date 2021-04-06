from app.admin.views import admin  # noqa

# Create a new service request.
@app.route('/create-request', methods=['GET', 'POST'])
def create_request():
    form = TransportationRequestForm()
    return render_template('create_request.html', title='Transportation Request', form=form)