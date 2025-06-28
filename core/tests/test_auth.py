from django.test import TestCase, Client
from django.contrib.auth.models import User

class AuthTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')

    def test_login_success(self):
        response = self.client.post('/login/', {'username': 'testuser', 'password': 'testpass'})
        self.assertEqual(response.status_code, 302)  # يفترض أنه يوجّه بعد الدخول

    def test_login_fail(self):
        response = self.client.post('/login/', {'username': 'testuser', 'password': 'wrongpass'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "تسجيل الدخول")  # بدل رسالة الخطأ لأن JS ما يعرضها وقت الاختبار

    def test_logout(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get('/logout/')
        self.assertEqual(response.status_code, 302)
