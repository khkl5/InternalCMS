from django.test import TestCase, Client
from django.contrib.auth.models import User
from core.models import UserProfile
from core.role import Role  # عدلي هذا إذا role داخل models.py

class DashboardPermissionTests(TestCase):
    def setUp(self):
        self.client = Client()

        self.role_admin = Role.objects.create(name='admin')
        self.role_staff = Role.objects.create(name='staff')
        self.role_viewer = Role.objects.create(name='viewer')

        self.admin_user = User.objects.create_user(username='admin', password='adminpass')
        self.staff_user = User.objects.create_user(username='staff', password='staffpass')
        self.viewer_user = User.objects.create_user(username='viewer', password='viewerpass')

        UserProfile.objects.create(user=self.admin_user, role=self.role_admin)
        UserProfile.objects.create(user=self.staff_user, role=self.role_staff)
        UserProfile.objects.create(user=self.viewer_user, role=self.role_viewer)

    def test_admin_can_access_dashboard(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.get('/')  # بدل /dashboard/
        self.assertEqual(response.status_code, 200)

    def test_staff_can_access_dashboard(self):
        self.client.login(username='staff', password='staffpass')
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_viewer_can_access_dashboard_with_limited_view(self):
        self.client.login(username='viewer', password='viewerpass')
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_anonymous_user_redirected_to_login(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.url)
