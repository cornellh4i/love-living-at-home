import json
import sys
from operator import __truediv__

from flask import (Blueprint, abort, flash, redirect, render_template, request,
                   send_file, url_for, jsonify)
from flask_login import current_user, login_required
from flask_rq import get_queue

from app import db
from app.admin.forms import (AddAvailability, AddServiceToVolunteer,
                             AddVetting, AddReview, ChangeAccountTypeForm,
                             ChangeUserEmailForm, ContractorManager,
                             EditMetroAreaForm, EditServiceForm, EditServiceCategoryForm,
                             EditDestinationAddressForm,
                             InviteUserForm, MemberManager, MembersHomeRequestForm, MultiCheckboxField,
                             NewUserForm, SearchRequestForm, TransportationRequestForm,
                             VolunteerManager, OfficeTimeRequestForm, GeneratePdfForm, EditServicesVolunteerCanProvide)
from app.decorators import admin_required
from app.email import send_email
from app.models import (Address, Availability, EditableHTML, LocalResource,
                        Member, MetroArea, ProvidedService, MembersHomeRequest, TransportationRequest, Role, Service, ServiceCategory, Staffer, User, Volunteer, VolunteerType, RequestMemberRecord, RequestMemberRecord, Review)
from app.models.transportation_request import ContactLogPriorityType, RequestDurationType, RequestStatus, RequestType
from app.models.request_volunteer_record import RequestVolunteerRecord
from app.models.office_request import OfficeRequest
from wtforms.fields.core import Label

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


@admin.route('/people-manager', methods=['GET', 'POST'])
@login_required
@admin_required
def people_manager():
    """People Manager Page."""
    service_categories = sorted(
        [(category.name, category.request_type_id, category.id)
         for category in ServiceCategory.query.all()],
        key=lambda triple: triple[2])
    services = [(service.name, service.category_id, service.id)
                for service in Service.query.all()]
    category_dict = {}
    category_name_to_id = {}
    for count, category in enumerate(service_categories):
        category_name_to_id[category[0]] = category[1]
        choices = []
        for service in services:
            if service[1] == category[1]:
                choices.append((service[0], service[0]))
        category_dict[category[0]] = MultiCheckboxField(category[0],
                                                        choices=choices)
    for key, value in category_dict.items():
        setattr(AddServiceToVolunteer, key, value)
    service_form = AddServiceToVolunteer()

    # NEED TO CHANGE THIS SO THAT WE UPDATE VETTINGS BASED ON WHICH USER WAS SELECTED
    volunteer = Volunteer.query.first()

    # SERVICES UPDATED
    if service_form.validate_on_submit():
        for key, value in category_dict.items():
            service_input = getattr(service_form, key)
            service_data = service_input.data
            for service in service_data:
                service_to_be_committed = Service.query.filter_by(
                    name=service,
                    category_id=int(category_name_to_id[key])).first()
                provided_service = ProvidedService(
                    service_id=service_to_be_committed.id,
                    volunteer_id=volunteer.id)
                db.session.add(provided_service)
                db.session.commit()
            flash(
                'Services provided by {} successfully updated'.format(
                    volunteer.first_name), 'form-success')
    active = "member"
    if 'active' in request.args:
        active = request.args['active']
    data ={'active':active }
    members = Member.query.all()
    volunteers = Volunteer.query.all()
    local_resources = LocalResource.query.all()
    return render_template('admin/people_manager/layouts/base.html',
                           service_form=service_form,
                           category_dict=category_dict,
                           members=members,
                           volunteers=volunteers,
                           local_resources=local_resources, data=data)


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
    return render_template('admin/system_manager/manage_user.html',
                           user=user,
                           form=form)


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
    return render_template('admin/system_manager/manage_user.html',
                           user=user,
                           form=form)


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

def select_all(selection, field):
    if '-1' in selection:
        if field == 'requesttype':
            return [0, 1, 2]
        if field == 'requeststatus':
            return [0, 1, 2, 3]
        if field == 'servicecategory':
            return [0, 1, 2, 3, 4, 5, 6, 7]
        if field == 'providertype':
            return [0, 1, 2]
    return list(map(int, selection))


@admin.route('/search-request', methods=['POST', 'GET'])
@login_required
@admin_required
def search_request():
    form = SearchRequestForm()

    # Pull choices from database
    form.request_type.choices = [(request_type.name, request_type.name)
                                 for request_type in RequestType.query.all()]
    form.request_status.choices = [
        (request_status.name, request_status.name)
        for request_status in RequestStatus.query.all()
    ]
    form.service_category.choices = [
        (service_category.name, service_category.name)
        for service_category in ServiceCategory.query.all()
    ]
    form.requesting_member.choices = [
        (member.id, member.first_name + " " + member.last_name)
        for member in Member.query.all()
    ] + [(-1, "Randy Warden"),
         (-2, "Anne Rodda")]  # temporarily added these extra members
    service_providers = [
        ('volunteer', volunteer.id,
         volunteer.first_name + " " + volunteer.last_name)
        for volunteer in Volunteer.query.all()
    ] + [('local-resource', local_resource.id, local_resource.company_name)
         for local_resource in LocalResource.query.all()
         ]  # TODO -- what is required from local resources

    form.dated_filter.choices = [(0, 'Dated'), (1, 'Undated')]
    temp_requests = []
    # temp_requests = [{
    #     'request_num': 6724,
    #     'request_status': "Requested",
    #     'requested_date_display': "06/17",
    #     'requested_date_full': "06/17/2021",
    #     'requested_day_of_week': "Saturday",
    #     'start_time': "12:00 PM",
    #     'end_time': "12:00 PM",
    #     'member_name': "Anne Rodda",
    #     'volunteer_name': "Fran Spadafora Manzella",
    #     'is_volunteer': True,
    #     'request_type': "Member's Home",
    #     'service': "Pet Care -Vol",
    #     'created_date': "06/15/2021",
    #     'modified_date': "N/A",
    #     'service_category': "Volunteer In-Home Support",
    #     'member_numbers': -2
    # }, {
    #     'request_num': 6697,
    #     'request_status': "Confirmed",
    #     'requested_date_display': "06/21",
    #     'requested_date_full': "06/21/2021",
    #     'requested_day_of_week': "Wednesday",
    #     'start_time': "11:30 AM",
    #     'end_time': "12:40 PM",
    #     'member_name': "Randy Warden",
    #     'volunteer_name': "Hank Dullea",
    #     'is_volunteer': True,
    #     'request_type': "Transportation",
    #     'service': "Vol Driver Local Medical Appt",
    #     'created_date': "06/11/2021",
    #     'modified_date': "06/18/2021",
    #     'service_category': "Transportation",
    #     'member_numbers': -1
    # }, {
    #     'request_num': 6698,
    #     'request_status': "Confirmed",
    #     'requested_date_display': "",
    #     'requested_date_full': "",
    #     'requested_day_of_week': "Friday",
    #     'start_time': "10:00 AM",
    #     'end_time': "11:00 PM",
    #     'member_name': "John Brown",
    #     'volunteer_name': "Diana Cosgrove",
    #     'is_volunteer': True,
    #     'request_type': "Transportation",
    #     'service': "Vol Driver Local Medical Appt",
    #     'created_date': "06/11/2021",
    #     'modified_date': "06/18/2021",
    #     'service_category': "Transportation",
    #     'member_numbers': -1
    # }]

    # Pull existing requests from the database and format each of them for display on front-end.
    transportation_requests = TransportationRequest.query.all()
    office_time_requests = OfficeRequest.query.all()
    members_home_requests = MembersHomeRequest.query.all()
    db_requests = [transportation_requests,
                   office_time_requests, members_home_requests]
    formatted_db_requests = []
    for index, db_request_type in enumerate(db_requests):
        for db_req in db_request_type:
            request_member_records = RequestMemberRecord.query.filter_by(
                request_id=db_req.id, request_category_id=index).all()

            members = []
            member_ids = []
            for request_member_record in request_member_records:
                members.append(Member.query.get(
                    request_member_record.member_id))
                member_ids.append(str(request_member_record.member_id))

            request_volunteer_records = RequestVolunteerRecord.query.filter_by(
                request_id=db_req.id, request_category_id=index).all()

            volunteers = []
            vol_ids = []
            for request_volunteer_record in request_volunteer_records:
                volunteers.append(Volunteer.query.get(
                    request_volunteer_record.volunteer_id))
                vol_ids.append(str(request_volunteer_record.volunteer_id))

            member_name = ""
            for member in members:
                member_name += member.first_name + " " + member.last_name + ", "
            member_name = member_name[:-2]
            volunteer_name = ""
            for volunteer in volunteers:
                volunteer_name += volunteer.first_name + " " + volunteer.last_name + ", "
            volunteer_name = volunteer_name[:-2]
            if index == 0:
                formatted_db_requests.append({
                    'request_num':
                    db_req.id,
                    'request_status':
                    RequestStatus.query.get(db_req.status_id).name,
                    'requested_date_display':
                    db_req.requested_date.strftime("%m/%d"),
                    'requested_date_full':
                    db_req.requested_date.strftime("%m/%d/%Y"),
                    'requested_day_of_week':
                    db_req.requested_date.strftime("%A"),
                    'start_time':
                    db_req.initial_pickup_time.strftime("%I:%M %p"),
                    'end_time':
                    db_req.drop_off_time.strftime("%I:%M %p"),
                    'member_name':
                    member_name,
                    'volunteer_name':
                    volunteer_name,
                    'is_volunteer':
                    True,
                    'request_type':
                    RequestType.query.get(db_req.type_id).name,
                    'request_type_id':
                    db_req.type_id,
                    'service_category':
                    ServiceCategory.query.get(db_req.service_category_id).name,
                    'service':
                    Service.query.get(db_req.service_id).name,
                    'created_date':
                    db_req.created_date.strftime("%m/%d/%Y"),
                    'modified_date':
                    db_req.modified_date.strftime("%m/%d/%Y"),
                    'member_numbers':
                    " ".join(member_ids),
                    'volunteer_ids':
                    " ".join(vol_ids)
                })
            elif index == 1:
                formatted_db_requests.append({
                    'request_num':
                    db_req.id,
                    'request_status':
                    RequestStatus.query.get(db_req.status_id).name,
                    'requested_date_display':
                    db_req.requested_date.strftime("%m/%d"),
                    'requested_date_full':
                    db_req.requested_date.strftime("%m/%d/%Y"),
                    'requested_day_of_week':
                    db_req.requested_date.strftime("%A"),
                    'start_time':
                    db_req.start_time.strftime("%I:%M %p"),
                    'end_time':
                    db_req.end_time.strftime("%I:%M %p"),
                    'member_name':
                    member_name,
                    'volunteer_name':
                    volunteer_name,
                    'is_volunteer':
                    True,
                    'request_type':
                    RequestType.query.get(db_req.type_id).name,
                    'request_type_id':
                    db_req.type_id,
                    'service_category':
                    ServiceCategory.query.get(db_req.service_category_id).name,
                    'service':
                    Service.query.get(db_req.service_id).name,
                    'created_date':
                    db_req.created_date.strftime("%m/%d/%Y"),
                    'modified_date':
                    db_req.modified_date.strftime("%m/%d/%Y"),
                    'member_numbers':
                    " ".join(member_ids),
                    'volunteer_ids':
                    " ".join(vol_ids)
                })
            elif index == 2:
                formatted_db_requests.append({
                    'request_num':
                    db_req.id,
                    'request_status':
                    RequestStatus.query.get(db_req.status_id).name,
                    'requested_date_display':
                    db_req.requested_date.strftime("%m/%d"),
                    'requested_date_full':
                    db_req.requested_date.strftime("%m/%d/%Y"),
                    'requested_day_of_week':
                    db_req.requested_date.strftime("%A"),
                    'start_time':
                    db_req.from_time.strftime("%I:%M %p"),
                    'end_time':
                    db_req.until_time.strftime("%I:%M %p"),
                    'member_name':
                    member_name,
                    'volunteer_name':
                    volunteer_name,
                    'is_volunteer':
                    True,
                    'request_type':
                    RequestType.query.get(db_req.type_id).name,
                    'request_type_id':
                    db_req.type_id,
                    'service_category':
                    ServiceCategory.query.get(db_req.service_category_id).name,
                    'service':
                    Service.query.get(db_req.service_id).name,
                    'created_date':
                    db_req.created_date.strftime("%m/%d/%Y"),
                    'modified_date':
                    db_req.modified_date.strftime("%m/%d/%Y"),
                    'member_numbers':
                    " ".join(member_ids),
                    'volunteer_ids':
                    " ".join(vol_ids)
                })

    temp_requests.extend(formatted_db_requests)
    return render_template('admin/request_manager/search_request.html',
                           title='Search Request',
                           form=form,
                           service_providers=service_providers,
                           requests=temp_requests,
                           num_requests=len(temp_requests)
                           )


