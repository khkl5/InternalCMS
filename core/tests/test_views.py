from django.test import TestCase, Client
from django.contrib.auth.models import User
from core.models import UserProfile
from core.role import Role  # أو import من models حسب مكانه

class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()

        self.role_admin = Role.objects.create(name='admin')
        self.admin = User.objects.create_user(username='admin', password='adminpass')
        UserProfile.objects.create(user=self.admin, role=self.role_admin)

    def test_settings_view_for_admin(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.get('/settings/')  # ← تأكدي أن هذا المسار موجود
        self.assertEqual(response.status_code, 200)

    def test_users_list_view_for_admin(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.get('/users/')  # ← تأكدي أن هذا المسار موجود
        self.assertEqual(response.status_code, 200)
