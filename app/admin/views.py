import json
import sys
import time
from operator import __truediv__

from flask import (Blueprint, abort, flash, redirect, render_template, request,
                   send_file, url_for)
from flask_login import current_user, login_required
from flask_rq import get_queue

from app import db
from app.admin.forms import (AddAvailability, AddServiceToVolunteer,
                             AddServiceVetting, ChangeAccountTypeForm,
                             ChangeUserEmailForm, ContractorManager,
                             EditMetroAreaForm, EditServiceForm, EditServiceCategoryForm,
                             InviteUserForm, MemberManager, MultiCheckboxField,
                             NewUserForm, Reviews, SearchRequestForm,
                             TransportationRequestForm, VolunteerManager, GeneratePdfForm)
from app.decorators import admin_required
from app.email import send_email
from app.models import (Address, Availability, EditableHTML, LocalResource,
                        Member, MetroArea, ProvidedService, Request, Role,
                        Service, ServiceCategory, Staffer, User, Volunteer)
from app.models.request import RequestDurationType, RequestStatus, RequestType
from app.models.request_volunteer_record import RequestVolunteerRecord

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
    add_availability = AddAvailability()
    add_vetting = AddServiceVetting()
    service_categories = sorted(
        [(category.name, category.request_type_id, category.id)
         for category in ServiceCategory.query.all()],
        key=lambda triple: triple[2])
    services = [(service.name, service.category_id, service.id)
                for service in Service.query.all()]
    reviews = Reviews()
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

    # VETTINGS UPDATED
    if add_vetting.validate_on_submit():
        # NEED TO CHANGE THIS SO THAT WE UPDATE VETTINGS BASED ON WHICH USER WAS SELECTED
        volunteer = Volunteer.query.first()
        volunteer.vettings = add_vetting.vetting_notes.data
        volunteer.is_fully_vetted = add_vetting.volunteer_fully_vetted_checkbox.data
        db.session.commit()
        flash(
            'Vettings for user {} successfully saved.'.format(
                volunteer.first_name), 'form-success')

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

    members = Member.query.all()
    volunteers = Volunteer.query.all()
    local_resources = LocalResource.query.all()
    return render_template('admin/people_manager/layouts/base.html',
                           add_availability=add_availability,
                           add_vetting=add_vetting,
                           service_form=service_form,
                           category_dict=category_dict,
                           reviews=reviews,
                           members=members,
                           volunteers=volunteers,
                           local_resources=local_resources)


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

    temp_requests = [{
        'request_num': 6724,
        'request_status': "Requested",
        'requested_date_display': "06/17",
        'requested_date_full': "06/17/2021",
        'requested_day_of_week': "Saturday",
        'start_time': "12:00 PM",
        'end_time': "12:00 PM",
        'member_name': "Anne Rodda",
        'volunteer_name': "Fran Spadafora Manzella",
        'is_volunteer': True,
        'request_type': "Member's Home",
        'service': "Pet Care -Vol",
        'created_date': "06/15/2021",
        'modified_date': "N/A",
        'service_category': "Volunteer In-Home Support",
        'member_number': -2
    }, {
        'request_num': 6697,
        'request_status': "Confirmed",
        'requested_date_display': "06/21",
        'requested_date_full': "06/21/2021",
        'requested_day_of_week': "Wednesday",
        'start_time': "11:30 AM",
        'end_time': "12:40 PM",
        'member_name': "Randy Warden",
        'volunteer_name': "Hank Dullea",
        'is_volunteer': True,
        'request_type': "Transportation",
        'service': "Vol Driver Local Medical Appt",
        'created_date': "06/11/2021",
        'modified_date': "06/18/2021",
        'service_category': "Transportation",
        'member_number': -1
    }]

    # Pull existing requests from the database and format each of them for display on front-end.
    db_requests = Request.query.all()
    formatted_db_requests = []
    for db_req in db_requests:
        member = Member.query.get(db_req.requesting_member_id)

        request_volunteer_record = RequestVolunteerRecord.query.filter_by(
            request_id=db_req.id).first()
        volunteer = Volunteer.query.get(request_volunteer_record.volunteer_id)

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
            f"{member.first_name} {member.last_name}",
            'member_number':
            member.member_number,
            'volunteer_name':
            f"{volunteer.first_name} {volunteer.last_name}",
            'volunteer_id':
            volunteer.id,
            'is_volunteer':
            True,
            'request_type':
            RequestType.query.get(db_req.type_id).name,
            'service_category':
            ServiceCategory.query.get(db_req.service_category_id).name,
            'service':
            Service.query.get(db_req.service_id).name,
            'created_date':
            db_req.created_date.strftime("%m/%d/%Y"),
            'modified_date':
            db_req.modified_date.strftime("%m/%d/%Y")
        })

    temp_requests.extend(formatted_db_requests)
    return render_template('admin/request_manager/search_request.html',
                           title='Search Request',
                           form=form,
                           service_providers=service_providers,
                           requests=temp_requests,
                           num_requests=len(temp_requests))