@ admin.route('/search-request/_delete-request/<int:request_type_id>/<int:request_id>')
@ login_required
@ admin_required
def delete_request(request_type_id, request_id):
    """Delete a request"""
    request_type = ""
    # Transportation Request
    if request_type_id == 0:
        request_type = "Transportation"
        request = TransportationRequest.query.filter_by(id=request_id).first()
    # Office Request
    elif request_type_id == 1:
        request_type = "Office"
        request = OfficeRequest.query.filter_by(id=request_id).first()
    # Member's Home Request
    elif request_type_id == 2:
        request_type = "Member's Home"
        request = MembersHomeRequest.query.filter_by(id=request_id).first()

    members = RequestMemberRecord.query.filter_by(
        request_id=request_id).filter_by(request_category_id=request_type_id).all()
    for member in members:
        db.session.delete(member)
    volunteers = RequestVolunteerRecord.query.filter_by(
        request_id=request_id).filter_by(request_category_id=request_type_id).all()
    for volunteer in volunteers:
        db.session.delete(volunteer)

    db.session.delete(request)
    db.session.commit()

    flash(
        'Successfully deleted request {}'.format(
            request_type + " #" + str(request_id)), 'success')
    return redirect(url_for('admin.search_request'))

# Create a new service request.


@admin.route('/create-request', methods=['GET', 'POST'])
@admin_required
def create_request():
    return render_template('admin/request_manager/create_request.html')


# Create a new Transportation service request.
@admin.route('/create-request/transportation-request/<int:request_id>', methods=['GET', 'POST'])
@admin.route('/create-request/transportation-request', methods=['GET', 'POST'])
@admin_required
def create_transportation_request(request_id=None):
    form = TransportationRequestForm()
    transportation_request = None
    if request_id:
        transportation_request = TransportationRequest.query.filter_by(
            id=request_id).first()
        form = TransportationRequestForm(
            type_id=0,
            status=RequestStatus.query.filter_by(
                id=transportation_request.status_id).first(),
            short_description=transportation_request.short_description,
            date_created=transportation_request.created_date,
            requested_date=transportation_request.requested_date,
            initial_pickup=transportation_request.initial_pickup_time,
            appointment=transportation_request.appointment_time,
            return_pickup=transportation_request.return_pickup_time,
            drop_off=transportation_request.drop_off_time,
            duration=transportation_request.duration_type_id,
            service_category=transportation_request.service_category_id,
            transportation_service=transportation_request.service_id,
            starting_location=transportation_request.starting_address,
            destination=transportation_request.destination_address_id,
            special_instructions=transportation_request.special_instructions,
            follow_up_date=transportation_request.followup_date,
            responsible_staffer=transportation_request.responsible_staffer_id,
            contact_log_priority=ContactLogPriorityType.query.filter_by(
                id=transportation_request.contact_log_priority_id).first(),
            cc_email=transportation_request.cc_email,
            time_flexible=transportation_request.is_date_time_flexible
        )

    form.requesting_member.multiple = True
    form.requesting_member.choices = [
        (member.id, member.first_name + " " + member.last_name)
        for member in Member.query.all()
    ]
    form.service_provider.choices = [
        (volunteer.id, volunteer.first_name + " " + volunteer.last_name)
        for volunteer in Volunteer.query.all()
    ]

    form.duration.choices = [
        (request_duration_type.id, request_duration_type.name)
        for request_duration_type in RequestDurationType.query.all()
    ]
    form.destination.choices = [(address.id,
                                address.name + " - " + address.address1 + (" " + address.address2 if address.address2 else ""))
                                for address in Address.query.all()]
    form.starting_location.choices = [
        (address.id, address.name + " - " + address.address1 +
         (" " + address.address2 if address.address2 else ""))
        for address in Address.query.all()
    ]
    form.special_instructions_list = json.dumps({
        str(member.id): member.volunteer_notes
        for member in Member.query.all()
    })
    form.responsible_staffer.choices = [
        (staffer.id, staffer.first_name + " " + staffer.last_name)
        for staffer in Staffer.query.all()
    ]
    if request_id:
        request_member_records = [member.member_id for member in RequestMemberRecord.query.filter_by(request_id=transportation_request.id,
                                                                                                     request_category_id=0).all()]
        form.requesting_member.data = request_member_records
        request_volunteer_records = [volunteer.volunteer_id for volunteer in RequestVolunteerRecord.query.filter_by(request_id=transportation_request.id,
                                                                                                                    request_category_id=0).all()]
        form.service_provider.data = request_volunteer_records

    if form.validate_on_submit():
        special_input = request.form.get('special_instructions')
        if transportation_request is not None:
            transportation_request.status_id = form.status.data.id
            transportation_request.short_description = form.description.data
            transportation_request.created_date = form.date_created.data
            transportation_request.requested_date = form.requested_date.data
            transportation_request.initial_pickup_time = form.initial_pickup.data
            transportation_request.appointment_time = form.appointment.data
            transportation_request.return_pickup_time = form.return_pickup.data
            transportation_request.drop_off_time = form.drop_off.data
            transportation_request.is_date_time_flexible = form.time_flexible.data
            transportation_request.duration_type_id = form.duration.data
            transportation_request.service_category_id = form.service_category.data.id
            transportation_request.service_id = form.transportation_service.data.id if form.service_category.data.id == 0 else form.covid_service.data.id
            transportation_request.starting_address = form.starting_location.data
            transportation_request.destination_address_id = form.destination.data
            transportation_request.special_instructions = special_input
            transportation_request.followup_date = form.follow_up_date.data
            transportation_request.responsible_staffer_id = form.responsible_staffer.data
            transportation_request.contact_log_priority_id = form.contact_log_priority.data.id
            transportation_request.cc_email = form.person_to_cc.data

            members = RequestMemberRecord.query.filter_by(
                request_id=transportation_request.id).filter_by(request_category_id=0).all()
            for member in members:
                db.session.delete(member)
            volunteers = RequestVolunteerRecord.query.filter_by(
                request_id=transportation_request.id).filter_by(request_category_id=0).all()
            for volunteer in volunteers:
                db.session.delete(volunteer)
            db.session.add(transportation_request)
            db.session.commit()
        else:
            transportation_request = TransportationRequest(
                type_id=0,
                status_id=form.status.data.id,
                short_description=form.description.data,
                created_date=form.date_created.data,
                requested_date=form.requested_date.data,
                initial_pickup_time=form.initial_pickup.data,
                appointment_time=form.appointment.data,
                return_pickup_time=form.return_pickup.data,
                drop_off_time=form.drop_off.data,
                is_date_time_flexible=bool(form.time_flexible.data),
                duration_type_id=form.duration.data,
                service_category_id=form.service_category.data.id,
                service_id=form.transportation_service.data.id if
                form.service_category.data.id == 0 else form.covid_service.data.id,
                starting_address=form.starting_location.data,
                destination_address_id=form.destination.data,
                special_instructions=special_input,
                followup_date=form.follow_up_date.data,
                responsible_staffer_id=form.responsible_staffer.data,
                contact_log_priority_id=form.contact_log_priority.data.id,
                cc_email=form.person_to_cc.data)
            db.session.add(transportation_request)
            db.session.commit()

        requesting_members = request.form.getlist("requesting_member")
        for member in requesting_members:
            record = RequestMemberRecord(request_id=transportation_request.id,
                                         request_category_id=0,
                                         member_id=member)
            db.session.add(record)
            db.session.commit()

        service_providers = request.form.getlist("service_provider")
        for volunteer in service_providers:
            request_volunteer_record = RequestVolunteerRecord(
                request_id=transportation_request.id,
                request_category_id=0,
                volunteer_id=volunteer,
                status_id=1,
                staffer_id=1,
                updated_datetime=form.date_created.data)
            db.session.add(request_volunteer_record)
            db.session.commit()

        if request_id:
            flash('Successfully editied transportation request # {}'.
                  format(request_id), 'success')
        else:
            flash('Successfully submitted a transportation request', 'success')
        return redirect(url_for('admin.search_request'))

    volunteer_info = []
    for volunteer in Volunteer.query.all():
        vol_status = VolunteerType.query.get(volunteer.type_id).name
        address = Address.query.get(volunteer.primary_address_id)
        street_address = address.address1
        location = address.city
        volunteer_info.append(
            (volunteer.first_name + " " + volunteer.last_name,
            street_address,
            location,
            volunteer.primary_phone_number,
            volunteer.preferred_contact_method,
            vol_status,
            str(volunteer.email_address),
            str(volunteer.is_fully_vetted),
            round(volunteer.rating, 2))
        )

    return render_template('admin/request_manager/transportation_request.html',
                           title='Transportation Request',
                           form=form,
                           volunteer_data=json.dumps(volunteer_info))

