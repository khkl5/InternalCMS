from django.test import TestCase, override_settings
from django.urls import reverse


class HealthCheckTests(TestCase):
    @override_settings(SECURE_SSL_REDIRECT=True)
    def test_health_check_is_public(self):
        response = self.client.get(reverse("health_check"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})