# Create a new service request.
@admin.route('/create-request', methods=['GET', 'POST'])
@admin_required
def create_request():
    return render_template('admin/request_manager/create_request.html')


# Create a new Transportation service request.
@admin.route('/create-request/transportation-request', methods=['GET', 'POST'])
@admin_required
def create_transportation_request():
    form = TransportationRequestForm()
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
                                 address.name + " - " + address.street_address)
                                for address in Address.query.all()]
    form.starting_location.choices = [
        (address.id, address.name + " " + address.street_address)
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
    if form.validate_on_submit():
        special_input = request.form.get('special_instructions')
        transportation_request = Request(
            type_id=0,
            status_id=form.status.data.id,
            short_description=form.description.data,
            created_date=form.date_created.data,
            requested_date=form.requested_date.data,
            initial_pickup_time=form.initial_pickup.data,
            appointment_time=form.appointment.data,
            return_pickup_time=form.return_pickup.data,
            drop_off_time=form.drop_off.data,
            is_date_time_flexible=form.time_flexible.data,
            duration_type_id=form.duration.data,
            service_category_id=form.service_category.data.id,
            service_id=form.transportation_service.data.id if
            form.service_category.data.id == 0 else form.covid_service.data.id,
            starting_address=form.starting_location.data,
            destination_address_id=form.destination.data,
            # Will be updated in the future for multiple ppl
            requesting_member_id=form.requesting_member.data[0],
            special_instructions=special_input,
            followup_date=form.follow_up_date.data,
            responsible_staffer_id=form.responsible_staffer.data,
            contact_log_priority_id=form.contact_log_priority.data.id,
            cc_email=form.person_to_cc.data)
        db.session.add(transportation_request)
        db.session.commit()
        print(form.service_provider.data)
        request_volunteer_record = RequestVolunteerRecord(
            request_id=transportation_request.id,
            volunteer_id=form.service_provider.data[0],
            status_id=-1,
            staffer_id=-1,
            updated_datetime=form.date_created.data)
        db.session.add(request_volunteer_record)
        db.session.commit()

        flash('Successfully submitted a new transportation request', 'success')
        return redirect(url_for('admin.search_request'))
    # elif (len(form.errors) > 0):
    # else:
    # flash(request.method, 'error')
    # flash(form.errors, 'error')
    return render_template('admin/request_manager/transportation_request.html',
                           title='Transportation Request',
                           form=form)


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
        primary_address1 = primary_address.street_address
        primary_city = primary_address.city
        primary_state = primary_address.state
        primary_zip_code = primary_address.zipcode
        secondary_address1 = None
        secondary_city = None
        secondary_state = None
        secondary_zip_code = None
        if member.secondary_address_id is not None:
            secondary_address = Address.query.filter_by(
                id=member.secondary_address_id).first()
            secondary_address1 = secondary_address.street_address
            secondary_city = secondary_address.city
            secondary_state = secondary_address.state
            secondary_zip_code = secondary_address.zipcode
        primary_city = primary_address.city
        primary_state = primary_address.state
        primary_zip_code = primary_address.zipcode
        #primary_metro_area = primary_address.metro_area
        form = MemberManager(
            first_name=member.first_name,
            middle_initial=member.middle_initial,
            last_name=member.last_name,
            preferred_name=member.preferred_name,
            salutation=member.salutation,
            gender=member.gender,
            birthdate=member.birthdate,
            primary_address1=primary_address1,
            primary_city=primary_city,
            primary_state=primary_state,
            primary_zip_code=primary_zip_code,
            secondary_address1=secondary_address1,
            secondary_city=secondary_city,
            secondary_state=secondary_state,
            secondary_zip_code=secondary_zip_code,
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
                street_address=form.secondary_address1.data + " " +
                form.secondary_address2.data,
                city=form.secondary_city.data,
                state=form.secondary_state.data,
                zipcode=form.secondary_zip_code.data)
            if form.primary_address1.data:
                secondary_address = Address(
                    name=form.first_name.data + " " + form.last_name.data,
                    street_address=form.primary_address1.data + " " +
                    form.primary_address2.data,
                    city=form.primary_city.data,
                    state=form.primary_state.data,
                    zipcode=form.primary_zip_code.data)
            if form.secondary_metro_area.data:
                metro = MetroArea(name=form.secondary_metro_area.data)
        else:
            address = Address(name=form.first_name.data + " " +
                              form.last_name.data,
                              street_address=form.primary_address1.data + " " +
                              form.primary_address2.data,
                              city=form.primary_city.data,
                              state=form.primary_state.data,
                              zipcode=form.primary_zip_code.data)
            if form.secondary_address1.data:
                secondary_address = Address(
                    name=form.first_name.data + " " + form.last_name.data,
                    street_address=form.secondary_address1.data + " " +
                    form.secondary_address2.data,
                    city=form.secondary_city.data,
                    state=form.secondary_state.data,
                    zipcode=form.secondary_zip_code.data)
            #membership_expiration_date = member.membership_expiration_date

    if form.validate_on_submit():
        secondary_address = False
        if (form.secondary_as_primary_checkbox.data):
            address = Address(
                name=form.first_name.data + " " + form.last_name.data,
                street_address=form.secondary_address1.data + " " +
                form.secondary_address2.data,
                city=form.secondary_city.data)
            secondary_address = Address(
                name=form.first_name.data + " " + form.last_name.data,
                street_address=form.primary_address1.data + " " +
                form.primary_address2.data,
                city=form.primary_city.data)
            if form.secondary_metro_area.data:
                metro = MetroArea(name=form.secondary_metro_area.data)
        else:
            address = Address(name=form.first_name.data + " " +
                              form.last_name.data,
                              street_address=form.primary_address1.data + " " +
                              form.primary_address2.data,
                              city=form.primary_city.data)
            if form.secondary_address1.data:
                secondary_address = Address(
                    name=form.first_name.data + " " + form.last_name.data,
                    street_address=form.secondary_address1.data + " " +
                    form.secondary_address2.data,
                    city=form.secondary_city.data)
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
            updated_member.primary_address_id = int(address.id)
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
                'Member {} successfully created'.format(form.first_name.data),
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
        setattr(VolunteerManager, key, value)

    # for editing existing Volunteer profiles
    volunteer = None
    form = VolunteerManager()
    if volunteer_id is not None:
        volunteer = Volunteer.query.filter_by(id=volunteer_id).first()
        primary_address = Address.query.filter_by(
            id=volunteer.primary_address_id).first()
        primary_street_address = primary_address.street_address
        primary_city = primary_address.city
        primary_state = primary_address.state
        primary_zip_code = primary_address.zipcode
        form = VolunteerManager(
            salutation=volunteer.salutation,
            first_name=volunteer.first_name,
            middle_initial=volunteer.middle_initial,
            last_name=volunteer.last_name,
            gender=volunteer.gender,
            birthdate=volunteer.birthdate,
            preferred_name=volunteer.preferred_name,
            street_address=primary_street_address,
            primary_city=primary_city,
            primary_state=primary_state,
            primary_zip_code=primary_zip_code,
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

    service_ids = []
    if form.validate_on_submit():
        for key, value in category_dict.items():
            service_input = getattr(form, key)
            service_data = service_input.data
            for service in service_data:
                service_to_be_committed = Service.query.filter_by(
                    name=service,
                    category_id=int(category_name_to_id[key])).first()
                service_ids.append(service_to_be_committed.id)
        address = Address(name=form.first_name.data + " " +
                          form.last_name.data,
                          street_address=form.street_address.data,
                          city=form.primary_city.data,
                          state=form.primary_state.data,
                          zipcode=form.primary_zip_code.data)
        db.session.add(address)
        db.session.commit()

        if volunteer is not None:
            updated_volunteer = volunteer
            updated_volunteer.salutation = form.salutation.data
            updated_volunteer.primary_address_id = int(address.id)
            # updated_volunteer.secondary_address_id=secondary_address.id if secondary_address else None
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
            flash(
                'Volunteer {} successfully updated'.format(
                    form.first_name.data), 'success')
        else:
            availability = Availability()
            db.session.add(availability)
            db.session.commit()

            volunteer = Volunteer(
                salutation=form.salutation.data,
                first_name=form.first_name.data,
                middle_initial=form.middle_initial.data,
                last_name=form.last_name.data,
                preferred_name=form.preferred_name.data,
                gender=form.gender.data,
                birthdate=form.birthdate.data,
                primary_address_id=address.id,
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
                is_fully_vetted=False,  # What should be default?
                availability_id=availability.id,
                general_notes=form.notes.data)
            db.session.add(volunteer)
            db.session.commit()
            flash(
                'Volunteer {} successfully added'.format(form.first_name.data),
                'success')

        return redirect(url_for('admin.people_manager'))

        for service in service_ids:
            provided_service = ProvidedService(service_id=service,
                                               volunteer_id=volunteer.id)
            db.session.add(provided_service)
            db.session.commit()
        flash('Volunteer {} successfully invited'.format(form.first_name.data),
              'form-success')
    return render_template('admin/people_manager/volunteer_manager.html',
                           form=form,
                           services=services,
                           service_categories=service_categories,
                           category_dict=category_dict)


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
        primary_street_address = primary_address.street_address
        primary_city = primary_address.city
        primary_state = primary_address.state
        primary_country = primary_address.country
        primary_zip_code = primary_address.zipcode
        form = ContractorManager(
            first_name=local_resource.contact_first_name,
            middle_initial=local_resource.contact_middle_initial,
            last_name=local_resource.contact_last_name,
            salutation=local_resource.contact_salutation,
            company_name=local_resource.company_name,
            primary_country=primary_country,
            street_address=primary_street_address,
            primary_city=primary_city,
            primary_state=primary_state,
            primary_zip_code=primary_zip_code,
            primary_phone_number=local_resource.primary_phone_number,
            email_address=local_resource.email_address,
            preferred_contact_method=local_resource.preferred_contact_method,
            website=local_resource.website)

    if form.validate_on_submit():
        address = Address(name=form.company_name.data,
                          street_address=form.street_address.data,
                          city=form.primary_city.data,
                          state=form.primary_state.data,
                          zipcode=form.primary_zip_code.data,
                          country=form.primary_country.data)
        db.session.add(address)
        db.session.commit()

        if local_resource is not None:
            updated_local_resource = local_resource
            updated_local_resource.address_id = int(address.id)
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

        return redirect(url_for('admin.people_manager'))

    return render_template('admin/people_manager/contractor_manager.html',
                           form=form)


@admin.route('/add-availability-volunteer/<int:volunteer_id>',
             methods=['GET', 'POST'])
@login_required
@admin_required
def add_availability_volunteer(volunteer_id=None):
    """Page for availability management."""
    print('Hello world!', file=sys.stderr)

    volunteer = Volunteer.query.filter_by(id=volunteer_id).first()
    availability_id = volunteer.availability_id
    print(f'Availability ID is {availability_id}', file=sys.stderr)

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
    print(form.errors, file=sys.stderr)

    if form.is_submitted():
        print("submitted", file=sys.stderr)

    if form.validate_on_submit():
        print('Form validate on submit.', file=sys.stderr)

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
            'Availability for {} successfully updated'.format(
                volunteer.last_name), 'success')
        return redirect(url_for('admin.people_manager'))
    else:
        print(form.errors, file=sys.stderr)
        print(form.backup_monday.data, file=sys.stderr)
    return render_template('admin/people_manager/availability.html', form=form)


@admin.route('/add-availability-local-resource/<int:local_resource_id>',
             methods=['GET', 'POST'])
@login_required
@admin_required
def add_availability_local_resource(local_resource_id=None):
    """Page for availability management."""
    print('Hello world!', file=sys.stderr)

    localResource = LocalResource.query.filter_by(id=local_resource_id).first()
    availability_id = localResource.availability_id
    print(f'Availability ID is {availability_id}', file=sys.stderr)

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
    print(form.errors, file=sys.stderr)

    if form.is_submitted():
        print("submitted", file=sys.stderr)

    if form.validate_on_submit():
        print('Form validate on submit.', file=sys.stderr)

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
            'Availability for {} successfully updated'.format(
                localResource.company_name), 'success')
        return redirect(url_for('admin.people_manager'))
    else:
        print(form.errors, file=sys.stderr)
        print(form.backup_monday.data, file=sys.stderr)
    return render_template('admin/people_manager/availability.html', form=form)


