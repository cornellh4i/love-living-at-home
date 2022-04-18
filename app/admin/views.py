import json
import sys
from operator import __truediv__

from flask import (Blueprint, abort, flash, redirect, render_template, request,
                   send_file, url_for, jsonify)
from flask_login import current_user, login_required
from flask_rq import get_queue

from app import db
from app.admin.forms import (AddAvailability,
                             AddVetting, AddReview, AddVacation, ChangeAccountTypeForm,
                             ChangeUserEmailForm, CompleteServiceRequestForm, LocalResourceManager,
                             EditMetroAreaForm, EditServiceForm, EditServiceCategoryForm,
                             EditDestinationAddressForm,
                             InviteUserForm, MakeMonthlyRepeatingCopiesForm, MakeYearlyRepeatingCopiesForm, MemberManager, MembersHomeRequestForm,
                             NewUserForm, SearchRequestForm, TransportationRequestForm,
                             VolunteerManager, OfficeTimeRequestForm, GeneratePdfForm,
                             EditServicesVolunteerCanProvide, MakeIndividualCopiesForm,
                             MakeDailyRepeatingCopiesForm,
                             MakeWeeklyRepeatingCopiesForm, MakeCopiesWithoutDateForm, AddMemberVolunteer)
from app.decorators import admin_required
from app.email import send_email
from app.models import (Address, Availability, EditableHTML, LocalResource, Member, MetroArea,
                        ProvidedService, MembersHomeRequest, TransportationRequest, Role, Vacation,
                        Service, ServiceCategory, Staffer, User, Volunteer, RequestMemberRecord, Review)
from app.models.transportation_request import ContactLogPriorityType, RequestDurationType, RequestStatus, RequestType
from app.models.request_volunteer_record import RequestVolunteerRecord
from app.models.office_request import OfficeRequest
from datetime import timedelta
from wtforms.fields.core import Label

from datetime import date, datetime
from dateutil.relativedelta import relativedelta, MO, TU, WE, TH, FR, SA, SU

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
    active = "member"
    if 'active' in request.args:
        active = request.args['active']
    data = {'active': active}
    members = Member.query.all()
    volunteers = Volunteer.query.all()
    local_resources = LocalResource.query.all()
    return render_template('admin/people_manager/layouts/base.html',
                           members=members,
                           volunteers=volunteers,
                           local_resources=local_resources,
                           data=data)


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


def get_request_obj(request_type_id, request_id):
    """
    Return request object based on the request_type_id and request_id

    request_type_id: 0,1,or 2 where 0 is Transportation, 1 is Office Time,
                    2 is Member's Home
    request_id: int
    """
    # Transportation Request
    if request_type_id == 0:
        request_obj = TransportationRequest.query.filter_by(
            id=request_id).first()
    # Office Request
    elif request_type_id == 1:
        request_obj = OfficeRequest.query.filter_by(id=request_id).first()
    # Member's Home Request
    elif request_type_id == 2:
        request_obj = MembersHomeRequest.query.filter_by(id=request_id).first()
    return request_obj


def get_request_obj(request_type_id, request_id):
    """
    Return request object based on the request_type_id and request_id

    request_type_id: 0,1,or 2 where 0 is Transportation, 1 is Office Time,
                    2 is Member's Home
    request_id: int
    """
    # Transportation Request
    if request_type_id == 0:
        request_obj = TransportationRequest.query.filter_by(
            id=request_id).first()
    # Office Request
    elif request_type_id == 1:
        request_obj = OfficeRequest.query.filter_by(id=request_id).first()
    # Member's Home Request
    elif request_type_id == 2:
        request_obj = MembersHomeRequest.query.filter_by(id=request_id).first()
    return request_obj


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
    ]
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
                    db_req.requested_date.strftime(
                        "%m/%d/%Y") if db_req.requested_date else "",
                    'requested_date_full':
                    db_req.requested_date.strftime(
                        "%m/%d/%Y") if db_req.requested_date else "",
                    'requested_day_of_week':
                    db_req.requested_date.strftime(
                        "%A") if db_req.requested_date else "",
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
                    db_req.requested_date.strftime(
                        "%m/%d/%Y") if db_req.requested_date else "",
                    'requested_date_full':
                    db_req.requested_date.strftime(
                        "%m/%d/%Y") if db_req.requested_date else "",
                    'requested_day_of_week':
                    db_req.requested_date.strftime(
                        "%A") if db_req.requested_date else "",
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
                    db_req.requested_date.strftime(
                        "%m/%d/%Y") if db_req.requested_date else "",
                    'requested_date_full':
                    db_req.requested_date.strftime(
                        "%m/%d/%Y") if db_req.requested_date else "",
                    'requested_day_of_week':
                    db_req.requested_date.strftime(
                        "%A") if db_req.requested_date else "",
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

########################## Make Copy in Search Request ########################


def make_individual_transportation_copies(
        request_obj, new_service_dates, new_service_times,
        include_selected_service_providers, include_service_request_status):
    """
    Make individual copy(s) of the selected transportation request
    """
    for i in range(len(new_service_dates)):
        transportation_request = TransportationRequest(
            type_id=0,
            status_id=request_obj.status_id if include_service_request_status else 0,
            requested_date=new_service_dates[i],
            short_description=request_obj.short_description,
            initial_pickup_time=new_service_times[i],
            appointment_time=request_obj.appointment_time,
            return_pickup_time=request_obj.return_pickup_time,
            drop_off_time=(datetime.combine(new_service_dates[i], new_service_times[i]) + (datetime.combine(new_service_dates[i], request_obj.drop_off_time) -
                                                                                           datetime.combine(new_service_dates[i], request_obj.initial_pickup_time))).time(),
            is_date_time_flexible=request_obj.is_date_time_flexible,
            duration_type_id=request_obj.duration_type_id,
            service_category_id=request_obj.service_category_id,
            service_id=request_obj.service_id,
            starting_address=request_obj.starting_address,
            destination_address_id=request_obj.destination_address_id,
            special_instructions=request_obj.special_instructions,
            followup_date=request_obj.followup_date,
            responsible_staffer_id=request_obj.responsible_staffer_id,
            contact_log_priority_id=request_obj.contact_log_priority_id,
            cc_email=request_obj.cc_email)
        db.session.add(transportation_request)
        db.session.commit()

        members = RequestMemberRecord.query.filter_by(
            request_id=request_obj.id).filter_by(request_category_id=0).all()
        for member in members:
            record = RequestMemberRecord(request_id=transportation_request.id,
                                         request_category_id=0,
                                         member_id=member.member_id)
            db.session.add(record)
            db.session.commit()
        if include_selected_service_providers:
            volunteers = RequestVolunteerRecord.query.filter_by(
                request_id=request_obj.id).filter_by(request_category_id=0).all()
            for volunteer in volunteers:
                request_volunteer_record = RequestVolunteerRecord(
                    request_id=transportation_request.id,
                    request_category_id=0,
                    volunteer_id=volunteer.volunteer_id,
                    status_id=1,
                    staffer_id=1,
                    updated_datetime=datetime.utcnow().date())
                db.session.add(request_volunteer_record)
                db.session.commit()


def make_individual_office_copies(
    request_obj, new_service_dates, new_service_times,
    include_selected_service_providers, include_service_request_status
):
    """
    Make individual copy(s) of the selected office time request
    """
    for i in range(len(new_service_dates)):
        office_request = OfficeRequest(
            type_id=1,
            status_id=request_obj.status_id if include_service_request_status else 0,
            short_description=request_obj.short_description,
            requested_date=new_service_dates[i],
            start_time=new_service_times[i],
            end_time=(datetime.combine(new_service_dates[i], new_service_times[i]) + (datetime.combine(new_service_dates[i], request_obj.end_time) -
                                                                                      datetime.combine(new_service_dates[i], request_obj.start_time))).time(),
            is_high_priority=request_obj.is_high_priority,
            service_category_id=request_obj.service_category_id,
            service_id=request_obj.service_id,
            special_instructions=request_obj.special_instructions,
            responsible_staffer_id=request_obj.responsible_staffer_id,
            contact_log_priority_id=request_obj.contact_log_priority_id,
            cc_email=request_obj.cc_email
        )
        db.session.add(office_request)
        db.session.commit()
        members = RequestMemberRecord.query.filter_by(
            request_id=request_obj.id).filter_by(request_category_id=1).all()
        for member in members:
            record = RequestMemberRecord(request_id=office_request.id,
                                         request_category_id=1,
                                         member_id=member.member_id)
            db.session.add(record)
            db.session.commit()
        if include_selected_service_providers:
            volunteers = RequestVolunteerRecord.query.filter_by(
                request_id=request_obj.id).filter_by(request_category_id=1).all()
            for volunteer in volunteers:
                request_volunteer_record = RequestVolunteerRecord(
                    request_id=office_request.id,
                    request_category_id=1,
                    volunteer_id=volunteer.volunteer_id,
                    status_id=1,
                    staffer_id=1,
                    updated_datetime=datetime.utcnow().date())
                db.session.add(request_volunteer_record)
                db.session.commit()


def make_individual_members_home_copies(
    request_obj, new_service_dates, new_service_times,
    include_selected_service_providers, include_service_request_status
):
    """
    Make individual copy(s) of the selected Member's Home request
    """
    for i in range(len(new_service_dates)):
        members_home_request = MembersHomeRequest(
            type_id=2,
            status_id=request_obj.status_id if include_service_request_status else 0,
            short_description=request_obj.short_description,
            requested_date=new_service_dates[i],
            from_time=new_service_times[i],
            until_time=(datetime.combine(new_service_dates[i], new_service_times[i]) + (datetime.combine(new_service_dates[i], request_obj.until_time) -
                                                                                        datetime.combine(new_service_dates[i], request_obj.from_time))).time(),
            is_date_time_flexible=request_obj.is_date_time_flexible,
            service_category_id=request_obj.service_category_id,
            service_id=request_obj.service_id,
            special_instructions=request_obj.special_instructions,
            followup_date=request_obj.followup_date,
            responsible_staffer_id=request_obj.responsible_staffer_id,
            contact_log_priority_id=request_obj.contact_log_priority_id,
            cc_email=request_obj.cc_email
        )
        db.session.add(members_home_request)
        db.session.commit()
        members = RequestMemberRecord.query.filter_by(
            request_id=request_obj.id).filter_by(request_category_id=2).all()
        for member in members:
            record = RequestMemberRecord(request_id=members_home_request.id,
                                         request_category_id=2,
                                         member_id=member.member_id)
            db.session.add(record)
            db.session.commit()
        if include_selected_service_providers:
            volunteers = RequestVolunteerRecord.query.filter_by(
                request_id=request_obj.id).filter_by(request_category_id=2).all()
            for volunteer in volunteers:
                request_volunteer_record = RequestVolunteerRecord(
                    request_id=members_home_request.id,
                    request_category_id=2,
                    volunteer_id=volunteer.volunteer_id,
                    status_id=1,
                    staffer_id=1,
                    updated_datetime=datetime.utcnow().date())
                db.session.add(request_volunteer_record)
                db.session.commit()


def make_individual_copies(
        request_type_id, request_obj, new_service_dates, new_service_times,
        include_selected_service_providers, include_service_request_status):
    """
    Make individual copies of the selected request
    """
    if request_type_id == 0:
        make_individual_transportation_copies(
            request_obj, new_service_dates, new_service_times,
            include_selected_service_providers, include_service_request_status)
        return
    elif request_type_id == 1:
        make_individual_office_copies(
            request_obj, new_service_dates, new_service_times,
            include_selected_service_providers, include_service_request_status
        )
        return
    elif request_type_id == 2:
        make_individual_members_home_copies(
            request_obj, new_service_dates, new_service_times,
            include_selected_service_providers, include_service_request_status
        )
        return


def make_transportation_copies_without_date(request_obj, number_of_copies,
                                            include_selected_service_providers, include_service_request_status):
    """
    Make copies of selected transportation request without date
    """
    for _ in range(number_of_copies):
        transportation_request = TransportationRequest(
            type_id=0,
            status_id=request_obj.status_id if include_service_request_status else 0,
            requested_date=None,
            short_description=request_obj.short_description,
            initial_pickup_time=request_obj.initial_pickup_time,
            appointment_time=request_obj.appointment_time,
            return_pickup_time=request_obj.return_pickup_time,
            drop_off_time=request_obj.drop_off_time,
            is_date_time_flexible=request_obj.is_date_time_flexible,
            duration_type_id=request_obj.duration_type_id,
            service_category_id=request_obj.service_category_id,
            service_id=request_obj.service_id,
            starting_address=request_obj.starting_address,
            destination_address_id=request_obj.destination_address_id,
            special_instructions=request_obj.special_instructions,
            followup_date=request_obj.followup_date,
            responsible_staffer_id=request_obj.responsible_staffer_id,
            contact_log_priority_id=request_obj.contact_log_priority_id,
            cc_email=request_obj.cc_email)
        db.session.add(transportation_request)
        db.session.commit()

        members = RequestMemberRecord.query.filter_by(
            request_id=request_obj.id).filter_by(request_category_id=0).all()
        for member in members:
            record = RequestMemberRecord(request_id=transportation_request.id,
                                         request_category_id=0,
                                         member_id=member.member_id)
            db.session.add(record)
            db.session.commit()
        if include_selected_service_providers:
            volunteers = RequestVolunteerRecord.query.filter_by(
                request_id=request_obj.id).filter_by(request_category_id=0).all()
            for volunteer in volunteers:
                request_volunteer_record = RequestVolunteerRecord(
                    request_id=transportation_request.id,
                    request_category_id=0,
                    volunteer_id=volunteer.volunteer_id,
                    status_id=1,
                    staffer_id=1,
                    updated_datetime=datetime.utcnow().date())
                db.session.add(request_volunteer_record)
                db.session.commit()


