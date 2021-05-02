from flask import (Blueprint, abort, flash, redirect, render_template, request,
                   url_for)
from flask_login import current_user, login_required
from flask_rq import get_queue

from app import db

from app.admin.forms import (ChangeAccountTypeForm, ChangeUserEmailForm,
                             ContractorManager, InviteUserForm, MemberManager,
                             NewUserForm, TransportationRequestForm,
                             VolunteerManager, SearchRequestForm, AddServiceVetting,
                             IsFullyVetted, AddAvailability, Reviews)
from app.decorators import admin_required
from app.email import send_email
from app.models import EditableHTML, Role, User, Member, Address, ServiceCategory, Service,  Request, service_category

admin = Blueprint('admin', __name__)


@admin.route('/')
@login_required
@admin_required
def index():
    """Admin dashboard page."""
    return render_template('admin/system_manager/index.html')


@admin.route('/request-manager')
@login_required
@admin_required
def request_manager():
    """Request Manager Page."""
    return render_template('admin/request_manager/layouts/base.html')


@admin.route('/people-manager')
@login_required
@admin_required
def people_manager():
    """People Manager Page."""
    return render_template('admin/people_manager/layouts/base.html')


@admin.route('/new-user', methods=['GET', 'POST'])
@login_required
@admin_required
def new_user():
    """Create a new user."""
    form = NewUserForm()
    if form.validate_on_submit():
        user = User(role=form.role.data,
                    first_name=form.first_name.data,
                    last_name=form.last_name.data,
                    email=form.email.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('User {} successfully created'.format(user.full_name()),
              'form-success')
    return render_template('admin/system_manager/new_user.html', form=form)


@admin.route('/invite-user', methods=['GET', 'POST'])
@login_required
@admin_required
def invite_user():
    """Invites a new user to create an account and set their own password."""
    form = InviteUserForm()
    if form.validate_on_submit():
        user = User(role=form.role.data,
                    first_name=form.first_name.data,
                    last_name=form.last_name.data,
                    email=form.email.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        invite_link = url_for('account.join_from_invite',
                              user_id=user.id,
                              token=token,
                              _external=True)
        get_queue().enqueue(
            send_email,
            recipient=user.email,
            subject='You Are Invited To Join',
            template='account/email/invite',
            user=user,
            invite_link=invite_link,
        )
        flash('User {} successfully invited'.format(user.full_name()),
              'form-success')
    return render_template('admin/system_manager/new_user.html', form=form)


@admin.route('/users')
@login_required
@admin_required
def registered_users():
    """View all registered users."""
    users = User.query.all()
    roles = Role.query.all()
    return render_template('admin/system_manager/registered_users.html',
                           users=users,
                           roles=roles)


@admin.route('/user/<int:user_id>')
@admin.route('/user/<int:user_id>/info')
@login_required
@admin_required
def user_info(user_id):
    """View a user's profile."""
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        abort(404)
    return render_template('admin/system_manager/manage_user.html', user=user)


@admin.route('/user/<int:user_id>/change-email', methods=['GET', 'POST'])
@login_required
@admin_required
def change_user_email(user_id):
    """Change a user's email."""
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        abort(404)
    form = ChangeUserEmailForm()
    if form.validate_on_submit():
        user.email = form.email.data
        db.session.add(user)
        db.session.commit()
        flash(
            'Email for user {} successfully changed to {}.'.format(
                user.full_name(), user.email), 'form-success')
    return render_template('admin/system_manager/manage_user.html', user=user, form=form)


@admin.route('/user/<int:user_id>/change-account-type',
             methods=['GET', 'POST'])
@login_required
@admin_required
def change_account_type(user_id):
    """Change a user's account type."""
    if current_user.id == user_id:
        flash(
            'You cannot change the type of your own account. Please ask '
            'another administrator to do this.', 'error')
        return redirect(url_for('admin.user_info', user_id=user_id))

    user = User.query.get(user_id)
    if user is None:
        abort(404)
    form = ChangeAccountTypeForm()
    if form.validate_on_submit():
        user.role = form.role.data
        db.session.add(user)
        db.session.commit()
        flash(
            'Role for user {} successfully changed to {}.'.format(
                user.full_name(), user.role.name), 'form-success')
    return render_template('admin/system_manager/manage_user.html', user=user, form=form)


@admin.route('/user/<int:user_id>/delete')
@login_required
@admin_required
def delete_user_request(user_id):
    """Request deletion of a user's account."""
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        abort(404)
    return render_template('admin/system_manager/manage_user.html', user=user)


@admin.route('/user/<int:user_id>/_delete')
@login_required
@admin_required
def delete_user(user_id):
    """Delete a user's account."""
    if current_user.id == user_id:
        flash(
            'You cannot delete your own account. Please ask another '
            'administrator to do this.', 'error')
    else:
        user = User.query.filter_by(id=user_id).first()
        db.session.delete(user)
        db.session.commit()
        flash('Successfully deleted user %s.' % user.full_name(), 'success')
    return redirect(url_for('admin.registered_users'))


@admin.route('/_update_editor_contents', methods=['POST'])
@login_required
@admin_required
def update_editor_contents():
    """Update the contents of an editor."""

    edit_data = request.form.get('edit_data')
    editor_name = request.form.get('editor_name')

    editor_contents = EditableHTML.query.filter_by(
        editor_name=editor_name).first()
    if editor_contents is None:
        editor_contents = EditableHTML(editor_name=editor_name)
    editor_contents.value = edit_data

    db.session.add(editor_contents)
    db.session.commit()

    return 'OK', 200


@admin.route('/search-request', methods=['POST', 'GET'])
@login_required
@admin_required
def search_request():
    form = SearchRequestForm()
    return render_template('admin/request_manager/search_request.html', title='Search Request', form=form)


# Create a new service request.
@admin.route('/create-request', methods=['GET', 'POST'])
@admin_required
def create_request():
    return render_template('admin/request_manager/create_request.html')


# Create a new Transportation service request.
@admin.route('/create-request/transportation-request', methods=['Get', 'POST'])
@admin_required
def create_transportation_request():
    form = TransportationRequestForm()
    if form.validate_on_submit():
        transportation_request = Request(
                                         type_id = 1,
                                         status_id=form.status.data.id,
                                         #update later to short description
                                         short_description=form.description.data,
                                         created_date=form.date_created.data,
                                         # modified_date=,
                                         requested_date=form.requested_date.data,
                                         initial_pickup_time=form.initial_pickup.data,
                                         appointment_time=form.appointment.data,
                                         return_pickup_time=form.return_pickup.data,
                                         drop_off_time=form.drop_off.data,
                                         is_date_time_flexible=form.time_flexible.data == 'Yes',
                                         duration_type_id=0,
                                         service_category_id=form.service_category.data.id,
                                         service_id=form.service.data.id,
                                         starting_address_id=form.starting_location.data,
                                         destination_address_id=form.destination.data.id,
                                         # Will be updated in the future for multiple ppl
                                         requesting_member_id=form.requesting_member.data[0].id,
                                         special_instructions=form.special_instructions.data,
                                         followup_date=form.follow_up_date.data,
                                         responsible_staffer_id=form.responsible_staffer.data,
                                         contact_log_priority_id=form.contact_log_priority.data.id,
                                         cc_email=form.person_to_cc.data)
        db.session.add(transportation_request)
        db.session.commit()
        flash(
            'Successfully submitted a new transportation request', 
            'form-success')
        return redirect(url_for('admin.index'))
    else:
        flash(form.errors, 'error')
    return render_template('admin/request_manager/transportation_request.html',
                           title='Transportation Request',
                           form=form)


@admin.route('/invite-member', methods=['GET', 'POST'])
@login_required
@admin_required
def invite_member():
    """Page for member management."""
    form = MemberManager()
    if form.validate_on_submit():
        if (form.secondary_as_primary_checkbox.data):
            address = Address(name=form.first_name.data + " " + form.last_name.data,
                              street_address=form.secondary_address1.data + " " + form.secondary_address2.data,
                              city=form.secondary_city.data)
        else:
            address = Address(name=form.first_name.data + " " + form.last_name.data,
                              street_address=form.primary_address1.data + " " + form.primary_address2.data,
                              city=form.primary_city.data)
        db.session.add(address)
        db.session.commit()
        member = Member(salutation=form.salutation.data,
                        primary_address_id=address.id,
                        first_name=form.first_name.data,
                        middle_initial=form.middle_initial.data,
                        last_name=form.last_name.data,
                        preferred_name=form.preferred_name.data,
                        gender=form.pronoun.data,
                        phone_number=form.home_phone_number.data,
                        email_address=form.email.data,
                        emergency_contact_name=form.emergency_contact_name.data,
                        emergency_contact_phone_number=form.emergency_contact_phone_number.data,
                        emergency_contact_email_address=form.emergency_contact_email_address.data,
                        membership_expiration_date=form.expiration_date.data,
                        volunteer_notes=form.volunteer_notes.data,
                        staffer_notes=form.staffer_notes.data)
        db.session.add(member)
        db.session.commit()
        flash('Member {} successfully created'.format(form.first_name.data),
              'form-success')
    return render_template('admin/people_manager/member_manager.html', form=form)


@admin.route('/invite-volunteer', methods=['GET', 'POST'])
@login_required
@admin_required
def invite_volunteer():
    """Invites a user to create a volunteer account"""
    form = VolunteerManager()
    add_vetting = AddServiceVetting()
    service_categories = [(category.name, category.request_type_id)
                          for category in ServiceCategory.query.all()]
    services = [(service.name, service.category_id)
                for service in Service.query.all()]
    is_fully_vetted = IsFullyVetted()
    add_availability = AddAvailability()
    if form.validate_on_submit():
        flash('Volunteer {} successfully invited'.format(
            form.first_name.data), 'form-success')
    return render_template('admin/people_manager/volunteer_manager.html',
                           form=form, add_vetting=add_vetting,
                           is_fully_vetted=is_fully_vetted,
                           add_availability=add_availability,
                           services=services,
                           service_categories=service_categories)


@admin.route('/invite-contractor', methods=['GET', 'POST'])
@login_required
@admin_required
def invite_contractor():
    """Page for contactor management."""
    form = ContractorManager()
    add_availability = AddAvailability()
    reviews = Reviews()
    if form.validate_on_submit():
        flash('Contractor {} successfully invited'.format(
            form.organization_name.data), 'form-success')
        return redirect(url_for('admin.index'))
    return render_template('admin/people_manager/contractor_manager.html', form=form, add_availability=add_availability, reviews=reviews)