@admin.route('/people-manager/<int:member_id>/_delete-member')
@login_required
@admin_required
def delete_member(member_id):
    """Delete a member."""
    member = Member.query.filter_by(id=member_id).first()
    db.session.delete(member)
    db.session.commit()
    flash(
        'Successfully deleted member {}'.format(member.first_name + '' +
                                                member.last_name), 'success')
    return redirect(url_for('admin.people_manager'))


@admin.route('/people-manager/<int:volunteer_id>/_delete-volunteer')
@login_required
@admin_required
def delete_volunteer(volunteer_id):
    """Delete a volunteer."""
    volunteer = Volunteer.query.filter_by(id=volunteer_id).first()
    db.session.delete(volunteer)
    db.session.commit()
    flash(
        'Successfully deleted volunteer {}'.format(volunteer.first_name + '' +
                                                   volunteer.last_name),
        'success')
    return redirect(url_for('admin.people_manager'))


@admin.route('/people-manager/<int:local_resource_id>/_delete-local-resource')
@login_required
@admin_required
def delete_local_resource(local_resource_id):
    """Delete a local resource."""
    localResource = LocalResource.query.filter_by(id=local_resource_id).first()
    db.session.delete(localResource)
    db.session.commit()
    flash(
        'Successfully deleted local resource {}'.format(
            localResource.company_name), 'success')
    return redirect(url_for('admin.people_manager'))


@admin.route('/services')
@login_required
@admin_required
def registered_services():
    """Manage services."""
    services = Service.query.all()
    return render_template('admin/system_manager/registered_services.html',
                           services=services)


# @admin.route('/services/<int:service_id>', methods=['GET', 'POST'])
@admin.route('/services/info/<int:service_id>', methods=['GET', 'POST'])
@login_required
@admin_required
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
        db.session.add(updated_service)
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
        template_vars = {"title": "Love Living at Home", "data": data.to_html()}
        html_out = template.render(template_vars)
        HTML(string=html_out).write_pdf(
            "./app/reports/" + file_name + ".pdf", stylesheets=["./app/assets/styles/report.css"])
        try:
            return send_file(file_name + ".pdf", as_attachment=True)
        except FileNotFoundError:
            flash('Failed to generate report.', 'error')
            abort(404)
    return render_template('admin/system_manager/generate_report.html', form = pdf_form)