def make_office_copies_without_date(request_obj, number_of_copies,
                                    include_selected_service_providers, include_service_request_status):
    """
    Make copies of selected office time request without date
    """
    for _ in range(number_of_copies):
        office_request = OfficeRequest(
            type_id=1,
            status_id=request_obj.status_id if include_service_request_status else 0,
            short_description=request_obj.short_description,
            requested_date=None,
            start_time=request_obj.start_time,
            end_time=request_obj.end_time,
            is_high_priority=request_obj.is_high_priority,
            service_category_id=request_obj.service_category_id,
            service_id=request_obj.service_id,
            special_instructions=request_obj.special_instructions,
            responsible_staffer_id=request_obj.responsible_staffer_id,
            contact_log_priority_id=request_obj.contact_log_priority_id,
            cc_email=request_obj.cc_email
        )
        db.session.add(office_request)
        db.session.commit()
        members = RequestMemberRecord.query.filter_by(
            request_id=request_obj.id).filter_by(request_category_id=1).all()
        for member in members:
            record = RequestMemberRecord(request_id=office_request.id,
                                         request_category_id=1,
                                         member_id=member.member_id)
            db.session.add(record)
            db.session.commit()
        if include_selected_service_providers:
            volunteers = RequestVolunteerRecord.query.filter_by(
                request_id=request_obj.id).filter_by(request_category_id=1).all()
            for volunteer in volunteers:
                request_volunteer_record = RequestVolunteerRecord(
                    request_id=office_request.id,
                    request_category_id=1,
                    volunteer_id=volunteer.volunteer_id,
                    status_id=1,
                    staffer_id=1,
                    updated_datetime=datetime.utcnow().date())
                db.session.add(request_volunteer_record)
                db.session.commit()


def make_members_home_copies_without_date(request_obj, number_of_copies,
                                          include_selected_service_providers, include_service_request_status):
    """
    Make copies of selected member's home request without date
    """
    for _ in range(number_of_copies):
        members_home_request = MembersHomeRequest(
            type_id=2,
            status_id=request_obj.status_id if include_service_request_status else 0,
            short_description=request_obj.short_description,
            requested_date=None,
            from_time=request_obj.from_time,
            until_time=request_obj.until_time,
            is_date_time_flexible=request_obj.is_date_time_flexible,
            service_category_id=request_obj.service_category_id,
            service_id=request_obj.service_id,
            special_instructions=request_obj.special_instructions,
            followup_date=request_obj.followup_date,
            responsible_staffer_id=request_obj.responsible_staffer_id,
            contact_log_priority_id=request_obj.contact_log_priority_id,
            cc_email=request_obj.cc_email
        )
        db.session.add(members_home_request)
        db.session.commit()
        members = RequestMemberRecord.query.filter_by(
            request_id=request_obj.id).filter_by(request_category_id=2).all()
        for member in members:
            record = RequestMemberRecord(request_id=members_home_request.id,
                                         request_category_id=2,
                                         member_id=member.member_id)
            db.session.add(record)
            db.session.commit()
        if include_selected_service_providers:
            volunteers = RequestVolunteerRecord.query.filter_by(
                request_id=request_obj.id).filter_by(request_category_id=2).all()
            for volunteer in volunteers:
                request_volunteer_record = RequestVolunteerRecord(
                    request_id=members_home_request.id,
                    request_category_id=2,
                    volunteer_id=volunteer.volunteer_id,
                    status_id=1,
                    staffer_id=1,
                    updated_datetime=datetime.utcnow().date())
                db.session.add(request_volunteer_record)
                db.session.commit()


def make_copies_without_date(
        request_type_id, request_obj, number_of_copies,
        include_selected_service_providers, include_service_request_status):
    """
    Make copies of the selected request without date
    """
    # Transportation Request
    if request_type_id == 0:
        make_transportation_copies_without_date(request_obj, number_of_copies,
                                                include_selected_service_providers, include_service_request_status)
        return
    # Office Request
    elif request_type_id == 1:
        make_office_copies_without_date(request_obj, number_of_copies,
                                        include_selected_service_providers, include_service_request_status)
        return
    # Member's Home Request
    elif request_type_id == 2:
        make_members_home_copies_without_date(request_obj, number_of_copies,
                                              include_selected_service_providers, include_service_request_status)
        return


def make_daily_repeating_copies(is_every_weekday, make_daily_repeating_copies_form, new_service_date,
                                new_service_time, request_type_id, request_obj, weekdays):
    """
    Make daily repeating copies
    """
    if not is_every_weekday:
        if make_daily_repeating_copies_form.end_after_2_1.data:
            end_after = make_daily_repeating_copies_form.end_after_2_1.data
            number_of_days = make_daily_repeating_copies_form.every_number_of_days.data
            new_service_dates = [
                new_service_date + timedelta(days=number_of_days*(i+1)) for i in range(end_after)]
            new_service_times = [new_service_time for _ in range(end_after)]
            make_individual_copies(request_type_id, request_obj, new_service_dates, new_service_times,
                                   make_daily_repeating_copies_form.include_selected_service_providers.data,
                                   make_daily_repeating_copies_form.include_service_request_status.data)
        else:
            end_by = make_daily_repeating_copies_form.end_by_2_1.data
            date = new_service_date
            number_of_days = make_daily_repeating_copies_form.every_number_of_days.data
            number_of_copies = 0
            new_service_dates = []
            date = new_service_date + timedelta(days=number_of_days)
            while date < end_by and number_of_copies < 50:
                new_service_dates.append(date)
                number_of_copies += 1
                date = new_service_date + \
                    timedelta(days=number_of_days*(number_of_copies+1))
            new_service_times = [new_service_time]*len(new_service_dates)
            make_individual_copies(request_type_id, request_obj, new_service_dates, new_service_times,
                                   make_daily_repeating_copies_form.include_selected_service_providers.data,
                                   make_daily_repeating_copies_form.include_service_request_status.data)
    elif is_every_weekday:
        # Make one copy in the selected new service date and time
        make_individual_copies(request_type_id, request_obj, [new_service_date], [new_service_time],
                               make_daily_repeating_copies_form.include_selected_service_providers.data,
                               make_daily_repeating_copies_form.include_service_request_status.data)
        ####
        if make_daily_repeating_copies_form.end_after_2_1.data:
            end_after = make_daily_repeating_copies_form.end_after_2_1.data
            counter = 1
            date = new_service_date+timedelta(days=1)
            if date.weekday() not in weekdays:
                date += timedelta(days=7-date.weekday())
            while counter < end_after:
                make_individual_copies(request_type_id, request_obj, [date], [new_service_time],
                                       make_daily_repeating_copies_form.include_selected_service_providers.data,
                                       make_daily_repeating_copies_form.include_service_request_status.data)
                date += timedelta(days=1)
                if date.weekday() not in weekdays:
                    date += timedelta(days=7-date.weekday())
                counter += 1
        elif make_daily_repeating_copies_form.end_by_2_1.data:
            end_by = make_daily_repeating_copies_form.end_by_2_1.data
            date = new_service_date+timedelta(days=1)
            counter = 0
            if date.weekday() not in weekdays:
                date += timedelta(days=7-date.weekday())
            while date <= end_by and counter < 50:
                make_individual_copies(request_type_id, request_obj, [date], [new_service_time],
                                       make_daily_repeating_copies_form.include_selected_service_providers.data,
                                       make_daily_repeating_copies_form.include_service_request_status.data)
                date += timedelta(days=1)
                counter += 1
                if date.weekday() not in weekdays:
                    date += timedelta(days=7-date.weekday())


def make_weekly_repeating_copies(end_after, new_service_date, day_of_week,
                                 request_type_id, request_obj, new_service_time,
                                 make_weekly_repeating_copies_form, every_number_of_weeks,
                                 end_by):
    """
    Make weekly repeating copies
    """
    if end_after:
        counter = 0
        # if trying to make a request on the same week of the inputted new service date
        # ex. today is Monday, and the request needs to be made every Friday
        if (new_service_date.weekday() < day_of_week[-1]) and counter < end_after:
            idx = 0
            while idx < len(day_of_week) and day_of_week[idx] < new_service_date.weekday():
                idx += 1
            while idx < len(day_of_week) and counter < end_after:
                make_individual_copies(request_type_id, request_obj, [new_service_date+timedelta(days=day_of_week[idx]-new_service_date.weekday())],
                                       [new_service_time], make_weekly_repeating_copies_form.include_selected_service_providers.data,
                                       make_weekly_repeating_copies_form.include_service_request_status.data)
                idx += 1
                counter += 1
        date = new_service_date
        while counter < end_after:
            date += timedelta(days=(7-date.weekday()+7 *
                              (every_number_of_weeks-1)))
            for day in day_of_week:
                if counter < end_after:
                    new_date = date+timedelta(days=day)
                    make_individual_copies(request_type_id, request_obj, [new_date], [new_service_time],
                                           make_weekly_repeating_copies_form.include_selected_service_providers.data,
                                           make_weekly_repeating_copies_form.include_service_request_status.data)
                    counter += 1
                else:
                    break
    elif end_by:
        date = new_service_date
        counter = 0
        if (new_service_date.weekday() < day_of_week[-1] and new_service_date < end_by):
            idx = 0
            while idx < len(day_of_week) and day_of_week[idx] < new_service_date.weekday():
                idx += 1
            while idx < len(day_of_week) and date < end_by:
                make_individual_copies(request_type_id, request_obj, [new_service_date+timedelta(days=day_of_week[idx]-new_service_date.weekday())],
                                       [new_service_time], make_weekly_repeating_copies_form.include_selected_service_providers.data,
                                       make_weekly_repeating_copies_form.include_service_request_status.data)
                date = new_service_date + \
                    timedelta(days=new_service_date.weekday()-day_of_week[idx])
                idx += 1
                counter += 1
        date = new_service_date
        while date < end_by and counter < 52:
            date += timedelta(days=(7-date.weekday()+7 *
                              (every_number_of_weeks-1)))
            for day in day_of_week:
                new_date = date+timedelta(days=day)
                if new_date < end_by and counter < 52:
                    make_individual_copies(request_type_id, request_obj, [new_date], [new_service_time],
                                           make_weekly_repeating_copies_form.include_selected_service_providers.data,
                                           make_weekly_repeating_copies_form.include_service_request_status.data)
                    counter += 1
                else:
                    break


