from app.models import User, Service, ServiceCategory, MetroArea, Address
from app.models.user import Permission, Role
import unittest

from app import create_app, db


class SystemManagerTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = client
        db.create_all()
        Role.insert_roles()
        r = Role.query.filter_by(
            permissions=Permission.ADMINISTER).first()
        user1 = User(first_name="Admin", last_name="Test",
                     email='user@example.com',
                     password='password', role=r)
        token = user1.generate_confirmation_token()
        user1.confirm_account(token)
        db.session.add(user1)
        db.session.commit()
        self.user = user1
        self.client.post('account/login',
                         data=dict(email='user@example.com',
                                   password='password'),
                         follow_redirects=True)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_admin_dashboard_page_endpoint(self):
        resp = self.client.get('/admin/')
        assert resp.status_code == 200

    def test_new_user_endpoint(self):
        resp = self.client.get('/admin/new-user')
        assert resp.status_code == 200

    def test_users_endpoint(self):
        resp = self.client.get('/admin/users')
        assert resp.status_code == 200

    def test_specific_user_endpoint(self):
        resp = self.client.get('/admin/user/' + str(self.user.id))
        assert resp.status_code == 200

        resp_info = self.client.get(
            '/admin/user/' + str(self.user.id) + "/info")
        assert resp_info.status_code == 200

    def test_user_change_email_endpoint(self):
        resp = self.client.get(
            '/admin/user/' + str(self.user.id) + "/change-email")
        assert resp.status_code == 200

    def test_user_change_account_type_endpoint(self):
        user2 = User(first_name="SecondUser", last_name="Test",
                     email='user2@example.com',
                     password='password')
        db.session.add(user2)
        db.session.commit()
        resp = self.client.get(
            '/admin/user/' + str(user2.id) + "/change-account-type")
        assert resp.status_code == 200

    def test_user_delete_endpoint(self):
        resp = self.client.get(
            '/admin/user/' + str(self.user.id) + "/delete")
        assert resp.status_code == 200

    def test_user_delete_hidden_endpoint(self):
        user2 = User(first_name="SecondUser", last_name="Test",
                     email='user2@example.com',
                     password='password')
        db.session.add(user2)
        db.session.commit()
        resp = self.client.get(
            '/admin/user/' + str(self.user.id) + "/_delete")
        assert resp.status_code == 302

        resp = self.client.get(
            '/admin/user/' + str(user2.id) + "/_delete")
        assert resp.status_code == 302

    def test_services_endpoint(self):
        resp = self.client.get('/admin/services')
        assert resp.status_code == 200

    def test_services_info_endpoint(self):
        Service.insert_services()
        resp = self.client.get('/admin/services/info/1')
        assert resp.status_code == 200

    def test_new_service_endpoint(self):
        resp = self.client.get('/admin/new-service')
        assert resp.status_code == 200

    def test_registered_service_categories_endpoint(self):
        resp = self.client.get('/admin/service-categories')
        assert resp.status_code == 200

    def test_registered_service_categories_info_endpoint(self):
        Service.insert_services()
        ServiceCategory.insert_categories()
        resp = self.client.get('/admin/service-categories/info/1')
        assert resp.status_code == 200

    def test_new_service_category_endpoint(self):
        resp = self.client.get('/admin/new-service-category')
        assert resp.status_code == 200

    def test_metro_areas_endpoint(self):
        resp = self.client.get('/admin/metro-areas')
        assert resp.status_code == 200

    def test_metro_areas_info_endpoint(self):
        MetroArea.insert_metro_areas()
        resp = self.client.get('/admin/metro-areas/info/1')
        assert resp.status_code == 200

    def test_new_metro_area_endpoint(self):
        resp = self.client.get('/admin/new-metro-area')
        assert resp.status_code == 200

    def test_destination_addresses_endpoint(self):
        resp = self.client.get('/admin/destination-addresses')
        assert resp.status_code == 200

    def test_destination_addresses_info_endpoint(self):
        Address.generate_fake(count=10)
        resp = self.client.get('/admin/destination-addresses/info/1')
        assert resp.status_code == 200

    def test_new_destination_address_endpoint(self):
        resp = self.client.get('/admin/new-destination-address')
        assert resp.status_code == 200

    def test_destination_address_delete_hidden_endpoint(self):
        Address.generate_fake(count=10)
        resp = self.client.get('/admin/destination-addresses/1/_delete')
        assert resp.status_code == 302

    def test_generate_report_endpoint(self):
        resp = self.client.get('/admin/generate-report')
        assert resp.status_code == 200
