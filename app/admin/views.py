from flask import (Blueprint, abort, flash, redirect, render_template, request,
                   url_for)
from flask_login import current_user, login_required
from flask_rq import get_queue

from app import db

from app.admin.forms import (ChangeAccountTypeForm, ChangeUserEmailForm,
                             ContractorManager, InviteUserForm, MemberManager,
                             NewUserForm, TransportationRequestForm,
                             VolunteerManager, SearchRequestForm, AddServiceVetting,
                             AddAvailability, Reviews, EditServiceForm, MultiCheckboxField, EditMetroAreaForm, AddServiceToVolunteer)
from app.decorators import admin_required
from app.email import send_email
from app.models import (EditableHTML, Role, User, Member, Address, ServiceCategory,
                        Service,  Request, service_category, LocalResource, Volunteer,
                        MetroArea, ProvidedService)


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


@admin.route('/people-manager',  methods=['GET', 'POST'])
@login_required
@admin_required
def people_manager():
    """People Manager Page."""
    add_availability = AddAvailability()
    add_vetting = AddServiceVetting()
    service_categories = sorted([(category.name, category.request_type_id, category.id)
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
        category_dict[category[0]] = MultiCheckboxField(
            category[0], choices=choices)
    for key, value in category_dict.items():
        setattr(AddServiceToVolunteer, key, value)
    service_form = AddServiceToVolunteer()

    # NEED TO CHANGE THIS SO THAT WE UPDATE VETTINGS BASED ON WHICH USER WAS SELECTED
    volunteer = Volunteer.query.first()

    ## VETTINGS UPDATED 
    if add_vetting.validate_on_submit():
        # NEED TO CHANGE THIS SO THAT WE UPDATE VETTINGS BASED ON WHICH USER WAS SELECTED
        volunteer = Volunteer.query.first()
        volunteer.vettings = add_vetting.vetting_notes.data
        volunteer.is_fully_vetted = add_vetting.volunteer_fully_vetted_checkbox.data
        db.session.commit()
        flash(
            'Vettings for user {} successfully saved.'.format(
                volunteer.first_name), 'form-success')

    ## SERVICES UPDATED 
    if service_form.validate_on_submit():
        for key, value in category_dict.items():
            service_input = getattr(service_form, key)
            service_data = service_input.data
            for service in service_data:
                service_to_be_committed = Service.query.filter_by(
                    name=service, category_id=int(category_name_to_id[key])).first()
                provided_service = ProvidedService(
                service_id=service_to_be_committed.id, volunteer_id=volunteer.id)
                db.session.add(provided_service)
                db.session.commit()
            flash('Services provided by {} successfully updated'.format(volunteer.first_name), 'form-success')

    return render_template('admin/people_manager/layouts/base.html',
                           add_availability=add_availability,
                           add_vetting=add_vetting,
                           service_form = service_form, 
                           category_dict = category_dict)


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
            type_id=1,
            status_id=form.status.data.id,
            # update later to short description
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
        secondary_address = False
        if (form.secondary_as_primary_checkbox.data):
            address = Address(name=form.first_name.data + " " + form.last_name.data,
                              street_address=form.secondary_address1.data + " " + form.secondary_address2.data,
                              city=form.secondary_city.data)
            secondary_address = Address(name=form.first_name.data + " " + form.last_name.data,
                                        street_address=form.primary_address1.data + " " + form.primary_address2.data,
                                        city=form.primary_city.data)
            if form.secondary_metro_area.data:
                metro = MetroArea(name=form.secondary_metro_area.data)
        else:
            address = Address(name=form.first_name.data + " " + form.last_name.data,
                              street_address=form.primary_address1.data + " " + form.primary_address2.data,
                              city=form.primary_city.data)
            if form.secondary_address1.data:
                secondary_address = Address(name=form.first_name.data + " " + form.last_name.data,
                                            street_address=form.secondary_address1.data + " " + form.secondary_address2.data,
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
        member = Member(salutation=form.salutation.data,
                        primary_address_id=address.id,
                        secondary_address_id=secondary_address.id if secondary_address else None,
                        metro_area_id=metro.id,
                        first_name=form.first_name.data,
                        middle_initial=form.middle_initial.data,
                        last_name=form.last_name.data,
                        preferred_name=form.preferred_name.data,
                        gender=form.gender.data,
                        birthdate=form.birthday.data,
                        primary_phone_number=form.primary_phone.data,
                        secondary_phone_number=form.cell_number.data,
                        email_address=form.email.data,
                        preferred_contact_method=form.preferred_contact_method.data,
                        emergency_contact_name=form.emergency_contact_name.data,
                        emergency_contact_phone_number=form.emergency_contact_phone_number.data,
                        emergency_contact_email_address=form.emergency_contact_email_address.data,
                        emergency_contact_relation=form.emergency_contact_relationship.data,
                        membership_expiration_date=form.expiration_date.data,
                        member_number=form.member_number.data,
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
    service_categories = sorted([(category.name, category.request_type_id, category.id)
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
        category_dict[category[0]] = MultiCheckboxField(
            category[0], choices=choices)
    for key, value in category_dict.items():
        setattr(VolunteerManager, key, value)
    form = VolunteerManager()
    service_ids = []
    if form.validate_on_submit():
        for key, value in category_dict.items():
            service_input = getattr(form, key)
            service_data = service_input.data
            for service in service_data:
                service_to_be_committed = Service.query.filter_by(
                    name=service, category_id=int(category_name_to_id[key])).first()
                service_ids.append(service_to_be_committed.id)
        address = Address(name=form.first_name.data + " " + form.last_name.data,
                          street_address=form.primary_address1.data + " " + form.primary_address2.data,
                          city=form.primary_city.data)
        db.session.add(address)
        db.session.commit()
        volunteer = Volunteer(
            salutation=form.salutation.data,
            first_name=form.first_name.data,
            middle_initial=form.middle_initial.data,
            last_name=form.last_name.data,
            preferred_name=form.preferred_name.data,
            birthday=form.birthday.data,
            gender=form.gender.data,
            primary_address_id = address.id,
            primary_phone_number=form.home_phone.data,
            email_address=form.email.data,
            emergency_contact_name=form.emergency_contact_name.data,
            emergency_contact_phone_number=form.emergency_contact_phone_number.data,
            emergency_contact_email_address=form.emergency_contact_email_address.data,
            preferred_contact_method=form.contact_preference.data,
            type_id=2,  # What should we set volunteer type id as???
            general_notes=form.notes.data,
            rating=1,  # Why is this not null before the user even creates a volunteer?
            is_fully_vetted=True,
        )
        db.session.add(volunteer)
        db.session.commit()
        for service in service_ids:
            provided_service = ProvidedService(
                service_id=service, volunteer_id=volunteer.id)
            db.session.add(provided_service)
            db.session.commit()
        flash('Volunteer {} successfully invited'.format(
            form.first_name.data), 'form-success')
    return render_template('admin/people_manager/volunteer_manager.html',
                           form=form,
                           services=services,
                           service_categories=service_categories, category_dict=category_dict)


@admin.route('/invite-contractor', methods=['GET', 'POST'])
@login_required
@admin_required
def invite_contractor():
    """Page for contactor management."""
    form = ContractorManager()
    reviews = Reviews()
    if form.validate_on_submit():
        address = None
        if form.primary_address1.data:
            address = Address(name=form.first_name.data + " " + form.last_name.data,
                              street_address=form.primary_address1.data + " " + form.primary_address2.data,
                              city=form.primary_city.data)
            db.session.add(address)
            db.session.commit()
        localResource = LocalResource(contact_salutation=form.salutation.data,
                                      address_id=(
                                          address.id if address else None),
                                      contact_first_name=form.first_name.data,
                                      contact_middle_initial=form.middle_initial.data,
                                      contact_last_name=form.last_name.data,
                                      company_name=form.company_name.data,
                                      primary_phone_number=form.primary_phone_number.data,
                                      secondary_phone_number=form.secondary_phone_number.data,
                                      email_address=form.email.data,
                                      preferred_contact_method=form.preferred_contact_method.data)
        db.session.add(localResource)
        db.session.commit()
        flash('Contractor {} successfully invited'.format(
            form.last_name.data), 'form-success')
    return render_template('admin/people_manager/contractor_manager.html', form=form, reviews=reviews)


@admin.route('/services')
@login_required
@admin_required
def registered_services():
    """Manage services."""
    services = Service.query.all()
    return render_template('admin/system_manager/registered_services.html',
                           services=services)


@admin.route('/services/<int:service_id>', methods=['GET', 'POST'])
@admin.route('/services/<int:service_id>/info', methods=['GET', 'POST'])
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
        flash('Service {} successfully updated'.format(
            form.name.data), 'form-success')
        return redirect(url_for('admin.registered_services'))
    if service is None:
        abort(404)
    return render_template('admin/system_manager/manage_service.html', service=service, form=form)


@admin.route('/services/<int:service_id>/_delete')
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
        flash('Service {} successfully created'.format(service.name), 'success')
        return redirect(url_for('admin.registered_services'))

    return render_template('admin/system_manager/manage_service.html', form=form)


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


@admin.route('/metro-areas/<int:metro_area_id>', methods=['GET', 'POST'])
@admin.route('/metro-areas/<int:metro_area_id>/info', methods=['GET', 'POST'])
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
        flash('Metro Area {} successfully updated'.format(
            form.name.data), 'form-success')
        return redirect(url_for('admin.registered_metro_areas'))
    if metro_area is None:
        abort(404)
    return render_template('admin/system_manager/manage_metro_area.html', metro_area=metro_area, form=form)


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
        flash('Metro Area {} successfully created'.format(
            metro_area.name), 'success')
        return redirect(url_for('admin.registered_metro_areas'))

    return render_template('admin/system_manager/manage_metro_area.html', form=form)