def make_monthly_repeating_copies(is_day_of_every_selected, make_monthly_repeating_copies_form,
                                  end_after, new_service_date, request_type_id, request_obj,
                                  new_service_time, end_by):
    """
    Make monthly repeating copies
    """
    if is_day_of_every_selected:
        nth_day = make_monthly_repeating_copies_form.nth_day.data
        of_every_nth_month = make_monthly_repeating_copies_form.of_every_nth_month.data
        if end_after:
            date = new_service_date
            counter = 0
            if new_service_date.day < nth_day:
                make_individual_copies(request_type_id, request_obj, [new_service_date+relativedelta(day=nth_day)],
                                       [new_service_time], make_monthly_repeating_copies_form.include_selected_service_providers.data,
                                       make_monthly_repeating_copies_form.include_service_request_status.data)
                date += relativedelta(day=nth_day)
                counter += 1
            while counter < end_after:
                date = date + \
                    relativedelta(months=of_every_nth_month, day=nth_day)
                make_individual_copies(request_type_id, request_obj, [date],
                                       [new_service_time], make_monthly_repeating_copies_form.include_selected_service_providers.data,
                                       make_monthly_repeating_copies_form.include_service_request_status.data)
                counter += 1
        elif end_by:
            date = new_service_date
            counter = 0
            if new_service_date.day < nth_day:
                date += relativedelta(day=nth_day)
                if new_service_date <= end_by:
                    make_individual_copies(request_type_id, request_obj, [date],
                                           [new_service_time], make_monthly_repeating_copies_form.include_selected_service_providers.data,
                                           make_monthly_repeating_copies_form.include_service_request_status.data)
                    counter += 1
            date = date + relativedelta(months=of_every_nth_month, day=nth_day)
            while date < end_by and counter < 24:
                make_individual_copies(request_type_id, request_obj, [date],
                                       [new_service_time], make_monthly_repeating_copies_form.include_selected_service_providers.data,
                                       make_monthly_repeating_copies_form.include_service_request_status.data)
                date = date + \
                    relativedelta(months=of_every_nth_month, day=nth_day)
                counter += 1
    elif not is_day_of_every_selected:
        week_choice = make_monthly_repeating_copies_form.week_choice.data
        weekday_choice = make_monthly_repeating_copies_form.weekday_choice.data
        month_choice = make_monthly_repeating_copies_form.month_choice.data
        if end_after:
            date = new_service_date
            counter = 0
            # ex. last monday when the new service date is 1/15/2022 would be 1/31/2022. So we need
            # to check if there is still a day in the same month for a request to be created in.
            if new_service_date < (new_service_date + relativedelta(day=1 if week_choice != -1 else 31,
                                                                    weekday=MO(week_choice) if weekday_choice == 0 else TU(week_choice) if weekday_choice == 1
                                                                    else WE(week_choice) if weekday_choice == 2 else TH(week_choice) if weekday_choice == 3 else
                                                                    FR(week_choice) if weekday_choice == 4 else SA(week_choice) if weekday_choice == 5 else SU(week_choice))):

                date += relativedelta(day=1 if week_choice != -1 else 31,
                                      weekday=MO(week_choice) if weekday_choice == 0 else TU(week_choice) if weekday_choice == 1
                                      else WE(week_choice) if weekday_choice == 2 else TH(week_choice) if weekday_choice == 3 else
                                      FR(week_choice) if weekday_choice == 4 else SA(
                                          week_choice) if weekday_choice == 5 else SU(week_choice)
                                      )

                make_individual_copies(request_type_id, request_obj, [date],
                                       [new_service_time], make_monthly_repeating_copies_form.include_selected_service_providers.data,
                                       make_monthly_repeating_copies_form.include_service_request_status.data)
                counter += 1

            while counter < end_after:
                date += relativedelta(months=month_choice, day=1 if week_choice != -1 else 31,
                                      weekday=MO(week_choice) if weekday_choice == 0 else TU(week_choice) if weekday_choice == 1
                                      else WE(week_choice) if weekday_choice == 2 else TH(week_choice) if weekday_choice == 3 else
                                      FR(week_choice) if weekday_choice == 4 else SA(
                                          week_choice) if weekday_choice == 5 else SU(week_choice)
                                      )
                make_individual_copies(request_type_id, request_obj, [date],
                                       [new_service_time], make_monthly_repeating_copies_form.include_selected_service_providers.data,
                                       make_monthly_repeating_copies_form.include_service_request_status.data)
                counter += 1
        elif end_by:
            date = new_service_date
            counter = 0
            # ex. last monday when the new service date is 1/15/2022 would be 1/31/2022. So we need
            # to check if there is still a day in the same month for a request to be created in.
            if (new_service_date < (new_service_date + relativedelta(day=1 if week_choice != -1 else 31,
                weekday=MO(week_choice) if weekday_choice == 0 else TU(week_choice) if weekday_choice == 1
                    else WE(week_choice) if weekday_choice == 2 else TH(week_choice) if weekday_choice == 3 else
                    FR(week_choice) if weekday_choice == 4 else SA(week_choice) if weekday_choice == 5 else SU(week_choice)))
                and (new_service_date + relativedelta(day=1 if week_choice != -1 else 31,
                                                      weekday=MO(week_choice) if weekday_choice == 0 else TU(week_choice) if weekday_choice == 1
                                                      else WE(week_choice) if weekday_choice == 2 else TH(week_choice) if weekday_choice == 3 else
                                                      FR(week_choice) if weekday_choice == 4 else SA(week_choice) if weekday_choice == 5 else SU(week_choice))) < end_by):

                date += relativedelta(day=1 if week_choice != -1 else 31,
                                      weekday=MO(week_choice) if weekday_choice == 0 else TU(week_choice) if weekday_choice == 1
                                      else WE(week_choice) if weekday_choice == 2 else TH(week_choice) if weekday_choice == 3 else
                                      FR(week_choice) if weekday_choice == 4 else SA(
                                          week_choice) if weekday_choice == 5 else SU(week_choice)
                                      )
            else:
                date += relativedelta(months=month_choice, day=1 if week_choice != -1 else 31,
                                      weekday=MO(week_choice) if weekday_choice == 0 else TU(week_choice) if weekday_choice == 1
                                      else WE(week_choice) if weekday_choice == 2 else TH(week_choice) if weekday_choice == 3 else
                                      FR(week_choice) if weekday_choice == 4 else SA(
                                          week_choice) if weekday_choice == 5 else SU(week_choice)
                                      )

            while date <= end_by and counter < 24:
                make_individual_copies(request_type_id, request_obj, [date],
                                       [new_service_time], make_monthly_repeating_copies_form.include_selected_service_providers.data,
                                       make_monthly_repeating_copies_form.include_service_request_status.data)
                date += relativedelta(months=month_choice, day=1 if week_choice != -1 else 31,
                                      weekday=MO(week_choice) if weekday_choice == 0 else TU(week_choice) if weekday_choice == 1
                                      else WE(week_choice) if weekday_choice == 2 else TH(week_choice) if weekday_choice == 3 else
                                      FR(week_choice) if weekday_choice == 4 else SA(
                                          week_choice) if weekday_choice == 5 else SU(week_choice)
                                      )
                counter += 1


def make_yearly_repeating_copies(is_day_of_every_selected, make_yearly_repeating_copies_form,
                                 new_service_date, new_service_time, request_type_id,
                                 request_obj, end_after, end_by):
    """
    Make yearly repeating copies
    """
    if is_day_of_every_selected:
        every_month_choice = make_yearly_repeating_copies_form.every_month_choice.data
        day_choice = make_yearly_repeating_copies_form.day_choice.data
        if end_after:
            date = new_service_date
            counter = 0
            if new_service_date < new_service_date + relativedelta(day=day_choice, month=every_month_choice):
                make_individual_copies(request_type_id, request_obj, [new_service_date+relativedelta(day=day_choice, month=every_month_choice)],
                                       [new_service_time], make_yearly_repeating_copies_form.include_selected_service_providers.data,
                                       make_yearly_repeating_copies_form.include_service_request_status.data)
                counter += 1

            while counter < end_after:
                date += relativedelta(day=day_choice,
                                      month=every_month_choice, years=+1)
                make_individual_copies(request_type_id, request_obj, [date],
                                       [new_service_time], make_yearly_repeating_copies_form.include_selected_service_providers.data,
                                       make_yearly_repeating_copies_form.include_service_request_status.data)
                counter += 1

        elif end_by:
            date = new_service_date
            counter = 0
            if (new_service_date < (new_service_date + relativedelta(day=day_choice, month=every_month_choice))
                    and (new_service_date + relativedelta(day=day_choice, month=every_month_choice)) <= end_by):
                make_individual_copies(request_type_id, request_obj, [new_service_date+relativedelta(day=day_choice, month=every_month_choice)],
                                       [new_service_time], make_yearly_repeating_copies_form.include_selected_service_providers.data,
                                       make_yearly_repeating_copies_form.include_service_request_status.data)
                counter += 1
            date += relativedelta(day=day_choice,
                                  month=every_month_choice, years=+1)
            while date < end_by and counter < 12:
                make_individual_copies(request_type_id, request_obj, [date],
                                       [new_service_time], make_yearly_repeating_copies_form.include_selected_service_providers.data,
                                       make_yearly_repeating_copies_form.include_service_request_status.data)
                date += relativedelta(day=day_choice,
                                      month=every_month_choice, years=+1)
                counter += 1

    elif not is_day_of_every_selected:
        yearly_week_choice = make_yearly_repeating_copies_form.yearly_week_choice.data
        yearly_weekday_choice = make_yearly_repeating_copies_form.yearly_weekday_choice.data
        yearly_month_choice = make_yearly_repeating_copies_form.yearly_month_choice.data
        if end_after:
            date = new_service_date
            counter = 0
            if new_service_date < (date + relativedelta(month=yearly_month_choice, day=1 if yearly_week_choice != -1 else 31,
                                                        weekday=MO(yearly_week_choice) if yearly_weekday_choice == 0 else TU(yearly_week_choice) if yearly_weekday_choice == 1
                                                        else WE(yearly_week_choice) if yearly_weekday_choice == 2 else TH(yearly_week_choice) if yearly_weekday_choice == 3 else
                                                        FR(yearly_week_choice) if yearly_weekday_choice == 4 else SA(yearly_week_choice) if yearly_weekday_choice == 5 else SU(yearly_week_choice))):

                date += relativedelta(month=yearly_month_choice, day=1 if yearly_week_choice != -1 else 31,
                                      weekday=MO(yearly_week_choice) if yearly_weekday_choice == 0 else TU(yearly_week_choice) if yearly_weekday_choice == 1
                                      else WE(yearly_week_choice) if yearly_weekday_choice == 2 else TH(yearly_week_choice) if yearly_weekday_choice == 3 else
                                      FR(yearly_week_choice) if yearly_weekday_choice == 4 else SA(yearly_week_choice) if yearly_weekday_choice == 5 else SU(yearly_week_choice))

                make_individual_copies(request_type_id, request_obj, [date],
                                       [new_service_time], make_yearly_repeating_copies_form.include_selected_service_providers.data,
                                       make_yearly_repeating_copies_form.include_service_request_status.data)
                counter += 1
            while counter < end_after:
                date += relativedelta(years=+1, month=yearly_month_choice, day=1 if yearly_week_choice != -1 else 31,
                                      weekday=MO(yearly_week_choice) if yearly_weekday_choice == 0 else TU(yearly_week_choice) if yearly_weekday_choice == 1
                                      else WE(yearly_week_choice) if yearly_weekday_choice == 2 else TH(yearly_week_choice) if yearly_weekday_choice == 3 else
                                      FR(yearly_week_choice) if yearly_weekday_choice == 4 else SA(yearly_week_choice) if yearly_weekday_choice == 5 else SU(yearly_week_choice))
                make_individual_copies(request_type_id, request_obj, [date],
                                       [new_service_time], make_yearly_repeating_copies_form.include_selected_service_providers.data,
                                       make_yearly_repeating_copies_form.include_service_request_status.data)
                counter += 1
        elif end_by:
            date = new_service_date
            counter = 0
            if (new_service_date < (date + relativedelta(month=yearly_month_choice, day=1 if yearly_week_choice != -1 else 31,
                                                         weekday=MO(yearly_week_choice) if yearly_weekday_choice == 0 else TU(yearly_week_choice) if yearly_weekday_choice == 1
                                                         else WE(yearly_week_choice) if yearly_weekday_choice == 2 else TH(yearly_week_choice) if yearly_weekday_choice == 3 else
                                                         FR(yearly_week_choice) if yearly_weekday_choice == 4 else SA(yearly_week_choice) if yearly_weekday_choice == 5 else SU(yearly_week_choice)))

                and (date + relativedelta(month=yearly_month_choice, day=1 if yearly_week_choice != -1 else 31,
                                          weekday=MO(yearly_week_choice) if yearly_weekday_choice == 0 else TU(yearly_week_choice) if yearly_weekday_choice == 1
                                          else WE(yearly_week_choice) if yearly_weekday_choice == 2 else TH(yearly_week_choice) if yearly_weekday_choice == 3 else
                                          FR(yearly_week_choice) if yearly_weekday_choice == 4 else SA(yearly_week_choice) if yearly_weekday_choice == 5 else SU(yearly_week_choice)))
                    < end_by

                ):

                date += relativedelta(month=yearly_month_choice, day=1 if yearly_week_choice != -1 else 31,
                                      weekday=MO(yearly_week_choice) if yearly_weekday_choice == 0 else TU(yearly_week_choice) if yearly_weekday_choice == 1
                                      else WE(yearly_week_choice) if yearly_weekday_choice == 2 else TH(yearly_week_choice) if yearly_weekday_choice == 3 else
                                      FR(yearly_week_choice) if yearly_weekday_choice == 4 else SA(yearly_week_choice) if yearly_weekday_choice == 5 else SU(yearly_week_choice))

                make_individual_copies(request_type_id, request_obj, [date],
                                       [new_service_time], make_yearly_repeating_copies_form.include_selected_service_providers.data,
                                       make_yearly_repeating_copies_form.include_service_request_status.data)
                counter += 1
            date += relativedelta(years=+1, month=yearly_month_choice, day=1 if yearly_week_choice != -1 else 31,
                                  weekday=MO(yearly_week_choice) if yearly_weekday_choice == 0 else TU(yearly_week_choice) if yearly_weekday_choice == 1
                                  else WE(yearly_week_choice) if yearly_weekday_choice == 2 else TH(yearly_week_choice) if yearly_weekday_choice == 3 else
                                  FR(yearly_week_choice) if yearly_weekday_choice == 4 else SA(yearly_week_choice) if yearly_weekday_choice == 5 else SU(yearly_week_choice))
            while date <= end_by and counter < 12:
                make_individual_copies(request_type_id, request_obj, [date],
                                       [new_service_time], make_yearly_repeating_copies_form.include_selected_service_providers.data,
                                       make_yearly_repeating_copies_form.include_service_request_status.data)
                date += relativedelta(years=+1, month=yearly_month_choice, day=1 if yearly_week_choice != -1 else 31,
                                      weekday=MO(yearly_week_choice) if yearly_weekday_choice == 0 else TU(yearly_week_choice) if yearly_weekday_choice == 1
                                      else WE(yearly_week_choice) if yearly_weekday_choice == 2 else TH(yearly_week_choice) if yearly_weekday_choice == 3 else
                                      FR(yearly_week_choice) if yearly_weekday_choice == 4 else SA(yearly_week_choice) if yearly_weekday_choice == 5 else SU(yearly_week_choice))
                counter += 1