@admin.route('/create-request/send-emails', methods=['GET'])
def send_vols_emails():
    """
    Email sending endpoint
    action_type -- type of action being done (send request, confirmation, etc)
    req_id -- the request id to pull data from
    req_type -- Transportation, Member's home, etc
    Fourth param onwards: volunteer emails
    """
    params = list(request.args)
    #TODO: Determine email template based on this variable
    action_type = params[0]
    req_id = int(params[1])
    req_type = params[2]
    emails = []
    for i in range(3, len(params)):
        emails.append(params[i])

    for vol_email in emails:
        if RequestMemberRecord.query.filter_by(request_id=req_id).first() is None:
            get_queue().enqueue(
                send_email,
                recipient=vol_email,
                subject="Admin Request",
                template="admin/email/blank_email"
            )
        else:
            for member_rec in RequestMemberRecord.query.filter_by(request_id=req_id):
                if req_type == "Transportation":
                    req_data = TransportationRequest.query.get(req_id)
                elif req_type == "Member\'s Home":
                    req_data = MembersHomeRequest.query.get(req_id)
                elif req_type == "Office Time":
                    req_data = OfficeTimeRequest.query.get(req_id)
                '''
                In the future the get_queue function would be moved into each of the if statements above.

                Within each function call a unique template would be supplied.
                '''
                get_queue().enqueue(
                    send_email,
                    recipient=vol_email,
                    subject=f"New {req_type} Request",
                    template="admin/email/send_request",
                    volunteer=Volunteer.get(RequestMemberRecord.query.get(req_id).volunteer_id),
                    member=Members.get(member_rec.member_id),
                    request_type=req_type,
                    request_data=req_data,
                    address=Address
                )
    return jsonify("OK")

@admin.route('/create-request/office-time-request/<int:request_id>', methods=['GET', 'POST'])
@admin.route('/create-request/office-time-request', methods=['GET', 'POST'])
@admin_required
def create_office_time_request(request_id=None):
    form = OfficeTimeRequestForm()
    office_time_request = None
    if request_id:
        office_time_request = OfficeRequest.query.filter_by(
            id=request_id).first()
        form = OfficeTimeRequestForm(
            type_id=1,
            description=office_time_request.short_description,
            date_created=office_time_request.created_date,
            requested_date=office_time_request.requested_date,
            start_time=office_time_request.start_time,
            end_time=office_time_request.end_time,
            high_priority=office_time_request.is_high_priority,
            responsible_staffer=office_time_request.responsible_staffer_id,
            person_to_cc=office_time_request.cc_email,
            service_category=ServiceCategory.query.filter_by(
                id=office_time_request.service_category_id).first(),
            office_time_service=Service.query.filter_by(
                id=office_time_request.service_id),
            status=RequestStatus.query.filter_by(
                id=office_time_request.status_id),
            contact_log_priority=ContactLogPriorityType.query.filter_by(
                id=office_time_request.contact_log_priority_id)
        )
    form.requesting_member.multiple = True
    form.requesting_member.choices = [
        (member.id, member.first_name + " " + member.last_name)
        for member in Member.query.all()
    ]
    form.service_provider.choices = [
        (volunteer.id, volunteer.first_name + " " + volunteer.last_name)
        for volunteer in Volunteer.query.all()
    ]
    form.special_instructions_list = json.dumps({
        str(member.id): member.volunteer_notes
        for member in Member.query.all()
    })
    form.responsible_staffer.choices = [
        (staffer.id, staffer.first_name + " " + staffer.last_name)
        for staffer in Staffer.query.all()
    ]
    if request_id:
        request_member_records = [member.member_id for member in RequestMemberRecord.query.filter_by(request_id=office_time_request.id,
                                                                                                     request_category_id=1).all()]
        form.requesting_member.data = request_member_records
        request_volunteer_records = [volunteer.volunteer_id for volunteer in RequestVolunteerRecord.query.filter_by(request_id=office_time_request.id,
                                                                                                                    request_category_id=1).all()]
        form.service_provider.data = request_volunteer_records
    if form.validate_on_submit():
        special_input = request.form.get('special_instructions')
        if office_time_request is not None:
            office_time_request.type_id = 1
            office_time_request.status_id = form.status.data.id
            office_time_request.short_description = form.description.data
            office_time_request.created_date = form.date_created.data
            office_time_request.requested_date = form.requested_date.data
            office_time_request.start_time = form.start_time.data
            office_time_request.end_time = form.end_time.data
            office_time_request.is_high_priority = form.high_priority.data
            office_time_request.service_category_id = form.service_category.data.id
            office_time_request.service_id = form.office_time_service.data.id if form.service_category.data.id == 6 else form.covid_service.data.id
            office_time_request.special_instructions = special_input
            office_time_request.responsible_staffer_id = form.responsible_staffer.data
            office_time_request.contact_log_priority_id = form.contact_log_priority.data.id
            office_time_request.cc_email = form.person_to_cc.data

            members = RequestMemberRecord.query.filter_by(
                request_id=office_time_request.id).filter_by(request_category_id=1).all()
            for member in members:
                db.session.delete(member)
            volunteers = RequestVolunteerRecord.query.filter_by(
                request_id=office_time_request.id).filter_by(request_category_id=1).all()
            for volunteer in volunteers:
                db.session.delete(volunteer)
            db.session.add(office_time_request)
            db.session.commit()

        else:
            office_time_request = OfficeRequest(
                type_id=1,
                status_id=form.status.data.id,
                short_description=form.description.data,
                created_date=form.date_created.data,
                requested_date=form.requested_date.data,
                start_time=form.start_time.data,
                end_time=form.end_time.data,
                is_high_priority=form.high_priority.data,
                service_category_id=form.service_category.data.id,
                service_id=form.office_time_service.data.id if
                form.service_category.data.id == 6 else form.covid_service.data.id,
                special_instructions=special_input,
                responsible_staffer_id=form.responsible_staffer.data,
                contact_log_priority_id=form.contact_log_priority.data.id,
                cc_email=form.person_to_cc.data)
            db.session.add(office_time_request)
            db.session.commit()

        requesting_members = request.form.getlist("requesting_member")
        for member in requesting_members:
            request_member_record = RequestMemberRecord(
                request_id=office_time_request.id,
                request_category_id=1,
                member_id=member
            )
            db.session.add(request_member_record)
            db.session.commit()

        service_providers = request.form.getlist("service_provider")
        for volunteer in service_providers:
            request_volunteer_record = RequestVolunteerRecord(
                request_id=office_time_request.id,
                request_category_id=1,
                volunteer_id=volunteer,
                status_id=1,
                staffer_id=1,
                updated_datetime=form.date_created.data)
            db.session.add(request_volunteer_record)
            db.session.commit()

        if request_id:
            flash('Successfully edited office time request # {}'.
                  format(request_id), 'success')
        else:
            flash('Successfully submitted am office time request', 'success')
        return redirect(url_for('admin.search_request'))

    volunteer_info = []
    for volunteer in Volunteer.query.all():
        vol_status = VolunteerType.query.get(volunteer.type_id).name
        address = Address.query.get(volunteer.primary_address_id)
        street_address = address.address1
        location = address.city
        volunteer_info.append(
            (volunteer.first_name + " " + volunteer.last_name,
            street_address,
            location,
            volunteer.primary_phone_number,
            volunteer.preferred_contact_method,
            vol_status,
            str(volunteer.email_address),
            str(volunteer.is_fully_vetted),
            round(volunteer.rating, 2))
        )

    return render_template('admin/request_manager/office_time_request.html',
                           title='Office Time Request',
                           form=form,
                           volunteer_data=json.dumps(volunteer_info))