# Multiple forms on one page solution:
# https://stackoverflow.com/questions/18290142/multiple-forms-in-a-single-page-using-flask-and-wtforms


@admin.route('/make-copy/<int:request_type_id>/<int:request_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def make_copy(request_type_id, request_id):
    "Make individual copy of the selected request"
    make_individual_copies_form = MakeIndividualCopiesForm()

    make_daily_repeating_copies_form = MakeDailyRepeatingCopiesForm()
    make_weekly_repeating_copies_form = MakeWeeklyRepeatingCopiesForm()
    make_monthly_repeating_copies_form = MakeMonthlyRepeatingCopiesForm()
    make_yearly_repeating_copies_form = MakeYearlyRepeatingCopiesForm()

    make_copies_without_date_form = MakeCopiesWithoutDateForm()

    request_types = ["Transportation", "Office", "Member's Home"]

    request_obj = get_request_obj(request_type_id, request_id)

    if make_individual_copies_form.submit1.data and make_individual_copies_form.validate():
        new_service_dates = make_individual_copies_form.new_service_dates.data
        new_service_times = make_individual_copies_form.new_service_times.data
        make_individual_copies(
            request_type_id, request_obj, new_service_dates, new_service_times,
            make_individual_copies_form.include_selected_service_providers.data,
            make_individual_copies_form.include_service_request_status.data
        )
        flash(
            'Successfully created copies of request {}'.format(
                request_types[request_type_id] + " #" + str(request_id)), 'success')
        return redirect(url_for('admin.search_request'))

    if make_daily_repeating_copies_form.submit2_1.data and make_daily_repeating_copies_form.validate():
        new_service_date = make_daily_repeating_copies_form.new_service_date.data
        new_service_time = make_daily_repeating_copies_form.new_service_time.data
        is_every_weekday = int(
            make_daily_repeating_copies_form.every_weekday.data)
        weekdays = {0, 1, 2, 3, 4}
        if not is_every_weekday and not make_daily_repeating_copies_form.every_number_of_days.data:
            make_daily_repeating_copies_form.every_number_of_days.errors.append(
                "Please input a number greater than or equal to 1")
        else:
            make_daily_repeating_copies(is_every_weekday, make_daily_repeating_copies_form, new_service_date,
                                        new_service_time, request_type_id, request_obj, weekdays)
        flash('Successfully created copies of request {}'.format(
            request_types[request_type_id] + " #" + str(request_id)), 'success')
        return redirect(url_for('admin.search_request'))

    if make_weekly_repeating_copies_form.submit2_2.data and make_weekly_repeating_copies_form.validate():
        new_service_date = make_weekly_repeating_copies_form.new_service_date.data
        new_service_time = make_weekly_repeating_copies_form.new_service_time.data
        every_number_of_weeks = make_weekly_repeating_copies_form.number_of_weeks.data
        end_after = make_weekly_repeating_copies_form.end_after_2_2.data
        end_by = make_weekly_repeating_copies_form.end_by_2_2.data

        # list of numbers where [0,1,2,3,4,5,6] is [Monday, Tuesday, Wednesday...]
        day_of_week = sorted(
            make_weekly_repeating_copies_form.day_of_week.data)

        make_weekly_repeating_copies(end_after, new_service_date, day_of_week,
                                     request_type_id, request_obj, new_service_time,
                                     make_weekly_repeating_copies_form, every_number_of_weeks,
                                     end_by)
        flash(
            'Successfully created copies of request {}'.format(
                request_types[request_type_id] + " #" + str(request_id)), 'success')
        return redirect(url_for('admin.search_request'))

    if make_monthly_repeating_copies_form.submit2_3.data and make_monthly_repeating_copies_form.validate():
        new_service_date = make_monthly_repeating_copies_form.new_service_date.data
        new_service_time = make_monthly_repeating_copies_form.new_service_time.data
        end_after = make_monthly_repeating_copies_form.end_after_2_3.data
        end_by = make_monthly_repeating_copies_form.end_by_2_3.data
        is_day_of_every_selected = int(
            make_monthly_repeating_copies_form.is_day_of_every_selected.data)

        make_monthly_repeating_copies(is_day_of_every_selected, make_monthly_repeating_copies_form,
                                      end_after, new_service_date, request_type_id, request_obj,
                                      new_service_time, end_by)
        flash(
            'Successfully created copies of request {}'.format(
                request_types[request_type_id] + " #" + str(request_id)), 'success')
        return redirect(url_for('admin.search_request'))

    if make_yearly_repeating_copies_form.submit2_4.data and make_yearly_repeating_copies_form.validate():
        new_service_date = make_yearly_repeating_copies_form.new_service_date.data
        new_service_time = make_yearly_repeating_copies_form.new_service_time.data
        end_after = make_yearly_repeating_copies_form.end_after_2_4.data
        end_by = make_yearly_repeating_copies_form.end_by_2_4.data
        is_day_of_every_selected = int(
            make_yearly_repeating_copies_form.is_yearly_day_of_every_selected.data)
        make_yearly_repeating_copies(is_day_of_every_selected, make_yearly_repeating_copies_form,
                                     new_service_date, new_service_time, request_type_id,
                                     request_obj, end_after, end_by)
        flash(
            'Successfully created copies of request {}'.format(
                request_types[request_type_id] + " #" + str(request_id)), 'success')
        return redirect(url_for('admin.search_request'))

    if make_copies_without_date_form.submit3.data and make_copies_without_date_form.validate():
        number_of_copies = make_copies_without_date_form.number_of_copies.data
        make_copies_without_date(
            request_type_id, request_obj, number_of_copies,
            make_copies_without_date_form.include_selected_service_providers.data,
            make_copies_without_date_form.include_service_request_status.data
        )
        flash(
            'Successfully created copies of request {}'.format(
                request_types[request_type_id] + " #" + str(request_id)), 'success')
        return redirect(url_for('admin.search_request'))

    return render_template('admin/request_manager/make_copy.html',
                           form1=make_individual_copies_form,
                           form2_1=make_daily_repeating_copies_form,
                           form2_2=make_weekly_repeating_copies_form,
                           form2_3=make_monthly_repeating_copies_form,
                           form2_4=make_yearly_repeating_copies_form,
                           form3=make_copies_without_date_form,
                           request_type_id=request_type_id,
                           request_id=request_id
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

    member_records = RequestMemberRecord.query.filter_by(
        request_id=request_id).filter_by(request_category_id=request_type_id).all()
    for member_record in member_records:
        db.session.delete(member_record)
    volunteer_records = RequestVolunteerRecord.query.filter_by(
        request_id=request_id).filter_by(request_category_id=request_type_id).all()
    for volunteer_record in volunteer_records:
        db.session.delete(volunteer_record)

    db.session.delete(request)
    db.session.commit()

    flash(
        'Successfully deleted request {}'.format(
            request_type + " #" + str(request_id)), 'success')
    return redirect(url_for('admin.search_request'))


@admin.route('/filter-service-providers', methods=['GET', 'POST'])
def filter_service_providers():
    req_json = request.get_json()
    id_list = req_json["serviceProviders"]
    final_id_list = []
    initial_pickup = datetime.strptime(
        req_json["initialPickup"], "%a, %d %b %Y %H:%M:%S %Z").time()
    return_pickup = datetime.strptime(
        req_json["returnPickup"], "%a, %d %b %Y %H:%M:%S %Z").time()
    requested_date = datetime.strptime(
        req_json["requestedDate"], "%a, %d %b %Y %H:%M:%S %Z").date()
    requested_day = requested_date.weekday()

    for id in id_list:
        # Compare each volunteer's availability on the requested day to the requested time
        availability = Availability.query.filter_by(
            id=id).first()

        # Determine which availabilities we're looking at depending on req day
        vol_day_mapping = {
            0: [
                availability.availability_monday_start,
                availability.availability_monday_end
            ],
            1: [
                availability.availability_tuesday_start,
                availability.availability_tuesday_end
            ],
            2: [
                availability.availability_wednesday_start,
                availability.availability_wednesday_end
            ],
            3: [
                availability.availability_thursday_start,
                availability.availability_thursday_end
            ],
            4: [
                availability.availability_friday_start,
                availability.availability_friday_end
            ],
            5: [
                availability.availability_saturday_start,
                availability.availability_saturday_end
            ],
            6: [
                availability.availability_sunday_start,
                availability.availability_sunday_end
            ]
        }

        vol_avail_start, vol_avail_end = vol_day_mapping[requested_day]

        if vol_avail_start is not None and vol_avail_end is not None:
            if initial_pickup <= return_pickup and initial_pickup >= vol_avail_start and return_pickup <= vol_avail_end:
                final_id_list.append(id)
                no_conflicts = True
                # Check if the volunteers are on vacation
                for vacation in Vacation.query.filter_by(v_id=id).all():
                    if vacation.start_date <= requested_date and vacation.end_date >= requested_date:
                        if no_conflicts:
                            no_conflicts = False
                            final_id_list.remove(id)
                # Check if there are any overlapping requests for each volunteer
                for volunteer_request in RequestVolunteerRecord.query.filter_by(volunteer_id=id).all():
                    # Transportation Request
                    if volunteer_request.request_category_id == 0:
                        current_request = TransportationRequest.query.filter_by(
                            id=volunteer_request.request_id).first()
                        crequest_date = current_request.requested_date
                        crequest_start = current_request.initial_pickup_time
                        crequest_end = current_request.return_pickup_time
                    # Office Request
                    elif volunteer_request.request_category_id == 1:
                        current_request = OfficeRequest.query.filter_by(
                            id=volunteer_request.request_id).first()
                        crequest_date = current_request.requested_date
                        crequest_start = current_request.start_time
                        crequest_end = current_request.end_time
                    # Member's Home Request
                    elif volunteer_request.request_category_id == 2:
                        current_request = MembersHomeRequest.query.filter_by(
                            id=volunteer_request.request_id).first()
                        crequest_date = current_request.requested_date
                        crequest_start = current_request.from_time
                        crequest_end = current_request.until_time
                    if crequest_date == requested_date:
                        if (crequest_start >= initial_pickup and crequest_start <= return_pickup) or (crequest_end >= initial_pickup and crequest_end <= return_pickup):
                            if no_conflicts:
                                no_conflicts = False
                                final_id_list.remove(id)

    return json.dumps(final_id_list)


@ admin.route('/cancel-request/<int:request_type_id>/<int:request_id>', methods=['GET', 'POST'])
@ login_required
@ admin_required
def cancel_request(request_type_id, request_id):
    """Cancel a request"""
    json = request.get_json()
    request_type = ""
    # Transportation Request
    if request_type_id == 0:
        request_type = "Transportation"
        request_obj = TransportationRequest.query.filter_by(
            id=request_id).first()
    # Office Request
    elif request_type_id == 1:
        request_type = "Office"
        request_obj = OfficeRequest.query.filter_by(id=request_id).first()
    # Member's Home Request
    elif request_type_id == 2:
        request_type = "Member's Home"
        request_obj = MembersHomeRequest.query.filter_by(id=request_id).first()

    # status id of cancel is 3
    request_obj.status_id = 3
    request_obj.cancellation_reason = json['reason']
    flash(
        'Successfully cancelled request {}'.format(
            request_type + " #" + str(request_id)), 'success')
    resp = jsonify(success=True)
    return resp


@ admin.route('/confirm-request/<int:request_type_id>/<int:request_id>', methods=['GET', 'POST'])
@ login_required
@ admin_required
def confirm_request(request_type_id, request_id):
    """Confirm a request"""
    form = CompleteServiceRequestForm()
    form.verified_by.choices = [
        (staffer.id, staffer.first_name + " " + staffer.last_name)
        for staffer in Staffer.query.all()
    ]
    request_member_records = RequestMemberRecord.query.filter_by(
        request_id=request_id, request_category_id=request_type_id).all()
    member_name = ""
    for request_member_record in request_member_records:
        member = Member.query.get(request_member_record.member_id)
        member_name += member.first_name + " " + member.last_name + ", "
    member_name = member_name[:-2]

    request_volunteer_records = RequestVolunteerRecord.query.filter_by(
        request_id=request_id, request_category_id=request_type_id).all()

    volunteer_name = ""
    for request_volunteer_record in request_volunteer_records:
        volunteer = Volunteer.query.get(request_volunteer_record.volunteer_id)
        volunteer_name += volunteer.first_name + " " + volunteer.last_name + ", "
    volunteer_name = volunteer_name[:-2]

    # Transportation Request
    if request_type_id == 0:
        request_type = "Transportation"
        request_obj = TransportationRequest.query.filter_by(
            id=request_id).first()
        start_time = request_obj.initial_pickup_time
        end_time = request_obj.drop_off_time
    # Office Request
    elif request_type_id == 1:
        request_type = "Office"
        request_obj = OfficeRequest.query.filter_by(id=request_id).first()
        start_time = request_obj.start_time
        end_time = request_obj.end_time
    # Member's Home Request
    elif request_type_id == 2:
        request_type = "Member's Home"
        request_obj = MembersHomeRequest.query.filter_by(id=request_id).first()
        start_time = request_obj.from_time
        end_time = request_obj.until_time
    service_category = ServiceCategory.query.get(
        request_obj.service_category_id).name
    service = Service.query.get(request_obj.service_id).name
    requested_date = request_obj.requested_date.strftime("%m/%d/%Y")
    if form.validate_on_submit():
        request_obj.rating = form.rating.data
        request_obj.member_comments = form.member_comments.data
        request_obj.provider_comments = form.provider_comments.data
        request_obj.duration_in_mins = form.duration_minutes.data
        if form.duration_hours.data:
            request_obj.duration_in_mins += form.duration_hours.data*60
        if not (form.duration_hours.data or form.duration_minutes.data):
            start_delta = timedelta(
                hours=start_time.hour, minutes=start_time.minute)
            end_delta = timedelta(hours=end_time.hour, minutes=end_time.minute)
            duration = end_delta - start_delta
            request_obj.duration_in_mins = duration.seconds/60
        request_obj.number_of_trips = form.number_of_trips.data
        request_obj.mileage = form.mileage.data
        request_obj.expenses = form.expenses.data
        request_obj.verified_by = form.verified_by.data

        # status id of complete is 2
        request_obj.status_id = 2

        flash(
            'Successfully completed request {}'.format(
                request_type + " #" + str(request_id)), 'success')
        return redirect(url_for('admin.search_request'))
    return render_template('admin/request_manager/confirm_request.html',
                           form=form, service_category=service_category, service=service,
                           member_name=member_name, volunteer_name=volunteer_name,
                           requested_date=requested_date, start_time=start_time.strftime("%I:%M %p"))


# Create a new service request
@admin.route('/create-request', methods=['GET', 'POST'])
@login_required
@admin_required
def create_request():
    return render_template('admin/request_manager/create_request.html')


@admin.route('/create-request/<int:service_category_id>')
@login_required
@admin_required
def get_services(service_category_id):
    """
    Returns services given its service category id
    """
    services = Service.query.filter_by(category_id=service_category_id).all()
    services_array = []
    for service in services:
        service_obj = {}
        service_obj['id'] = service.id
        service_obj['name'] = service.name
        services_array.append(service_obj)
    return jsonify({'services': services_array})


@admin.route('/create-request/service/<int:service_id>')
@login_required
@admin_required
def get_services_of_volunteers(service_id):
    services = {}
    services["service_providers"] = []
    for p in ProvidedService.query.filter_by(service_id=service_id).all():
        services["service_providers"].append({
            "id": p.volunteer_id,
            "firstName": Volunteer.query.get(p.volunteer_id).first_name,
            "lastName": Volunteer.query.get(p.volunteer_id).last_name
        })
    return jsonify(services)


# Create a new Transportation service request.


@admin.route('/create-request/transportation-request/<int:request_id>', methods=['GET', 'POST'])
@admin.route('/create-request/transportation-request', methods=['GET', 'POST'])
@login_required
@admin_required
def create_transportation_request(request_id=None):
    form = TransportationRequestForm()
    service_category_choices = []
    for category in ServiceCategory.query.filter_by(request_type_id=0).all():
        if len(Service.query.filter_by(category_id=category.id).all()) != 0:
            service_category_choices.append((category.id, category.name))
    form.service_category.choices = service_category_choices
    form.transportation_service.choices = [
        (service.id, service.name) for service in
        Service.query.filter_by(
            category_id=service_category_choices[0][0]
        ).all()
    ]

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
        form.service_category.choices = service_category_choices
        form.transportation_service.choices = [
            (service.id, service.name) for service in
            Service.query.filter_by(
                category_id=transportation_request.service_category_id
            ).all()
        ]

    form.requesting_member.multiple = True
    form.requesting_member.choices = [
        (member.id, member.first_name + " " + member.last_name)
        for member in Member.query.all()
    ]

    service_provider_choices = []
    for p in ProvidedService.query.filter_by(service_id=(Service.query.filter_by(
            category_id=service_category_choices[0][0]).first()).id).all():
        service_provider_choices.append(
            (p.volunteer_id, Volunteer.query.get(p.volunteer_id).first_name + " " + Volunteer.query.get(p.volunteer_id).last_name))
    form.service_provider.choices = service_provider_choices

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

    if request.method == 'POST':
        if form.service_category.data in [choice[0] for choice in form.service_category.choices]:
            form.transportation_service.choices = [
                (service.id, service.name) for service in
                Service.query.filter_by(
                    category_id=form.service_category.data
                ).all()
            ]
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
                transportation_request.service_category_id = form.service_category.data
                transportation_request.service_id = form.transportation_service.data
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
                    service_category_id=form.service_category.data,
                    service_id=form.transportation_service.data,
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
                flash('Successfully edited transportation request # {}'.
                      format(request_id), 'success')
            else:
                flash('Successfully submitted a transportation request', 'success')
            return redirect(url_for('admin.search_request'))

    volunteer_info = []
    for volunteer in Volunteer.query.all():
        vol_status = 'Non-Member Volunteer' if volunteer.is_member_volunteer == False else 'Member Volunteer'
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
             str(volunteer.is_fully_vetted))
        )

    member_info = []
    for member in Member.query.all():
        address = Address.query.get(member.primary_address_id)
        street_address = address.address1
        member_info.append(
            (member.first_name + " " + member.last_name,
             member.membership_expiration_date,
             str(member.email_address),
             member.primary_phone_number,
             street_address
             )
        )

    return render_template('admin/request_manager/transportation_request.html',
                           title='Transportation Request',
                           form=form,
                           volunteer_data=json.dumps(volunteer_info),
                           member_data=json.dumps(member_info, default=str))


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
    # TODO: Determine email template based on this variable
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
                    volunteer=Volunteer.get(
                        RequestMemberRecord.query.get(req_id).volunteer_id),
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
    service_category_choices = []
    for category in ServiceCategory.query.filter_by(request_type_id=1).all():
        if len(Service.query.filter_by(category_id=category.id).all()) != 0:
            service_category_choices.append((category.id, category.name))
    form.service_category.choices = service_category_choices
    form.office_time_service.choices = [
        (service.id, service.name) for service in
        Service.query.filter_by(
            category_id=service_category_choices[0][0]
        ).all()
    ]
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
            service_category=office_time_request.service_category_id,
            office_time_service=office_time_request.service_id,
            status=RequestStatus.query.filter_by(
                id=office_time_request.status_id),
            contact_log_priority=ContactLogPriorityType.query.filter_by(
                id=office_time_request.contact_log_priority_id),
            special_instructions=office_time_request.special_instructions
        )
        form.service_category.choices = service_category_choices
        form.office_time_service.choices = [
            (service.id, service.name) for service in
            Service.query.filter_by(
                category_id=office_time_request.service_category_id
            ).all()
        ]
    form.requesting_member.multiple = True
    form.requesting_member.choices = [
        (member.id, member.first_name + " " + member.last_name)
        for member in Member.query.all()
    ]

    service_provider_choices = []
    for p in ProvidedService.query.filter_by(service_id=(Service.query.filter_by(
            category_id=service_category_choices[0][0]).first()).id).all():
        service_provider_choices.append(
            (p.volunteer_id, Volunteer.query.get(p.volunteer_id).first_name + " " + Volunteer.query.get(p.volunteer_id).last_name))
    form.service_provider.choices = service_provider_choices

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
    if request.method == 'POST':
        if form.service_category.data in [choice[0] for choice in form.service_category.choices]:
            form.office_time_service.choices = [
                (service.id, service.name) for service in
                Service.query.filter_by(
                    category_id=form.service_category.data
                ).all()
            ]
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
                office_time_request.service_category_id = form.service_category.data
                office_time_request.service_id = form.office_time_service.data
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
                    service_category_id=form.service_category.data,
                    service_id=form.office_time_service.data,
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
        vol_status = 'Non-Member Volunteer' if volunteer.is_member_volunteer == False else 'Member Volunteer'
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
             str(volunteer.is_fully_vetted))
        )

    member_info = []
    for member in Member.query.all():
        address = Address.query.get(member.primary_address_id)
        street_address = address.address1
        member_info.append(
            (member.first_name + " " + member.last_name,
             member.membership_expiration_date,
             str(member.email_address),
             member.primary_phone_number,
             street_address
             )
        )

    return render_template('admin/request_manager/office_time_request.html',
                           title='Office Time Request',
                           form=form,
                           volunteer_data=json.dumps(volunteer_info),
                           member_data=json.dumps(member_info, default=str))


@admin.route('/create-request/members-home-request/<int:request_id>', methods=['GET', 'POST'])
@admin.route('create-request/members-home-request', methods=['GET', 'POST'])
@admin_required
@login_required
def create_members_home_request(request_id=None):
    form = MembersHomeRequestForm()
    service_category_choices = []
    for category in ServiceCategory.query.filter_by(request_type_id=2).all():
        if len(Service.query.filter_by(category_id=category.id).all()) != 0:
            service_category_choices.append((category.id, category.name))
    form.service_category.choices = service_category_choices
    form.member_home_service.choices = [
        (service.id, service.name) for service in
        Service.query.filter_by(
            category_id=service_category_choices[0][0]
        ).all()
    ]
    members_home_request = None
    if request_id:
        members_home_request = MembersHomeRequest.query.filter_by(
            id=request_id).first()
        form = MembersHomeRequestForm(
            type_id=2,
            description=members_home_request.short_description,
            date_created=members_home_request.created_date,
            requested_date=members_home_request.requested_date,
            time_from=members_home_request.from_time,
            time_until=members_home_request.until_time,
            time_flexible=members_home_request.is_date_time_flexible,
            follow_up_date=members_home_request.followup_date,
            responsible_staffer=members_home_request.responsible_staffer_id,
            person_to_cc=members_home_request.cc_email,
            service_category=members_home_request.service_category_id,
            member_home_service=members_home_request.service_id,
            special_instructions=members_home_request.special_instructions)
        form.service_category.choices = service_category_choices
        form.member_home_service.choices = [
            (service.id, service.name) for service in
            Service.query.filter_by(
                category_id=members_home_request.service_category_id
            ).all()
        ]

    form.requesting_member.multiple = True
    form.requesting_member.choices = [
        (member.id, member.first_name + " " + member.last_name)
        for member in Member.query.all()
    ]

    service_provider_choices = []
    for p in ProvidedService.query.filter_by(service_id=(Service.query.filter_by(
            category_id=service_category_choices[0][0]).first()).id).all():
        service_provider_choices.append(
            (p.volunteer_id, Volunteer.query.get(p.volunteer_id).first_name + " " + Volunteer.query.get(p.volunteer_id).last_name))
    form.service_provider.choices = service_provider_choices

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
        form.contact_log_priority.data = ContactLogPriorityType.query.filter_by(
            id=members_home_request.contact_log_priority_id).first()
    if request.method == 'POST':
        if form.service_category.data in [choice[0] for choice in form.service_category.choices]:
            form.member_home_service.choices = [
                (service.id, service.name) for service in
                Service.query.filter_by(
                    category_id=form.service_category.data
                ).all()
            ]
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
                members_home_request.service_category_id = form.service_category.data
                members_home_request.service_id = form.member_home_service.data
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
                    service_category_id=form.service_category.data,
                    service_id=form.member_home_service.data,
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
        vol_status = 'Non-Member Volunteer' if volunteer.is_member_volunteer == False else 'Member Volunteer'
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
             str(volunteer.is_fully_vetted))
        )

    member_info = []
    for member in Member.query.all():
        address = Address.query.get(member.primary_address_id)
        street_address = address.address1
        member_info.append(
            (member.first_name + " " + member.last_name,
             member.membership_expiration_date,
             str(member.email_address),
             member.primary_phone_number,
             street_address
             )
        )

    return render_template('admin/request_manager/members_home_request.html',
                           title='Members Home Request',
                           form=form,
                           volunteer_data=json.dumps(volunteer_info),
                           member_data=json.dumps(member_info, default=str))