@admin.route('/create-request/members-home-request/<int:request_id>', methods=['GET', 'POST'])
@admin.route('create-request/members-home-request', methods=['GET', 'POST'])
@admin_required
@login_required
def create_members_home_request(request_id=None):
    form = MembersHomeRequestForm()
    members_home_request = None
    if request_id:
        members_home_request = MembersHomeRequest.query.filter_by(
            id=request_id).first()
        form = MembersHomeRequestForm(
            description=members_home_request.short_description,
            date_created=members_home_request.created_date,
            requested_date=members_home_request.requested_date,
            time_from=members_home_request.from_time,
            time_until=members_home_request.until_time,
            time_flexible=members_home_request.is_date_time_flexible,
            follow_up_date=members_home_request.followup_date,
            responsible_staffer=members_home_request.responsible_staffer_id,
            person_to_cc=members_home_request.cc_email,
            cc_email=form.person_to_cc.data)

    form.requesting_member.multiple = True
    form.requesting_member.choices = [
        (member.id, member.first_name + " " + member.last_name)
        for member in Member.query.all()
    ]

    form.service_provider.choices = [
        (volunteer.id, volunteer.first_name + " " + volunteer.last_name)
        for volunteer in Volunteer.query.all()
    ]

    form.home_location.choices = [(1, "Home")]

    form.special_instructions_list = json.dumps({
        str(member.id): member.volunteer_notes
        for member in Member.query.all()
    })

    form.responsible_staffer.choices = [
        (staffer.id, staffer.first_name + " " + staffer.last_name)
        for staffer in Staffer.query.all()
    ]

    if request_id:
        request_member_records = [
            member.member_id for member in
            RequestMemberRecord.query.filter_by(request_id=members_home_request.id,
                                                request_category_id=2).all()]
        form.requesting_member.data = request_member_records
        request_volunteer_records = [
            volunteer.volunteer_id for volunteer in
            RequestVolunteerRecord.query.filter_by(request_id=members_home_request.id,
                                                   request_category_id=2).all()]
        form.service_provider.data = request_volunteer_records
        form.status.data = RequestStatus.query.filter_by(
            id=members_home_request.status_id).first()
        form.service_category.data = ServiceCategory.query.filter_by(
            id=members_home_request.service_category_id).first()
        service = Service.query.filter_by(
            id=members_home_request.service_id).first()
        if form.service_category.data == 3:
            form.tech_services.data = service
        elif form.service_category.data == 4:
            form.prof_home_services.data = service
        elif form.service_category.data == 5:
            form.prof_support_services.data = service
        elif form.service_category.data == 7:
            form.vol_home_services.data = service
        elif form.service_category.data == 8:
            form.vol_support_services.data = service
        form.contact_log_priority.data = ContactLogPriorityType.query.filter_by(
            id=members_home_request.contact_log_priority_id).first()

    if form.validate_on_submit():
        special_input = request.form.get('special_instructions')
        if members_home_request is not None:
            members_home_request.type_id = 2
            members_home_request.status_id = request.form.get("status")
            members_home_request.short_description = form.description.data
            members_home_request.created_date = form.date_created.data
            members_home_request.requested_date = form.requested_date.data
            members_home_request.from_time = form.time_from.data
            members_home_request.until_time = form.time_until.data
            members_home_request.is_date_time_flexible = form.time_flexible.data
            members_home_request.service_category_id = form.service_category.data.id
            members_home_request.service_id = (form.tech_services.data.id if
                                               form.service_category.data.id == 3
                                               else (form.prof_home_services.data.id
                                                     if form.service_category.data.id == 4
                                                     else (form.prof_support_services if
                                                           form.service_category.data.id == 5
                                                           else (form.vol_home_services.data.id
                                                                 if form.service_category.data.id == 7
                                                                 else form.vol_support_services.data.id))))
            members_home_request.special_instructions = special_input
            members_home_request.followup_date = form.follow_up_date.data
            members_home_request.responsible_staffer_id = form.responsible_staffer.data
            members_home_request.contact_log_priority_id = request.form.get(
                "contact_log_priority")
            members_home_request.cc_email = form.person_to_cc.data

            members = RequestMemberRecord.query.filter_by(
                request_id=members_home_request.id).filter_by(request_category_id=2).all()
            for member in members:
                db.session.delete(member)
            volunteers = RequestVolunteerRecord.query.filter_by(
                request_id=members_home_request.id).filter_by(request_category_id=2).all()
            for volunteer in volunteers:
                db.session.delete(volunteer)
            db.session.add(members_home_request)
            db.session.commit()
        else:
            members_home_request = MembersHomeRequest(
                type_id=2,
                status_id=form.status.data.id,
                short_description=form.description.data,
                created_date=form.date_created.data,
                requested_date=form.requested_date.data,
                from_time=form.time_from.data,
                until_time=form.time_until.data,
                is_date_time_flexible=form.time_flexible.data,
                service_category_id=form.service_category.data.id,
                service_id=form.tech_services.data.id if
                form.service_category.data.id == 3 else (form.prof_home_services.data.id if form.service_category.data.id == 4 else (form.prof_support_services if form.service_category.data.id == 5 else (form.vol_home_services.data.id if form.service_category.data.id == 7 else form.vol_support_services.data.id))),
                special_instructions=special_input,
                followup_date=form.follow_up_date.data,
                responsible_staffer_id=form.responsible_staffer.data,
                contact_log_priority_id=form.contact_log_priority.data.id,
                cc_email=form.person_to_cc.data)
            db.session.add(members_home_request)
            db.session.commit()

        requesting_members = request.form.getlist("requesting_member")
        for member in requesting_members:
            record = RequestMemberRecord(request_id=members_home_request.id,
                                         request_category_id=2,
                                         member_id=member)
            db.session.add(record)
            db.session.commit()

        service_providers = request.form.getlist("service_provider")
        for volunteer in service_providers:
            request_volunteer_record = RequestVolunteerRecord(
                request_id=members_home_request.id,
                request_category_id=2,
                volunteer_id=volunteer,
                status_id=1,
                staffer_id=1,
                updated_datetime=form.date_created.data)
            db.session.add(request_volunteer_record)
            db.session.commit()

        if request_id:
            flash('Successfully edited member\'s home request # {}'.
                  format(request_id), 'success')
        else:
            flash('Successfully submitted a new member\'s home request', 'success')
        return redirect(url_for('admin.search_request'))

    volunteer_info = []
    for volunteer in Volunteer.query.all():
        vol_status = VolunteerType.query.get(volunteer.type_id).name
        address = Address.query.get(volunteer.primary_address_id)
        street_address = address.address1
        location = address.city
        volunteer_info.append(
            (volunteer.first_name + " " + volunteer.last_name,
            street_address,
            location,
            volunteer.primary_phone_number,
            volunteer.preferred_contact_method,
            vol_status,
            str(volunteer.email_address),
            str(volunteer.is_fully_vetted),
            round(volunteer.rating, 2))
        )

    return render_template('admin/request_manager/members_home_request.html',
                           title='Members Home Request',
                           form=form,
                           volunteer_data=json.dumps(volunteer_info))