@admin.route('/invite-member', methods=['GET', 'POST'])
@admin.route('/invite-member/<int:member_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def invite_member(member_id=None):
    """Page for member management."""
    member = None
    member_volunteer = None
    form = MemberManager()

    # Get member information from the Member table if the user is editing an existing member
    if member_id is not None:
        member = Member.query.filter_by(id=member_id).first()

        if member.volunteer_id is not None:
            member_volunteer = True

        primary_address = Address.query.filter_by(
            id=member.primary_address_id).first()
        primary_metro_area = None
        # Get primary address information from the Address table
        if primary_address is not None:
            primary_address1 = primary_address.address1
            primary_address2 = primary_address.address2
            primary_city = primary_address.city
            primary_state = primary_address.state
            primary_zip_code = primary_address.zipcode
            primary_country = primary_address.country

            # Get metro area information from the Metro Area table if the primary address has a metro area
            if primary_address.metro_area_id is not None:
                primary_metro_area = MetroArea.query.filter_by(
                    id=primary_address.metro_area_id).first()

        secondary_address = Address.query.filter_by(
            id=member.secondary_address_id).first()
        secondary_metro_area = None
        # Get secondary address information from the Address table if the member has a secondary address
        if secondary_address is not None:
            secondary_address1 = secondary_address.address1
            secondary_address2 = secondary_address.address2
            secondary_city = secondary_address.city
            secondary_state = secondary_address.state
            secondary_zip_code = secondary_address.zipcode
            secondary_country = secondary_address.country

            # Get metro area information from the Metro Area table if the secondary address has a metro area
            if secondary_address.metro_area_id is not None:
                secondary_metro_area = MetroArea.query.filter_by(
                    id=secondary_address.metro_area_id).first()

        # Populate existing information
        form = MemberManager(
            first_name=member.first_name,
            middle_initial=member.middle_initial,
            last_name=member.last_name,
            preferred_name=member.preferred_name,
            salutation=member.salutation,
            gender=member.gender,
            birthdate=member.birthdate,
            primary_address1=primary_address1 if primary_address else None,
            primary_address2=primary_address2 if primary_address else None,
            primary_city=primary_city if primary_address else None,
            primary_state=primary_state if primary_address else None,
            primary_zip_code=primary_zip_code if primary_address else None,
            primary_country=primary_country if primary_address else None,
            primary_metro_area=primary_metro_area if primary_metro_area else None,
            secondary_address1=secondary_address1 if secondary_address else None,
            secondary_address2=secondary_address2 if secondary_address else None,
            secondary_city=secondary_city if secondary_address else None,
            secondary_state=secondary_state if secondary_address else None,
            secondary_zip_code=secondary_zip_code if secondary_address else None,
            secondary_country=secondary_country if secondary_address else None,
            secondary_metro_area=secondary_metro_area if secondary_metro_area else None,
            primary_phone_number=member.primary_phone_number,
            secondary_phone_number=member.secondary_phone_number,
            email_address=member.email_address,
            preferred_contact_method=member.preferred_contact_method,
            emergency_contact_name=member.emergency_contact_name,
            emergency_contact_relationship=member.emergency_contact_relationship,
            emergency_contact_phone_number=member.emergency_contact_phone_number,
            emergency_contact_email_address=member.emergency_contact_email_address,
            membership_expiration_date=member.membership_expiration_date,
            member_number=member.member_number,
            volunteer_notes=member.volunteer_notes,
            staffer_notes=member.staffer_notes)

    if form.validate_on_submit():

        # Retrieve address and metro area information entered into the form
        secondary_address = None
        primary_metro_area = None
        secondary_metro_area = None
        if form.primary_metro_area.data:
            primary_metro_area = form.primary_metro_area.data
        if form.secondary_metro_area.data:
            secondary_metro_area = form.secondary_metro_area.data

        if (form.secondary_as_primary_checkbox.data):
            primary_address = Address(
                name=form.first_name.data + " " + form.last_name.data,
                address1=form.secondary_address1.data,
                address2=form.secondary_address2.data,
                city=form.secondary_city.data,
                state=form.secondary_state.data,
                zipcode=form.secondary_zip_code.data,
                country=form.secondary_country.data,
                metro_area_id=secondary_metro_area.id if secondary_metro_area else None)
            if form.primary_address1.data:
                secondary_address = Address(
                    name=form.first_name.data + " " + form.last_name.data,
                    address1=form.primary_address1.data,
                    address2=form.primary_address2.data,
                    city=form.primary_city.data,
                    state=form.primary_state.data,
                    zipcode=form.primary_zip_code.data,
                    country=form.primary_country.data,
                    metro_area_id=primary_metro_area.id if primary_metro_area else None)
        else:
            primary_address = Address(name=form.first_name.data + " " +
                                      form.last_name.data,
                                      address1=form.primary_address1.data,
                                      address2=form.primary_address2.data,
                                      city=form.primary_city.data,
                                      state=form.primary_state.data,
                                      zipcode=form.primary_zip_code.data,
                                      country=form.primary_country.data,
                                      metro_area_id=primary_metro_area.id if primary_metro_area else None)
            if form.secondary_address1.data:
                secondary_address = Address(
                    name=form.first_name.data + " " + form.last_name.data,
                    address1=form.secondary_address1.data,
                    address2=form.secondary_address2.data,
                    city=form.secondary_city.data,
                    state=form.secondary_state.data,
                    zipcode=form.secondary_zip_code.data,
                    country=form.secondary_country.data,
                    metro_area_id=secondary_metro_area.id if secondary_metro_area else None)

        db.session.add(primary_address)
        db.session.commit()
        if secondary_address:
            db.session.add(secondary_address)
            db.session.commit()

        if member is not None:

            # Retrieve member information entered into the form when editing an existing member
            old_primary_address = Address.query.filter_by(
                id=member.primary_address_id).first()
            if old_primary_address is not None:
                db.session.delete(old_primary_address)
                db.session.commit()
            old_secondary_address = Address.query.filter_by(
                id=member.secondary_address_id).first()
            if old_secondary_address is not None:
                db.session.delete(old_secondary_address)
                db.session.commit()

            updated_member = member
            updated_member.salutation = form.salutation.data
            updated_member.primary_address_id = primary_address.id
            updated_member.secondary_address_id = secondary_address.id if secondary_address else None
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

            if member_volunteer is not None:
                updated_volunteer = Volunteer.query.filter_by(
                    id=member.volunteer_id).first()
                updated_volunteer.salutation = form.salutation.data
                updated_volunteer.primary_address_id = primary_address.id
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
                db.session.add(updated_volunteer)
                db.session.commit()
            flash(
                'Member {} successfully updated'.format(form.first_name.data),
                'success')

        else:
            # Retrieve member information entered into the form when creating a new member
            member = Member(
                salutation=form.salutation.data,
                primary_address_id=primary_address.id,
                secondary_address_id=secondary_address.id
                if secondary_address else None,
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

        return redirect(url_for('admin.people_manager', active='member'))

    return render_template('admin/people_manager/member_manager.html',
                           form=form, member_volunteer=member_volunteer)


@admin.route('/invite-volunteer', methods=['GET', 'POST'])
@admin.route('/invite-volunteer/<int:user_id>', methods=['GET', 'POST'])
@admin.route('/invite-volunteer/<int:user_id>/<member_volunteer>', methods=['GET', 'POST'])
@login_required
@admin_required
def invite_volunteer(user_id=None, member_volunteer=None):
    """Invites a user to create a volunteer account"""
    volunteer = None
    form = VolunteerManager()

    # Get volunteer information from the Member table if the user is creating a member-volunteer
    if member_volunteer is not None:
        member = Member.query.filter_by(id=user_id).first()

        primary_address = Address.query.filter_by(
            id=member.primary_address_id).first()
        primary_metro_area = None
        # Get primary address information from the Address table
        if primary_address is not None:
            primary_address1 = primary_address.address1
            primary_address2 = primary_address.address2
            primary_city = primary_address.city
            primary_state = primary_address.state
            primary_zip_code = primary_address.zipcode
            primary_country = primary_address.country

            # Get metro area information from the Metro Area table if the primary address has a metro area
            if primary_address.metro_area_id is not None:
                primary_metro_area = MetroArea.query.filter_by(
                    id=primary_address.metro_area_id).first()

        secondary_address = Address.query.filter_by(
            id=member.secondary_address_id).first()
        secondary_metro_area = None
        # Get secondary address information from the Address table if the volunteer has a secondary address
        if secondary_address is not None:
            secondary_address1 = secondary_address.address1
            secondary_address2 = secondary_address.address2
            secondary_city = secondary_address.city
            secondary_state = secondary_address.state
            secondary_zip_code = secondary_address.zipcode
            secondary_country = secondary_address.country

            # Get metro area information from the Metro Area table if the secondary address has a metro area
            if secondary_address.metro_area_id is not None:
                secondary_metro_area = MetroArea.query.filter_by(
                    id=secondary_address.metro_area_id).first()

        form = VolunteerManager(
            member_id=member.id,
            salutation=member.salutation,
            first_name=member.first_name,
            middle_initial=member.middle_initial,
            last_name=member.last_name,
            gender=member.gender,
            birthdate=member.birthdate,
            preferred_name=member.preferred_name,
            primary_address1=primary_address1 if primary_address else None,
            primary_address2=primary_address2 if primary_address else None,
            primary_city=primary_city if primary_address else None,
            primary_state=primary_state if primary_address else None,
            primary_zip_code=primary_zip_code if primary_address else None,
            primary_country=primary_country if primary_address else None,
            primary_metro_area=primary_metro_area if primary_metro_area else None,
            secondary_address1=secondary_address1 if secondary_address else None,
            secondary_address2=secondary_address2 if secondary_address else None,
            secondary_city=secondary_city if secondary_address else None,
            secondary_state=secondary_state if secondary_address else None,
            secondary_zip_code=secondary_zip_code if secondary_address else None,
            secondary_country=secondary_country if secondary_address else None,
            secondary_metro_area=secondary_metro_area if secondary_metro_area else None,
            emergency_contact_name=member.emergency_contact_name,
            emergency_contact_relationship=member.
            emergency_contact_relationship,
            emergency_contact_phone_number=member.
            emergency_contact_phone_number,
            emergency_contact_email_address=member.
            emergency_contact_email_address,
            primary_phone_number=member.primary_phone_number,
            secondary_phone_number=member.secondary_phone_number,
            email_address=member.email_address,
            preferred_contact_method=member.preferred_contact_method)

    # Get volunteer information from the Volunteer table if the user is editing an existing volunteer
    elif user_id is not None:
        volunteer = Volunteer.query.filter_by(id=user_id).first()

        if volunteer.is_member_volunteer == True:
            member_volunteer = True

        primary_address = Address.query.filter_by(
            id=volunteer.primary_address_id).first()
        primary_metro_area = None
        # Get primary address information from the Address table
        if primary_address is not None:
            primary_address1 = primary_address.address1
            primary_address2 = primary_address.address2
            primary_city = primary_address.city
            primary_state = primary_address.state
            primary_zip_code = primary_address.zipcode
            primary_country = primary_address.country

            # Get metro area information from the Metro Area table if the primary address has a metro area
            if primary_address.metro_area_id is not None:
                primary_metro_area = MetroArea.query.filter_by(
                    id=primary_address.metro_area_id).first()

        secondary_address = Address.query.filter_by(
            id=volunteer.secondary_address_id).first()
        secondary_metro_area = None
        # Get secondary address information from the Address table if the volunteer has a secondary address
        if secondary_address is not None:
            secondary_address1 = secondary_address.address1
            secondary_address2 = secondary_address.address2
            secondary_city = secondary_address.city
            secondary_state = secondary_address.state
            secondary_zip_code = secondary_address.zipcode
            secondary_country = secondary_address.country

            # Get metro area information from the Metro Area table if the secondary address has a metro area
            if secondary_address.metro_area_id is not None:
                secondary_metro_area = MetroArea.query.filter_by(
                    id=secondary_address.metro_area_id).first()

        # Populate existing information
        form = VolunteerManager(
            salutation=volunteer.salutation,
            first_name=volunteer.first_name,
            middle_initial=volunteer.middle_initial,
            last_name=volunteer.last_name,
            gender=volunteer.gender,
            birthdate=volunteer.birthdate,
            preferred_name=volunteer.preferred_name,
            primary_address1=primary_address1 if primary_address else None,
            primary_address2=primary_address2 if primary_address else None,
            primary_city=primary_city if primary_address else None,
            primary_state=primary_state if primary_address else None,
            primary_zip_code=primary_zip_code if primary_address else None,
            primary_country=primary_country if primary_address else None,
            primary_metro_area=primary_metro_area if primary_metro_area else None,
            secondary_address1=secondary_address1 if secondary_address else None,
            secondary_address2=secondary_address2 if secondary_address else None,
            secondary_city=secondary_city if secondary_address else None,
            secondary_state=secondary_state if secondary_address else None,
            secondary_zip_code=secondary_zip_code if secondary_address else None,
            secondary_country=secondary_country if secondary_address else None,
            secondary_metro_area=secondary_metro_area if secondary_metro_area else None,
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
            general_notes=volunteer.general_notes)

    if form.validate_on_submit():

        # Retrieve address and metro area information entered into the form
        secondary_address = None
        primary_metro_area = None
        secondary_metro_area = None
        if form.primary_metro_area.data:
            primary_metro_area = form.primary_metro_area.data
        if form.secondary_metro_area.data:
            secondary_metro_area = form.secondary_metro_area.data

        if (form.secondary_as_primary_checkbox.data):
            primary_address = Address(
                name=form.first_name.data + " " + form.last_name.data,
                address1=form.secondary_address1.data,
                address2=form.secondary_address2.data,
                city=form.secondary_city.data,
                state=form.secondary_state.data,
                zipcode=form.secondary_zip_code.data,
                country=form.secondary_country.data,
                metro_area_id=secondary_metro_area.id if secondary_metro_area else None)
            if form.primary_address1.data:
                secondary_address = Address(
                    name=form.first_name.data + " " + form.last_name.data,
                    address1=form.primary_address1.data,
                    address2=form.primary_address2.data,
                    city=form.primary_city.data,
                    state=form.primary_state.data,
                    zipcode=form.primary_zip_code.data,
                    country=form.primary_country.data,
                    metro_area_id=primary_metro_area.id if primary_metro_area else None)
        else:
            primary_address = Address(name=form.first_name.data + " " +
                                      form.last_name.data,
                                      address1=form.primary_address1.data,
                                      address2=form.primary_address2.data,
                                      city=form.primary_city.data,
                                      state=form.primary_state.data,
                                      zipcode=form.primary_zip_code.data,
                                      country=form.primary_country.data,
                                      metro_area_id=primary_metro_area.id if primary_metro_area else None)
            if form.secondary_address1.data:
                secondary_address = Address(
                    name=form.first_name.data + " " + form.last_name.data,
                    address1=form.secondary_address1.data,
                    address2=form.secondary_address2.data,
                    city=form.secondary_city.data,
                    state=form.secondary_state.data,
                    zipcode=form.secondary_zip_code.data,
                    country=form.secondary_country.data,
                    metro_area_id=secondary_metro_area.id if secondary_metro_area else None)

        db.session.add(primary_address)
        db.session.commit()
        if secondary_address:
            db.session.add(secondary_address)
            db.session.commit()

        if volunteer is not None:

            # Retrieve volunteer information entered into the form when editing an existing volunteer
            old_primary_address = Address.query.filter_by(
                id=volunteer.primary_address_id).first()
            if old_primary_address is not None:
                db.session.delete(old_primary_address)
                db.session.commit()
            old_secondary_address = Address.query.filter_by(
                id=volunteer.secondary_address_id).first()
            if old_secondary_address is not None:
                db.session.delete(old_secondary_address)
                db.session.commit()

            updated_volunteer = volunteer
            updated_volunteer.salutation = form.salutation.data
            updated_volunteer.primary_address_id = primary_address.id
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
            updated_volunteer.general_notes = form.general_notes.data
            db.session.add(updated_volunteer)
            db.session.commit()

            if member_volunteer is not None:
                updated_member = Member.query.filter_by(
                    id=volunteer.member_id).first()
                updated_member.salutation = form.salutation.data
                updated_member.primary_address_id = primary_address.id
                updated_member.secondary_address_id = secondary_address.id if secondary_address else None
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
                db.session.add(updated_member)
                db.session.commit()
            flash(
                'Volunteer {} successfully updated'.format(
                    form.first_name.data), 'success')
        else:

            # Retrieve volunteer information entered into the form when creating a new volunteer
            availability = Availability()
            db.session.add(availability)
            db.session.commit()

            volunteer = Volunteer(
                member_id=form.member_id.data,
                salutation=form.salutation.data,
                primary_address_id=primary_address.id,
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
                is_member_volunteer=True if member_volunteer else False,
                availability_id=availability.id,
                general_notes=form.general_notes.data)
            db.session.add(volunteer)
            db.session.commit()

            if member_volunteer is not None:
                updated_member = member
                updated_member.volunteer_id = volunteer.id
                updated_member.salutation = form.salutation.data

                old_member_primary_address = Address.query.filter_by(
                    id=member.primary_address_id).first()
                if old_member_primary_address is not None:
                    db.session.delete(old_member_primary_address)
                    db.session.commit()
                old_member_secondary_address = Address.query.filter_by(
                    id=member.secondary_address_id).first()
                if old_member_secondary_address is not None:
                    db.session.delete(old_member_secondary_address)
                    db.session.commit()

                updated_member.primary_address_id = primary_address.id
                updated_member.secondary_address_id = secondary_address.id if secondary_address else None
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
                db.session.add(updated_member)
                db.session.commit()
            flash(
                'Volunteer {} successfully added'.format(form.first_name.data),
                'success')

        return redirect(url_for('admin.people_manager', active='volunteer'))

    return render_template('admin/people_manager/volunteer_manager.html',
                           form=form, member_volunteer=member_volunteer)


@admin.route('/invite-member-volunteer', methods=['GET', 'POST'])
@login_required
@admin_required
def invite_member_volunteer():
    """Invites a user to create a member volunteer account"""
    form = AddMemberVolunteer()
    member_choices = [
        (member.id, member.first_name + " " + member.last_name)
        for member in Member.query.filter_by(volunteer_id=None).all()
    ]

    if form.validate_on_submit():
        member_name = form.member.data
        member_first_name = member_name.split()[0].capitalize()
        member = Member.query.filter_by(
            first_name=member_first_name).first()

        return redirect(url_for('admin.invite_volunteer', user_id=member.id, member_volunteer=True))

    return render_template('admin/people_manager/member_volunteer.html', form=form, member_choices=member_choices)


@admin.route('/invite-local-resource', methods=['GET', 'POST'])
@admin.route('/invite-local-resource/<int:local_resource_id>',
             methods=['GET', 'POST'])
@login_required
@admin_required
def invite_local_resource(local_resource_id=None):
    """Page for contactor management."""
    local_resource = None
    form = LocalResourceManager()

    # Get local resource information from the Local Resource table if the user is editing an existing local resource
    if local_resource_id is not None:
        local_resource = LocalResource.query.filter_by(
            id=local_resource_id).first()

        primary_address = Address.query.filter_by(
            id=local_resource.address_id).first()
        primary_metro_area = None
        # Get primary address information from the Address table
        if primary_address is not None:
            primary_address1 = primary_address.address1
            primary_address2 = primary_address.address2
            primary_city = primary_address.city
            primary_state = primary_address.state
            primary_zip_code = primary_address.zipcode
            primary_country = primary_address.country

            # Get metro area information from the Metro Area table if the primary address has a metro area
            if primary_address.metro_area_id is not None:
                primary_metro_area = MetroArea.query.filter_by(
                    id=primary_address.metro_area_id).first()

        # Populate existing information
        form = LocalResourceManager(
            first_name=local_resource.contact_first_name,
            middle_initial=local_resource.contact_middle_initial,
            last_name=local_resource.contact_last_name,
            salutation=local_resource.contact_salutation,
            company_name=local_resource.company_name,
            primary_address1=primary_address1 if primary_address else None,
            primary_address2=primary_address2 if primary_address else None,
            primary_city=primary_city if primary_address else None,
            primary_state=primary_state if primary_address else None,
            primary_zip_code=primary_zip_code if primary_address else None,
            primary_country=primary_country if primary_address else None,
            primary_metro_area=primary_metro_area if primary_metro_area else None,
            primary_phone_number=local_resource.primary_phone_number,
            email_address=local_resource.email_address,
            preferred_contact_method=local_resource.preferred_contact_method,
            website=local_resource.website)

    if form.validate_on_submit():

        # Retrieve address and metro area information entered into the form
        primary_metro_area = None
        if form.primary_metro_area.data:
            primary_metro_area = form.primary_metro_area.data

        address = Address(name=form.company_name.data,
                          address1=form.primary_address1.data,
                          address2=form.primary_address2.data,
                          city=form.primary_city.data,
                          state=form.primary_state.data,
                          zipcode=form.primary_zip_code.data,
                          country=form.primary_country.data,
                          metro_area_id=primary_metro_area.id if primary_metro_area else None)

        db.session.add(address)
        db.session.commit()

        if local_resource is not None:

            # Retrieve local resource information entered into the form when editing an existing local resource
            old_address = Address.query.filter_by(
                id=local_resource.address_id).first()
            if old_address is not None:
                db.session.delete(old_address)
                db.session.commit()

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

            # Retrieve local resource information entered into the form when creating a new local resource
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

    return render_template('admin/people_manager/local_resource_manager.html',
                           form=form)


@admin.route('/add-volunteer-services/<int:volunteer_id>',
             methods=['GET', 'POST'])
@login_required
@admin_required
def add_volunteer_services(volunteer_id=None):
    """Page for volunteer services management."""

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
            'Services Volunteer {} can provide successfully updated'.format(
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
    """Page for local resource review management."""

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
        'Successfully deleted Review by {}'.format(
            review.reviewer_name), 'success')
    return redirect(url_for('admin.add_local_resource_review', local_resource_id=local_resource_id))


@ admin.route('/add-volunteer-vacation/<int:volunteer_id>',
              methods=['GET', 'POST'])
@ login_required
@ admin_required
def add_volunteer_vacation(volunteer_id=None):
    """Page for volunteer vacation management."""

    volunteer = Volunteer.query.filter_by(id=volunteer_id).first()
    vacations = Vacation.query.filter_by(v_id=volunteer_id).all()
    current_date = date.today()

    def vacation_sort(v):
        return v.start_date
    vacations.sort(key=vacation_sort)

    for v in vacations:
        if v.end_date < current_date:
            vacations.remove(v)
            db.session.delete(v)
            db.session.commit()

    form = AddVacation()
    form.vacation_identity.label = Label("vacation_identity", "Volunteer " + volunteer.first_name + " " +
                                         volunteer.last_name)

    if form.validate_on_submit():
        if form.start_date.data > form.end_date.data:
            flash(
                'The starting date of the vacation must come before the ending date!', 'error')
            return redirect(url_for('admin.add_volunteer_vacation', volunteer_id=volunteer_id))

        elif form.end_date.data < current_date:
            flash(
                'The ending date of the vacation must come after the current date!', 'error')
            return redirect(url_for('admin.add_volunteer_vacation', volunteer_id=volunteer_id))

        else:
            vacation = Vacation(
                start_date=form.start_date.data,
                end_date=form.end_date.data,
                v_id=volunteer_id)
            db.session.add(vacation)
            db.session.commit()

            flash(
                'Vacation for Volunteer {} successfully added'.format(
                    volunteer.last_name), 'success')
            return redirect(url_for('admin.people_manager', active='volunteer'))

    return render_template('admin/people_manager/vacation.html', form=form, vacations=vacations)


@ admin.route('/add-volunteer-vacation/_delete-vacation/<int:vacation_id>')
@ login_required
@ admin_required
def delete_vacation(vacation_id):
    """Delete a vacation."""
    vacation = Vacation.query.filter_by(id=vacation_id).first()
    volunteer_id = vacation.v_id
    db.session.delete(vacation)
    db.session.commit()
    flash(
        'Successfully deleted Vacation starting on {}'.format(
            vacation.start_date), 'success')
    return redirect(url_for('admin.add_volunteer_vacation', volunteer_id=volunteer_id))


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
        availability_monday_start=availability.availability_monday_start,
        availability_monday_end=availability.availability_monday_end,
        backup_monday_start=availability.backup_monday_start,
        backup_monday_end=availability.backup_monday_end,
        availability_tuesday_start=availability.availability_tuesday_start,
        availability_tuesday_end=availability.availability_tuesday_end,
        backup_tuesday_start=availability.backup_tuesday_start,
        backup_tuesday_end=availability.backup_tuesday_end,
        availability_wednesday_start=availability.availability_wednesday_start,
        availability_wednesday_end=availability.availability_wednesday_end,
        backup_wednesday_start=availability.backup_wednesday_start,
        backup_wednesday_end=availability.backup_wednesday_end,
        availability_thursday_start=availability.availability_thursday_start,
        availability_thursday_end=availability.availability_thursday_end,
        backup_thursday_start=availability.backup_thursday_start,
        backup_thursday_end=availability.backup_thursday_end,
        availability_friday_start=availability.availability_friday_start,
        availability_friday_end=availability.availability_friday_end,
        backup_friday_start=availability.backup_friday_start,
        backup_friday_end=availability.backup_friday_end,
        availability_saturday_start=availability.availability_saturday_start,
        availability_saturday_end=availability.availability_saturday_end,
        backup_saturday_start=availability.backup_saturday_start,
        backup_saturday_end=availability.backup_saturday_end,
        availability_sunday_start=availability.availability_sunday_start,
        availability_sunday_end=availability.availability_sunday_end,
        backup_sunday_start=availability.backup_sunday_start,
        backup_sunday_end=availability.backup_sunday_end)
    form.availability_identity.label = Label("availability_identity", "Volunteer " + volunteer.first_name + " " +
                                             volunteer.last_name)

    if form.validate_on_submit():
        updated_availability = availability
        updated_availability.availability_monday_start = form.availability_monday_start.data
        updated_availability.availability_monday_end = form.availability_monday_end.data
        updated_availability.backup_monday_start = form.backup_monday_start.data
        updated_availability.backup_monday_end = form.backup_monday_end.data
        updated_availability.availability_tuesday_start = form.availability_tuesday_start.data
        updated_availability.availability_tuesday_end = form.availability_tuesday_end.data
        updated_availability.backup_tuesday_start = form.backup_tuesday_start.data
        updated_availability.backup_tuesday_end = form.backup_tuesday_end.data
        updated_availability.availability_wednesday_start = form.availability_wednesday_start.data
        updated_availability.availability_wednesday_end = form.availability_wednesday_end.data
        updated_availability.backup_wednesday_start = form.backup_wednesday_start.data
        updated_availability.backup_wednesday_end = form.backup_wednesday_end.data
        updated_availability.availability_thursday_start = form.availability_thursday_start.data
        updated_availability.availability_thursday_end = form.availability_thursday_end.data
        updated_availability.backup_thursday_start = form.backup_thursday_start.data
        updated_availability.backup_thursday_end = form.backup_thursday_end.data
        updated_availability.availability_friday_start = form.availability_friday_start.data
        updated_availability.availability_friday_end = form.availability_friday_end.data
        updated_availability.backup_friday_start = form.backup_friday_start.data
        updated_availability.backup_friday_end = form.backup_friday_end.data
        updated_availability.availability_saturday_start = form.availability_saturday_start.data
        updated_availability.availability_saturday_end = form.availability_saturday_end.data
        updated_availability.backup_saturday_start = form.backup_saturday_start.data
        updated_availability.backup_saturday_end = form.backup_saturday_end.data
        updated_availability.availability_sunday_start = form.availability_sunday_start.data
        updated_availability.availability_sunday_end = form.availability_sunday_end.data
        updated_availability.backup_sunday_start = form.backup_sunday_start.data
        updated_availability.backup_sunday_end = form.backup_sunday_end.data
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
        availability_monday_start=availability.availability_monday_start,
        availability_monday_end=availability.availability_monday_end,
        backup_monday_start=availability.backup_monday_start,
        backup_monday_end=availability.backup_monday_end,
        availability_tuesday_start=availability.availability_tuesday_start,
        availability_tuesday_end=availability.availability_tuesday_end,
        backup_tuesday_start=availability.backup_tuesday_start,
        backup_tuesday_end=availability.backup_tuesday_end,
        availability_wednesday_start=availability.availability_wednesday_start,
        availability_wednesday_end=availability.availability_wednesday_end,
        backup_wednesday_start=availability.backup_wednesday_start,
        backup_wednesday_end=availability.backup_wednesday_end,
        availability_thursday_start=availability.availability_thursday_start,
        availability_thursday_end=availability.availability_thursday_end,
        backup_thursday_start=availability.backup_thursday_start,
        backup_thursday_end=availability.backup_thursday_end,
        availability_friday_start=availability.availability_friday_start,
        availability_friday_end=availability.availability_friday_end,
        backup_friday_start=availability.backup_friday_start,
        backup_friday_end=availability.backup_friday_end,
        availability_saturday_start=availability.availability_saturday_start,
        availability_saturday_end=availability.availability_saturday_end,
        backup_saturday_start=availability.backup_saturday_start,
        backup_saturday_end=availability.backup_saturday_end,
        availability_sunday_start=availability.availability_sunday_start,
        availability_sunday_end=availability.availability_sunday_end,
        backup_sunday_start=availability.backup_sunday_start,
        backup_sunday_end=availability.backup_sunday_end)
    form.availability_identity.label = Label(
        "availability_identity", "Local Resource " + localResource.company_name)

    if form.validate_on_submit():
        updated_availability = availability
        updated_availability.availability_monday_start = form.availability_monday_start.data
        updated_availability.availability_monday_end = form.availability_monday_end.data
        updated_availability.backup_monday_start = form.backup_monday_start.data
        updated_availability.backup_monday_end = form.backup_monday_end.data
        updated_availability.availability_tuesday_start = form.availability_tuesday_start.data
        updated_availability.availability_tuesday_end = form.availability_tuesday_end.data
        updated_availability.backup_tuesday_start = form.backup_tuesday_start.data
        updated_availability.backup_tuesday_end = form.backup_tuesday_end.data
        updated_availability.availability_wednesday_start = form.availability_wednesday_start.data
        updated_availability.availability_wednesday_end = form.availability_wednesday_end.data
        updated_availability.backup_wednesday_start = form.backup_wednesday_start.data
        updated_availability.backup_wednesday_end = form.backup_wednesday_end.data
        updated_availability.availability_thursday_start = form.availability_thursday_start.data
        updated_availability.availability_thursday_end = form.availability_thursday_end.data
        updated_availability.backup_thursday_start = form.backup_thursday_start.data
        updated_availability.backup_thursday_end = form.backup_thursday_end.data
        updated_availability.availability_friday_start = form.availability_friday_start.data
        updated_availability.availability_friday_end = form.availability_friday_end.data
        updated_availability.backup_friday_start = form.backup_friday_start.data
        updated_availability.backup_friday_end = form.backup_friday_end.data
        updated_availability.availability_saturday_start = form.availability_saturday_start.data
        updated_availability.availability_saturday_end = form.availability_saturday_end.data
        updated_availability.backup_saturday_start = form.backup_saturday_start.data
        updated_availability.backup_saturday_end = form.backup_saturday_end.data
        updated_availability.availability_sunday_start = form.availability_sunday_start.data
        updated_availability.availability_sunday_end = form.availability_sunday_end.data
        updated_availability.backup_sunday_start = form.backup_sunday_start.data
        updated_availability.backup_sunday_end = form.backup_sunday_end.data
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

    # Delete addresses unless the member is linked to a volunteer
    if member.volunteer_id is not None:
        linked_volunteer = Volunteer.query.filter_by(
            id=member.volunteer_id).first()
        linked_volunteer.member_id = None
        linked_volunteer.is_member_volunteer = False
        db.session.add(linked_volunteer)
        db.session.commit()

    else:
        primary_address = Address.query.filter_by(
            id=member.primary_address_id).first()
        if primary_address is not None:
            db.session.delete(primary_address)
            db.session.commit()
        secondary_address = Address.query.filter_by(
            id=member.secondary_address_id).first()
        if secondary_address is not None:
            db.session.delete(secondary_address)
            db.session.commit()

    # Delete member
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

    # Delete addresses unless the volunteer is linked to a member
    if volunteer.member_id is not None:
        linked_member = Member.query.filter_by(
            id=volunteer.member_id).first()
        linked_member.volunteer_id = None
        db.session.add(linked_member)
        db.session.commit()

    else:
        primary_address = Address.query.filter_by(
            id=volunteer.primary_address_id).first()
        if primary_address is not None:
            db.session.delete(primary_address)
            db.session.commit()
        secondary_address = Address.query.filter_by(
            id=volunteer.secondary_address_id).first()
        if secondary_address is not None:
            db.session.delete(secondary_address)
            db.session.commit()

    # Delete availability
    availability = Availability.query.filter_by(
        id=volunteer.availability_id).first()
    if availability is not None:
        db.session.delete(availability)
        db.session.commit()

    # Delete vacation days
    for vacation in Vacation.query.filter_by(v_id=volunteer_id):
        db.session.delete(vacation)
        db.session.commit()

    # Delete provided services
    for service in ProvidedService.query.filter_by(volunteer_id=volunteer_id):
        db.session.delete(service)
        db.session.commit()

    # Delete volunteer
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

    # Delete address
    address = Address.query.filter_by(
        id=localResource.address_id).first()
    if address is not None:
        db.session.delete(address)
        db.session.commit()

    # Delete availability
    availability = Availability.query.filter_by(
        id=localResource.availability_id).first()
    if availability is not None:
        db.session.delete(availability)
        db.session.commit()

    # Delete reviews
    for review in Review.query.filter_by(lr_id=local_resource_id):
        db.session.delete(review)
        db.session.commit()

    # Delete local resource
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
    services = Service.query.filter_by(category_id=service.category_id).all()

    if services is not None and len(services) <= 1:
        flash('Cannot delete the last service in a service category.', 'error')

    elif services is not None and len(services) > 1:
        provided_services = ProvidedService.query.filter_by(
            service_id=service_id).all()
        if provided_services is not None:
            for provided_service in provided_services:
                if provided_service is not None:
                    db.session.delete(provided_service)
                    db.session.commit()

        transportation_requests = TransportationRequest.query.filter_by(
            service_id=service_id).all()
        office_time_requests = OfficeRequest.query.filter_by(
            service_id=service_id).all()
        members_home_requests = MembersHomeRequest.query.filter_by(
            service_id=service_id).all()

        requests_to_delete = transportation_requests + \
            office_time_requests + members_home_requests
        for request in requests_to_delete:
            if request is not None:
                delete_request(request.type_id, request.id)

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
    category = ServiceCategory.query.filter_by(id=category_id).first()
    categories = ServiceCategory.query.filter_by(
        request_type_id=category.request_type_id).all()

    if categories is not None and len(categories) <= 1:
        flash('Cannot delete the last service category of a request form.', 'error')

    elif categories is not None and len(categories) > 1:
        transportation_requests = TransportationRequest.query.filter_by(
            service_category_id=category_id).all()
        office_time_requests = OfficeRequest.query.filter_by(
            service_category_id=category_id).all()
        members_home_requests = MembersHomeRequest.query.filter_by(
            service_category_id=category_id).all()

        requests_to_delete = transportation_requests + \
            office_time_requests + members_home_requests
        for request in requests_to_delete:
            if request is not None:
                delete_request(request.type_id, request.id)
                db.session.commit()

        services = Service.query.filter_by(category_id=category_id).all()
        for service in services:
            provided_services = ProvidedService.query.filter_by(
                service_id=service.id).all()
            if provided_services is not None:
                for provided_service in provided_services:
                    if provided_service is not None:
                        db.session.delete(provided_service)
                        db.session.commit()
            db.session.delete(service)
            db.session.commit()

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