@admin.route('/invite-member', methods=['GET', 'POST'])
@admin.route('/invite-member/<int:member_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def invite_member(member_id=None):
    """Page for member management."""
    member = None
    form = MemberManager()
    if member_id is not None:
        member = Member.query.filter_by(id=member_id).first()
        # get the address information from Address table
        primary_address = Address.query.filter_by(
            id=member.primary_address_id).first()
        primary_address1 = primary_address.address1
        primary_address2 = primary_address.address2
        primary_city = primary_address.city
        primary_state = primary_address.state
        primary_zip_code = primary_address.zipcode
        primary_country = primary_address.country
        secondary_address = None
        if member.secondary_address_id is not None:
            secondary_address = Address.query.filter_by(
                id=member.secondary_address_id).first()
            secondary_address1 = secondary_address.address1
            secondary_address2 = secondary_address.address2
            secondary_city = secondary_address.city
            secondary_state = secondary_address.state
            secondary_zip_code = secondary_address.zipcode
            secondary_country = secondary_address.country

        form = MemberManager(
            first_name=member.first_name,
            middle_initial=member.middle_initial,
            last_name=member.last_name,
            preferred_name=member.preferred_name,
            salutation=member.salutation,
            gender=member.gender,
            birthdate=member.birthdate,
            primary_address1=primary_address1,
            primary_address2=primary_address2,
            primary_city=primary_city,
            primary_state=primary_state,
            primary_zip_code=primary_zip_code,
            primary_country=primary_country,
            secondary_address1=secondary_address1 if secondary_address else None,
            secondary_address2=secondary_address2 if secondary_address else None,
            secondary_city=secondary_city if secondary_address else None,
            secondary_state=secondary_state if secondary_address else None,
            secondary_zip_code=secondary_zip_code if secondary_address else None,
            secondary_country=secondary_country if secondary_address else None,
            primary_phone_number=member.primary_phone_number,
            secondary_phone_number=member.secondary_phone_number,
            email_address=member.email_address,
            preferred_contact_method=member.preferred_contact_method,
            emergency_contact_name=member.emergency_contact_name,
            emergency_contact_relationship=member.
            emergency_contact_relationship,
            emergency_contact_phone_number=member.
            emergency_contact_phone_number,
            emergency_contact_email_address=member.
            emergency_contact_email_address,
            membership_expiration_date=member.membership_expiration_date,
            member_number=member.member_number,
            volunteer_notes=member.volunteer_notes,
            staffer_notes=member.staffer_notes)

    if form.validate_on_submit():
        secondary_address = False
        if (form.secondary_as_primary_checkbox.data):
            address = Address(
                name=form.first_name.data + " " + form.last_name.data,
                address1=form.secondary_address1.data,
                address2=form.secondary_address2.data,
                city=form.secondary_city.data,
                state=form.secondary_state.data,
                zipcode=form.secondary_zip_code.data,
                country=form.secondary_country.data)
            if form.primary_address1.data:
                secondary_address = Address(
                    name=form.first_name.data + " " + form.last_name.data,
                    address1=form.primary_address1.data,
                    address2=form.primary_address2.data,
                    city=form.primary_city.data,
                    state=form.primary_state.data,
                    zipcode=form.primary_zip_code.data,
                    country=form.primary_country.data)
            if form.secondary_metro_area.data:
                metro = MetroArea(name=form.secondary_metro_area.data)
        else:
            address = Address(name=form.first_name.data + " " +
                              form.last_name.data,
                              address1=form.primary_address1.data,
                              address2=form.primary_address2.data,
                              city=form.primary_city.data,
                              state=form.primary_state.data,
                              zipcode=form.primary_zip_code.data,
                              country=form.primary_country.data)
            if form.secondary_address1.data:
                secondary_address = Address(
                    name=form.first_name.data + " " + form.last_name.data,
                    address1=form.secondary_address1.data,
                    address2=form.secondary_address2.data,
                    city=form.secondary_city.data,
                    state=form.secondary_state.data,
                    zipcode=form.secondary_zip_code.data,
                    country=form.secondary_country.data)
            if form.primary_metro_area.data:
                metro = MetroArea(name=form.primary_metro_area.data)

        db.session.add(address)
        db.session.commit()
        if metro:
            db.session.add(metro)
            db.session.commit()
        if secondary_address:
            db.session.add(secondary_address)
            db.session.commit()

        if member is not None:
            updated_member = member
            updated_member.salutation = form.salutation.data
            updated_member.primary_address_id = address.id
            updated_member.secondary_address_id = secondary_address.id if secondary_address else None
            updated_member.metro_area_id = metro.id
            updated_member.first_name = form.first_name.data
            updated_member.middle_initial = form.middle_initial.data
            updated_member.last_name = form.last_name.data
            updated_member.preferred_name = form.preferred_name.data
            updated_member.gender = form.gender.data
            updated_member.birthdate = form.birthdate.data
            updated_member.primary_phone_number = form.primary_phone_number.data
            updated_member.secondary_phone_number = form.secondary_phone_number.data
            updated_member.email_address = form.email_address.data
            updated_member.preferred_contact_method = form.preferred_contact_method.data
            updated_member.emergency_contact_name = form.emergency_contact_name.data
            updated_member.emergency_contact_phone_number = form.emergency_contact_phone_number.data
            updated_member.emergency_contact_email_address = form.emergency_contact_email_address.data
            updated_member.emergency_contact_relationship = form.emergency_contact_relationship.data
            updated_member.membership_expiration_date = form.membership_expiration_date.data
            updated_member.member_number = form.member_number.data
            updated_member.volunteer_notes = form.volunteer_notes.data
            updated_member.staffer_notes = form.staffer_notes.data
            db.session.add(updated_member)
            db.session.commit()
            flash(
                'Member {} successfully updated'.format(form.first_name.data),
                'success')
        else:
            member = Member(
                salutation=form.salutation.data,
                primary_address_id=address.id,
                secondary_address_id=secondary_address.id
                if secondary_address else None,
                metro_area_id=metro.id,
                first_name=form.first_name.data,
                middle_initial=form.middle_initial.data,
                last_name=form.last_name.data,
                preferred_name=form.preferred_name.data,
                gender=form.gender.data,
                birthdate=form.birthdate.data,
                primary_phone_number=form.primary_phone_number.data,
                secondary_phone_number=form.secondary_phone_number.data,
                email_address=form.email_address.data,
                preferred_contact_method=form.preferred_contact_method.data,
                emergency_contact_name=form.emergency_contact_name.data,
                emergency_contact_phone_number=form.
                emergency_contact_phone_number.data,
                emergency_contact_email_address=form.
                emergency_contact_email_address.data,
                emergency_contact_relationship=form.
                emergency_contact_relationship.data,
                membership_expiration_date=form.membership_expiration_date.
                data,
                member_number=form.member_number.data,
                volunteer_notes=form.volunteer_notes.data,
                staffer_notes=form.staffer_notes.data)
            db.session.add(member)
            db.session.commit()
            flash(
                'Member {} successfully added'.format(form.first_name.data),
                'success')
        return redirect(url_for('admin.people_manager'))
    return render_template('admin/people_manager/member_manager.html',
                           form=form)


@admin.route('/invite-volunteer', methods=['GET', 'POST'])
@admin.route('/invite-volunteer/<int:volunteer_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def invite_volunteer(volunteer_id=None):
    """Invites a user to create a volunteer account"""
    # for editing existing Volunteer profiles
    volunteer = None
    form = VolunteerManager()
    choices = []
    service_categories = dict()
    category_to_indices = dict()
    for idx, c in enumerate(Service.query.order_by('category_id')):
        if c.category_id not in category_to_indices:
            category_to_indices[c.category_id] = []
        category_to_indices[c.category_id].append(idx+1)
        choices.append((c.id, c.name))
    for category in ServiceCategory.query.order_by('id'):
        service_categories[category.id] = category.name

    form.provided_services.choices = choices
    if volunteer_id is not None:
        volunteer = Volunteer.query.filter_by(id=volunteer_id).first()
        primary_address = Address.query.filter_by(
            id=volunteer.primary_address_id).first()
        primary_address1 = primary_address.address1
        primary_address2 = primary_address.address2
        primary_city = primary_address.city
        primary_state = primary_address.state
        primary_zip_code = primary_address.zipcode
        primary_country = primary_address.country
        secondary_address = None
        if volunteer.secondary_address_id is not None:
            secondary_address = Address.query.filter_by(
                id=volunteer.secondary_address_id).first()
            secondary_address1 = secondary_address.address1
            secondary_address2 = secondary_address.address2
            secondary_city = secondary_address.city
            secondary_state = secondary_address.state
            secondary_zip_code = secondary_address.zipcode
            secondary_country = secondary_address.country
        form = VolunteerManager(
            salutation=volunteer.salutation,
            first_name=volunteer.first_name,
            middle_initial=volunteer.middle_initial,
            last_name=volunteer.last_name,
            gender=volunteer.gender,
            birthdate=volunteer.birthdate,
            preferred_name=volunteer.preferred_name,
            primary_address1=primary_address1,
            primary_address2=primary_address2,
            primary_city=primary_city,
            primary_state=primary_state,
            primary_zip_code=primary_zip_code,
            primary_country=primary_country,
            secondary_address1=secondary_address1 if secondary_address else None,
            secondary_address2=secondary_address2 if secondary_address else None,
            secondary_city=secondary_city if secondary_address else None,
            secondary_state=secondary_state if secondary_address else None,
            secondary_zip_code=secondary_zip_code if secondary_address else None,
            secondary_country=secondary_country if secondary_address else None,
            emergency_contact_name=volunteer.emergency_contact_name,
            emergency_contact_relationship=volunteer.
            emergency_contact_relationship,
            emergency_contact_phone_number=volunteer.
            emergency_contact_phone_number,
            emergency_contact_email_address=volunteer.
            emergency_contact_email_address,
            primary_phone_number=volunteer.primary_phone_number,
            secondary_phone_number=volunteer.secondary_phone_number,
            email_address=volunteer.email_address,
            preferred_contact_method=volunteer.preferred_contact_method,
            notes=volunteer.general_notes)
        form.provided_services.choices = choices
        form.provided_services.data = [
            p.service_id for p in ProvidedService.query.filter_by(volunteer_id=volunteer_id)]

    service_ids = []
    if form.validate_on_submit():
        service_ids = request.form.getlist("provided_services")
        secondary_address = False
        if (form.secondary_as_primary_checkbox.data):
            address = Address(
                name=form.first_name.data + " " + form.last_name.data,
                address1=form.secondary_address1.data,
                address2=form.secondary_address2.data,
                city=form.secondary_city.data,
                state=form.secondary_state.data,
                zipcode=form.secondary_zip_code.data,
                country=form.secondary_country.data)
            if form.primary_address1.data:
                secondary_address = Address(
                    name=form.first_name.data + " " + form.last_name.data,
                    address1=form.primary_address1.data,
                    address2=form.primary_address2.data,
                    city=form.primary_city.data,
                    state=form.primary_state.data,
                    zipcode=form.primary_zip_code.data,
                    country=form.primary_country.data)
            if form.secondary_metro_area.data:
                metro = MetroArea(name=form.secondary_metro_area.data)
        else:
            address = Address(name=form.first_name.data + " " +
                              form.last_name.data,
                              address1=form.primary_address1.data,
                              address2=form.primary_address2.data,
                              city=form.primary_city.data,
                              state=form.primary_state.data,
                              zipcode=form.primary_zip_code.data,
                              country=form.primary_country.data)
            if form.secondary_address1.data:
                secondary_address = Address(
                    name=form.first_name.data + " " + form.last_name.data,
                    address1=form.secondary_address1.data,
                    address2=form.secondary_address2.data,
                    city=form.secondary_city.data,
                    state=form.secondary_state.data,
                    zipcode=form.secondary_zip_code.data,
                    country=form.secondary_country.data)
            if form.primary_metro_area.data:
                metro = MetroArea(name=form.primary_metro_area.data)

        db.session.add(address)
        db.session.commit()
        if metro:
            db.session.add(metro)
            db.session.commit()
        if secondary_address:
            db.session.add(secondary_address)
            db.session.commit()

        if volunteer is not None:
            updated_volunteer = volunteer
            updated_volunteer.salutation = form.salutation.data
            updated_volunteer.primary_address_id = address.id
            updated_volunteer.secondary_address_id = secondary_address.id if secondary_address else None
            updated_volunteer.first_name = form.first_name.data
            updated_volunteer.middle_initial = form.middle_initial.data
            updated_volunteer.last_name = form.last_name.data
            updated_volunteer.preferred_name = form.preferred_name.data
            updated_volunteer.gender = form.gender.data
            updated_volunteer.birthdate = form.birthdate.data
            updated_volunteer.primary_phone_number = form.primary_phone_number.data
            updated_volunteer.secondary_phone_number = form.secondary_phone_number.data
            updated_volunteer.email_address = form.email_address.data
            updated_volunteer.preferred_contact_method = form.preferred_contact_method.data
            updated_volunteer.emergency_contact_name = form.emergency_contact_name.data
            updated_volunteer.emergency_contact_phone_number = form.emergency_contact_phone_number.data
            updated_volunteer.emergency_contact_email_address = form.emergency_contact_email_address.data
            updated_volunteer.emergency_contact_relationship = form.emergency_contact_relationship.data
            updated_volunteer.general_notes = form.notes.data
            db.session.add(updated_volunteer)
            db.session.commit()
            volunteer = updated_volunteer
            flash(
                'Volunteer {} successfully updated'.format(
                    form.first_name.data), 'success')
        else:
            availability = Availability()
            db.session.add(availability)
            db.session.commit()

            volunteer = Volunteer(
                salutation=form.salutation.data,
                primary_address_id=address.id,
                secondary_address_id=secondary_address.id
                if secondary_address else None,
                first_name=form.first_name.data,
                middle_initial=form.middle_initial.data,
                last_name=form.last_name.data,
                preferred_name=form.preferred_name.data,
                gender=form.gender.data,
                birthdate=form.birthdate.data,
                primary_phone_number=form.primary_phone_number.data,
                email_address=form.email_address.data,
                preferred_contact_method=form.preferred_contact_method.data,
                emergency_contact_name=form.emergency_contact_name.data,
                emergency_contact_phone_number=form.
                emergency_contact_phone_number.data,
                emergency_contact_email_address=form.
                emergency_contact_email_address.data,
                emergency_contact_relationship=form.
                emergency_contact_relationship.data,
                type_id=1,  # What should we set volunteer type id as???
                rating=1,  # Why is this not null before the user even creates a volunteer?
                availability_id=availability.id,
                general_notes=form.notes.data)
            db.session.add(volunteer)
            db.session.commit()
            flash(
                'Volunteer {} successfully added'.format(
                    form.first_name.data),
                'success')

        need_to_be_deleted = []
        for provided_service in ProvidedService.query.filter_by(volunteer_id=volunteer.id):
            if provided_service.service_id not in service_ids:
                need_to_be_deleted.append(provided_service)
        for service in need_to_be_deleted:
            db.session.delete(service)
            db.session.commit()
        for service in service_ids:
            if not ProvidedService.query.filter_by(service_id=service, volunteer_id=volunteer.id).first():
                db.session.add(ProvidedService(
                    service_id=service, volunteer_id=volunteer.id))
                db.session.commit()

        flash('Volunteer {} successfully invited'.format(form.first_name.data),
              'form-success')

        return redirect(url_for('admin.people_manager', active='volunteer'))
    return render_template('admin/people_manager/volunteer_manager.html',
                           form=form,
                           service_categories=service_categories,
                           category_to_indices=category_to_indices)


@admin.route('/invite-contractor', methods=['GET', 'POST'])
@admin.route('/invite-contractor/<int:local_resource_id>',
             methods=['GET', 'POST'])
@login_required
@admin_required
def invite_contractor(local_resource_id=None):
    """Page for contactor management."""
    local_resource = None
    form = ContractorManager()
    if local_resource_id is not None:
        local_resource = LocalResource.query.filter_by(
            id=local_resource_id).first()
        primary_address = Address.query.filter_by(
            id=local_resource.address_id).first()
        primary_address1 = primary_address.address1
        primary_address2 = primary_address.address2
        primary_city = primary_address.city
        primary_state = primary_address.state
        primary_zip_code = primary_address.zipcode
        primary_country = primary_address.country
        form = ContractorManager(
            first_name=local_resource.contact_first_name,
            middle_initial=local_resource.contact_middle_initial,
            last_name=local_resource.contact_last_name,
            salutation=local_resource.contact_salutation,
            company_name=local_resource.company_name,
            primary_country=primary_country,
            primary_address1=primary_address1,
            primary_address2=primary_address2,
            primary_city=primary_city,
            primary_state=primary_state,
            primary_zip_code=primary_zip_code,
            primary_phone_number=local_resource.primary_phone_number,
            email_address=local_resource.email_address,
            preferred_contact_method=local_resource.preferred_contact_method,
            website=local_resource.website)

    if form.validate_on_submit():
        address = Address(name=form.company_name.data,
                          address1=form.primary_address1.data,
                          address2=form.primary_address2.data,
                          city=form.primary_city.data,
                          state=form.primary_state.data,
                          zipcode=form.primary_zip_code.data,
                          country=form.primary_country.data)
        db.session.add(address)
        db.session.commit()

        if local_resource is not None:
            updated_local_resource = local_resource
            updated_local_resource.address_id = address.id
            updated_local_resource.contact_first_name = form.first_name.data
            updated_local_resource.contact_middle_initial = form.middle_initial.data
            updated_local_resource.contact_last_name = form.last_name.data
            updated_local_resource.contaqct_salutation = form.salutation.data
            updated_local_resource.company_name = form.company_name.data
            updated_local_resource.primary_phone_number = form.primary_phone_number.data
            updated_local_resource.secondary_phone_number = form.secondary_phone_number.data
            updated_local_resource.email_address = form.email_address.data
            updated_local_resource.preferred_contact_method = form.preferred_contact_method.data
            updated_local_resource.website = form.website.data
            db.session.add(updated_local_resource)
            db.session.commit()
            flash(
                'Local Resource {} successfully updated'.format(
                    form.company_name.data), 'success')
        else:
            availability = Availability()
            db.session.add(availability)
            db.session.commit()

            local_resource = LocalResource(
                address_id=address.id,
                contact_first_name=form.first_name.data,
                contact_middle_initial=form.middle_initial.data,
                contact_last_name=form.last_name.data,
                contact_salutation=form.salutation.data,
                company_name=form.company_name.data,
                primary_phone_number=form.primary_phone_number.data,
                secondary_phone_number=form.secondary_phone_number.data,
                email_address=form.email_address.data,
                preferred_contact_method=form.preferred_contact_method.data,
                website=form.website.data,
                availability_id=availability.id)
            db.session.add(local_resource)
            db.session.commit()
            flash(
                'Local Resource {} successfully added'.format(
                    form.company_name.data), 'success')

        return redirect(url_for('admin.people_manager', active='local-resource'))

    return render_template('admin/people_manager/contractor_manager.html',
                           form=form)


@admin.route('/add-volunteer-services/<int:volunteer_id>',
             methods=['GET', 'POST'])
@login_required
@admin_required
def add_volunteer_services(volunteer_id=None):
    """Page for volunteer's services management."""

    volunteer = Volunteer.query.filter_by(id=volunteer_id).first()
    volunteer_name = volunteer.first_name + " " + volunteer.last_name
    form = EditServicesVolunteerCanProvide()
    choices = []
    service_categories = dict()
    category_to_indices = dict()
    for idx, c in enumerate(Service.query.order_by('category_id')):
        if c.category_id not in category_to_indices:
            category_to_indices[c.category_id] = []
        category_to_indices[c.category_id].append(idx+1)
        choices.append((c.id, c.name))
    for category in ServiceCategory.query.order_by('id'):
        service_categories[category.id] = category.name
    form.provided_services.choices = choices

    if volunteer_id:
        form.provided_services.choices = choices
        form.provided_services.data = [
            p.service_id for p in ProvidedService.query.filter_by(volunteer_id=volunteer_id)]

    if form.validate_on_submit():
        service_ids = request.form.getlist("provided_services")
        need_to_be_deleted = []
        for provided_service in ProvidedService.query.filter_by(volunteer_id=volunteer_id):
            if provided_service.service_id not in service_ids:
                need_to_be_deleted.append(provided_service)
        for service in need_to_be_deleted:
            db.session.delete(service)
            db.session.commit()
        for service in service_ids:
            if not ProvidedService.query.filter_by(service_id=service,
                                                   volunteer_id=volunteer_id).first():
                db.session.add(ProvidedService(
                    service_id=service, volunteer_id=volunteer_id))
                db.session.commit()
        flash(
            'Services Volunteer can provide {} successfully updated'.format(
                volunteer.last_name), 'success')
        return redirect(url_for('admin.people_manager', active='volunteer'))
    return render_template('admin/people_manager/volunteer_services.html',
                           form=form, service_categories=service_categories,
                           category_to_indices=category_to_indices,
                           volunteer_name=volunteer_name)


@ admin.route('/add-local-resource-review/<int:local_resource_id>',
              methods=['GET', 'POST'])
@ login_required
@ admin_required
def add_local_resource_review(local_resource_id=None):
    """Page for review management."""

    localResource = LocalResource.query.filter_by(id=local_resource_id).first()
    reviews = Review.query.filter_by(lr_id=local_resource_id).all()

    form = AddReview()
    form.review_identity.label = Label(
        "review_identity", "Local Resource " + localResource.company_name)

    if form.validate_on_submit():
        review = Review(
            reviewer_name=form.reviewer_name.data,
            rating=form.rating.data,
            review_text=form.review_text.data,
            lr_id=local_resource_id,
            date_created=form.date_created.data)
        db.session.add(review)
        db.session.commit()

        flash(
            'Review for Local Resource {} successfully added'.format(
                localResource.company_name), 'success')
        return redirect(url_for('admin.people_manager', active='local-resource'))

    return render_template('admin/people_manager/review.html', form=form, reviews=reviews)


@ admin.route('/add-local-resource-review/_delete-review/<int:review_id>')
@ login_required
@ admin_required
def delete_review(review_id):
    """Delete a review."""
    review = Review.query.filter_by(id=review_id).first()
    local_resource_id = review.lr_id
    db.session.delete(review)
    db.session.commit()
    flash(
        'Successfully deleted review by {}'.format(
            review.reviewer_name), 'success')
    return redirect(url_for('admin.add_local_resource_review', local_resource_id=local_resource_id))


@admin.route('/add-volunteer-vetting/<int:volunteer_id>',
             methods=['GET', 'POST'])
@login_required
@admin_required
def add_volunteer_vetting(volunteer_id=None):
    """Page for volunteer vetting management."""

    volunteer = Volunteer.query.filter_by(id=volunteer_id).first()

    form = AddVetting(
        is_fully_vetted=volunteer.is_fully_vetted,
        vetting_notes=volunteer.vetting_notes)
    form.vetting_identity.label = Label("vetting_identity", "Volunteer " + volunteer.first_name + " " +
                                        volunteer.last_name)

    if form.validate_on_submit():
        updated_volunteer = volunteer
        updated_volunteer.is_fully_vetted = form.is_fully_vetted.data
        updated_volunteer.vetting_notes = form.vetting_notes.data
        db.session.add(updated_volunteer)
        db.session.commit()

        flash(
            'Vetting for Volunteer {} successfully updated'.format(
                volunteer.last_name), 'success')
        return redirect(url_for('admin.people_manager', active='volunteer'))

    return render_template('admin/people_manager/volunteer_vetting.html', form=form)


@admin.route('/add-availability-volunteer/<int:volunteer_id>',
             methods=['GET', 'POST'])
@login_required
@admin_required
def add_availability_volunteer(volunteer_id=None):
    """Page for availability management."""

    volunteer = Volunteer.query.filter_by(id=volunteer_id).first()
    availability_id = volunteer.availability_id

    availability = Availability.query.filter_by(id=availability_id).first()
    form = AddAvailability(
        availability_monday=availability.availability_monday,
        backup_monday=availability.backup_monday,
        availability_tuesday=availability.availability_tuesday,
        backup_tuesday=availability.backup_tuesday,
        availability_wednesday=availability.availability_wednesday,
        backup_wednesday=availability.backup_wednesday,
        availability_thursday=availability.availability_thursday,
        backup_thursday=availability.backup_thursday,
        availability_friday=availability.availability_friday,
        backup_friday=availability.backup_friday,
        availability_saturday=availability.availability_saturday,
        backup_saturday=availability.backup_saturday,
        availability_sunday=availability.availability_sunday,
        backup_sunday=availability.backup_sunday)
    form.availability_identity.label = Label("availability_identity", "Volunteer " + volunteer.first_name + " " +
                                             volunteer.last_name)

    if form.validate_on_submit():
        updated_availability = availability
        updated_availability.availability_monday = form.availability_monday.data
        updated_availability.backup_monday = form.backup_monday.data
        updated_availability.availability_tuesday = form.availability_tuesday.data
        updated_availability.backup_tuesday = form.backup_tuesday.data
        updated_availability.availability_wednesday = form.availability_wednesday.data
        updated_availability.backup_wednesday = form.backup_wednesday.data
        updated_availability.availability_thursday = form.availability_thursday.data
        updated_availability.backup_thursday = form.backup_thursday.data
        updated_availability.availability_friday = form.availability_friday.data
        updated_availability.backup_friday = form.backup_friday.data
        updated_availability.availability_saturday = form.availability_saturday.data
        updated_availability.backup_saturday = form.backup_saturday.data
        updated_availability.availability_sunday = form.availability_sunday.data
        updated_availability.backup_sunday = form.backup_sunday.data
        db.session.add(updated_availability)
        db.session.commit()

        flash(
            'Availability for Volunteer {} successfully updated'.format(
                volunteer.last_name), 'success')
        return redirect(url_for('admin.people_manager', active='volunteer'))

    return render_template('admin/people_manager/availability.html', form=form, active='volunteer')


@ admin.route('/add-availability-local-resource/<int:local_resource_id>',
              methods=['GET', 'POST'])
@ login_required
@ admin_required
def add_availability_local_resource(local_resource_id=None):
    """Page for availability management."""

    localResource = LocalResource.query.filter_by(id=local_resource_id).first()
    availability_id = localResource.availability_id

    availability = Availability.query.filter_by(id=availability_id).first()
    form = AddAvailability(
        availability_monday=availability.availability_monday,
        backup_monday=availability.backup_monday,
        availability_tuesday=availability.availability_tuesday,
        backup_tuesday=availability.backup_tuesday,
        availability_wednesday=availability.availability_wednesday,
        backup_wednesday=availability.backup_wednesday,
        availability_thursday=availability.availability_thursday,
        backup_thursday=availability.backup_thursday,
        availability_friday=availability.availability_friday,
        backup_friday=availability.backup_friday,
        availability_saturday=availability.availability_saturday,
        backup_saturday=availability.backup_saturday,
        availability_sunday=availability.availability_sunday,
        backup_sunday=availability.backup_sunday)
    form.availability_identity.label = Label(
        "availability_identity", "Local Resource " + localResource.company_name)

    if form.validate_on_submit():
        updated_availability = availability
        updated_availability.availability_monday = form.availability_monday.data
        updated_availability.backup_monday = form.backup_monday.data
        updated_availability.availability_tuesday = form.availability_tuesday.data
        updated_availability.backup_tuesday = form.backup_tuesday.data
        updated_availability.availability_wednesday = form.availability_wednesday.data
        updated_availability.backup_wednesday = form.backup_wednesday.data
        updated_availability.availability_thursday = form.availability_thursday.data
        updated_availability.backup_thursday = form.backup_thursday.data
        updated_availability.availability_friday = form.availability_friday.data
        updated_availability.backup_friday = form.backup_friday.data
        updated_availability.availability_saturday = form.availability_saturday.data
        updated_availability.backup_saturday = form.backup_saturday.data
        updated_availability.availability_sunday = form.availability_sunday.data
        updated_availability.backup_sunday = form.backup_sunday.data
        db.session.add(updated_availability)
        db.session.commit()

        flash(
            'Availability for Local Resource {} successfully updated'.format(
                localResource.company_name), 'success')
        return redirect(url_for('admin.people_manager', active='local-resource'))

    return render_template('admin/people_manager/availability.html', form=form, active='local-resource')

@ admin.route('/people-manager/_delete-member/<int:member_id>')
@ login_required
@ admin_required
def delete_member(member_id):
    """Delete a member."""
    member = Member.query.filter_by(id=member_id).first()
    db.session.delete(member)
    db.session.commit()
    flash(
        'Successfully deleted member {}'.format(member.first_name + ' ' +
                                                member.last_name), 'success')
    return redirect(url_for('admin.people_manager'))


@ admin.route('/people-manager/_delete-volunteer/<int:volunteer_id>')
@ login_required
@ admin_required
def delete_volunteer(volunteer_id):
    """Delete a volunteer."""
    volunteer = Volunteer.query.filter_by(id=volunteer_id).first()
    db.session.delete(volunteer)
    db.session.commit()
    flash(
        'Successfully deleted volunteer {}'.format(volunteer.first_name + ' ' +
                                                   volunteer.last_name),
        'success')
    return redirect(url_for('admin.people_manager', active='volunteer'))


@ admin.route('/people-manager/_delete-local-resource/<int:local_resource_id>')
@ login_required
@ admin_required
def delete_local_resource(local_resource_id):
    """Delete a local resource."""
    localResource = LocalResource.query.filter_by(id=local_resource_id).first()
    db.session.delete(localResource)
    db.session.commit()
    flash(
        'Successfully deleted local resource {}'.format(
            localResource.company_name), 'success')
    return redirect(url_for('admin.people_manager', active='local-resource'))


@ admin.route('/services')
@ login_required
@ admin_required
def registered_services():
    """Manage services."""
    services = Service.query.all()
    return render_template('admin/system_manager/registered_services.html',
                           services=services)


# @admin.route('/services/<int:service_id>', methods=['GET', 'POST'])
@ admin.route('/services/info/<int:service_id>', methods=['GET', 'POST'])
@ login_required
@ admin_required
def service_info(service_id):
    """View a service's profile."""
    service = Service.query.filter_by(id=service_id).first()
    form = EditServiceForm(name=service.name, category=service.category)
    if form.validate_on_submit():
        updated_service = service
        updated_service.name = form.name.data
        updated_service.category = form.category.data
        db.session.add(updated_service)
        db.session.commit()
        flash('Service {} successfully updated'.format(form.name.data),
              'form-success')
        return redirect(url_for('admin.registered_services'))
    if service is None:
        abort(404)
    return render_template('admin/system_manager/manage_service.html',
                           service=service,
                           form=form)


@admin.route('/services/_delete/<int:service_id>')
@login_required
@admin_required
def delete_service(service_id):
    """Delete a service."""
    service = Service.query.filter_by(id=service_id).first()
    db.session.delete(service)
    db.session.commit()
    flash('Successfully deleted service %s.' % service.name, 'success')
    return redirect(url_for('admin.registered_services'))


@admin.route('/new-service', methods=['GET', 'POST'])
@login_required
@admin_required
def new_service():
    """Create a new service."""
    form = EditServiceForm()
    if form.validate_on_submit():
        service = Service(name=form.name.data,
                          category_id=form.category.data.id)
        db.session.add(service)
        db.session.commit()
        flash('Service {} successfully created'.format(service.name),
              'success')
        return redirect(url_for('admin.registered_services'))

    return render_template('admin/system_manager/manage_service.html',
                           form=form)


@admin.route('/service-categories')
@login_required
@admin_required
def registered_service_categories():
    """Manage service categories."""
    categories = ServiceCategory.query.all()
    category_to_services = dict()
    for c in categories:
        service_list = [service.name for service in Service.query.filter_by(
            category_id=c.id).all()]
        category_to_services[c.name] = service_list
    return render_template('admin/system_manager/registered_service_categories.html',
                           categories=categories, services=category_to_services)


@admin.route('/service-categories/info/<int:category_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def service_category_info(category_id):
    """View a service's profile."""
    category = ServiceCategory.query.filter_by(id=category_id).first()
    request_type = RequestType.query.filter_by(
        id=category.request_type_id).first()
    form = EditServiceCategoryForm(
        name=category.name, request_type=request_type)
    if form.validate_on_submit():
        updated_service_category = category
        updated_service_category.name = form.name.data
        updated_service_category.request_type_id = form.request_type.data.id
        db.session.add(updated_service_category)
        db.session.commit()
        flash('Service Catgeory {} successfully updated'.format(form.name.data),
              'form-success')
        return redirect(url_for('admin.registered_service_categories'))
    if category is None:
        abort(404)
    return render_template('admin/system_manager/manage_service_category.html',
                           category=category,
                           form=form)


@admin.route('/new-service-category', methods=['GET', 'POST'])
@login_required
@admin_required
def new_service_category():
    """Create a new service category."""
    form = EditServiceCategoryForm()
    if form.validate_on_submit():
        category = ServiceCategory(name=form.name.data,
                                   request_type_id=form.request_type.data.id)
        db.session.add(category)
        db.session.commit()
        flash('Service Category {} successfully created'.format(category.name),
              'success')
        return redirect(url_for('admin.registered_service_categories'))

    return render_template('admin/system_manager/manage_service_category.html',
                           form=form)


@admin.route('/service-categories/_delete/<int:category_id>')
@login_required
@admin_required
def delete_service_category(category_id):
    """Delete a service category."""
    services = Service.query.filter_by(category_id=category_id).all()
    for service in services:
        db.session.delete(service)
    category = ServiceCategory.query.filter_by(id=category_id).first()
    db.session.delete(category)
    db.session.commit()
    flash('Successfully deleted service category %s.' %
          category.name, 'success')
    return redirect(url_for('admin.registered_service_categories'))

####
# Metro Areas
####


@admin.route('/metro-areas')
@login_required
@admin_required
def registered_metro_areas():
    """Manage metro areas."""
    metro_areas = MetroArea.query.all()
    return render_template('admin/system_manager/registered_metro_areas.html',
                           metro_areas=metro_areas)


# @admin.route('/metro-areas/<int:metro_area_id>', methods=['GET', 'POST'])
@admin.route('/metro-areas/info/<int:metro_area_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def metro_area_info(metro_area_id):
    """View a metro area's profile."""
    metro_area = MetroArea.query.filter_by(id=metro_area_id).first()
    form = EditMetroAreaForm(name=metro_area.name)
    if form.validate_on_submit():
        updated_metro_area = metro_area
        updated_metro_area.name = form.name.data
        db.session.add(updated_metro_area)
        db.session.commit()
        flash('Metro Area {} successfully updated'.format(form.name.data),
              'form-success')
        return redirect(url_for('admin.registered_metro_areas'))
    if metro_area is None:
        abort(404)
    return render_template('admin/system_manager/manage_metro_area.html',
                           metro_area=metro_area,
                           form=form)


@admin.route('/metro-areas/<int:metro_area_id>/_delete')
@login_required
@admin_required
def delete_metro_area(metro_area_id):
    """Delete a metro area.."""
    metro_area = MetroArea.query.filter_by(id=metro_area_id).first()
    db.session.delete(metro_area)
    db.session.commit()
    flash('Successfully deleted metro area %s.' % metro_area.name, 'success')
    return redirect(url_for('admin.registered_metro_areas'))


@admin.route('/new-metro-area', methods=['GET', 'POST'])
@login_required
@admin_required
def new_metro_area():
    """Create a new metro area."""
    form = EditMetroAreaForm()
    if form.validate_on_submit():
        metro_area = MetroArea(name=form.name.data)
        db.session.add(metro_area)
        db.session.commit()
        flash('Metro Area {} successfully created'.format(metro_area.name),
              'success')
        return redirect(url_for('admin.registered_metro_areas'))

    return render_template('admin/system_manager/manage_metro_area.html',
                           form=form)

####
# Destination Addresses
####


@admin.route('/destination-addresses')
@login_required
@admin_required
def registered_destination_addresses():
    """Manage destination addresses."""
    # TODO: Change addresses to be queried from standard destinations and not addresses table
    addresses = Address.query.all()
    return render_template('admin/system_manager/registered_destination_addresses.html',
                           addresses=addresses)


@admin.route('/destination-addresses/info/<int:destination_address_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def destination_address_info(destination_address_id):
    """View a destination address's profile."""
    destination_address = Address.query.filter_by(
        id=destination_address_id).first()
    form = EditDestinationAddressForm(name=destination_address.name,
                                      address1=destination_address.address1, address2=destination_address.address2,
                                      city=destination_address.city,
                                      state=destination_address.state,
                                      country=destination_address.country,
                                      zip_code=destination_address.zipcode)
    if form.validate_on_submit():
        updated_destination_address = destination_address
        updated_destination_address.name = form.name.data
        updated_destination_address.address1 = form.address1.data
        updated_destination_address.address2 = form.address2.data
        updated_destination_address.city = form.city.data
        updated_destination_address.state = form.state.data
        updated_destination_address.country = form.country.data
        updated_destination_address.zipcode = form.zip_code.data
        db.session.add(updated_destination_address)
        db.session.commit()
        flash('Destination Address {} successfully updated'.format(form.name.data),
              'form-success')
        return redirect(url_for('admin.registered_destination_addresses'))
    if destination_address is None:
        abort(404)
    return render_template('admin/system_manager/manage_destination_address.html',
                           destination_address=destination_address,
                           form=form)


@admin.route('/new-destination-address', methods=['GET', 'POST'])
@login_required
@admin_required
def new_destination_address():
    """Create a new destination address."""
    form = EditDestinationAddressForm()
    if form.validate_on_submit():
        destination_address = Address(
            name=form.name.data, address1=form.address1.data, address2=form.address2.data,
            city=form.city.data, state=form.state.data,
            country=form.country.data, zipcode=form.zip_code.data)
        db.session.add(destination_address)
        db.session.commit()
        flash('Destination Address {} successfully created'.format(destination_address.name),
              'success')
        return redirect(url_for('admin.registered_destination_addresses'))

    return render_template('admin/system_manager/manage_destination_address.html',
                           form=form)


@admin.route('/destination-addresses/<int:destination_address_id>/_delete')
@login_required
@admin_required
def delete_destination_address(destination_address_id):
    """Delete a destination address."""
    destination_address = Address.query.filter_by(
        id=destination_address_id).first()
    db.session.delete(destination_address)
    db.session.commit()
    flash('Successfully deleted destination address %s.' %
          destination_address.name, 'success')
    return redirect(url_for('admin.registered_destination_addresses'))


@admin.route("/generate-report", methods=['GET', 'POST'])
@login_required
@admin_required
def generate_report():
    pdf_form = GeneratePdfForm()
    if pdf_form.validate_on_submit():
        file_name = pdf_form.file_name.data
        import pandas as pd
        import numpy as np
        from jinja2 import Environment, FileSystemLoader
        from weasyprint import HTML

        data = pd.DataFrame()
        data['Col1'] = np.arange(1, 50)
        data['Col2'] = np.arange(2, 51)

        env = Environment(loader=FileSystemLoader('.'))
        template = env.get_template("./app/templates/admin/report.html")
        template_vars = {"title": "Love Living at Home",
                         "data": data.to_html()}
        html_out = template.render(template_vars)
        HTML(string=html_out).write_pdf(
            "./app/reports/" + file_name + ".pdf", stylesheets=["./app/assets/styles/report.css"])
        try:
            return send_file("reports/" + file_name + ".pdf", as_attachment=True)
        except FileNotFoundError:
            flash('Failed to generate report.', 'error')
            abort(404)
    return render_template('admin/system_manager/generate_report.html', form=pdf_form)