@admin.route('/edit-metro-areas', methods=['GET', 'POST'])
@admin.route('/edit-metro-areas/<int:metro_area_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_metro_areas(metro_area_id=None):
    """Create a new metro area or edit existing metro areas."""
    metro_area = None
    form = EditMetroAreaForm()

    if metro_area_id is not None:
        metro_area = MetroArea.query.filter_by(id=metro_area_id).first()
        form = EditMetroAreaForm(name=metro_area.name)

    if form.validate_on_submit():
        if metro_area is not None:
            updated_metro_area = metro_area
            updated_metro_area.name = form.name.data
            db.session.add(updated_metro_area)
            db.session.commit()
            flash('Metro Area {} successfully updated'.format(updated_metro_area.name),
                  'success')
        else:
            metro_area = MetroArea(name=form.name.data)
            db.session.add(metro_area)
            db.session.commit()
            flash('Metro Area {} successfully created'.format(metro_area.name),
                  'success')
        return redirect(url_for('admin.registered_metro_areas'))

    if metro_area is not None:
        return render_template('admin/system_manager/manage_metro_area.html',
                               form=form, metro_area=metro_area)
    else:
        return render_template('admin/system_manager/manage_metro_area.html',
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


@admin.route('/add-transportation-address', methods=["GET", "POST"])
def transport_address_addition():
    json = request.get_json()
    new_address = Address(
        name=json["address-name"],
        address1=json["street-address"],
        address2=json["addr-cont"],
        city=json["city"],
        state=json["state"],
        country=json["country"],
        zipcode=json["zip"]
    )
    db.session.add(new_address)
    db.session.commit()
    return jsonify("OK")


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
