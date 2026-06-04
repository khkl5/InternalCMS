from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from unittest.mock import patch

from content.forms import DocumentUploadForm
from content.models import Document
from core.models import Role, UserProfile
from tasks.models import Task
from utils.supabase_client import upload_file


class SecurityRegressionTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_role, _ = Role.objects.get_or_create(name="admin")
        self.staff_role, _ = Role.objects.get_or_create(name="staff")
        self.viewer_role, _ = Role.objects.get_or_create(name="viewer")

        self.admin = self.create_user("admin", self.admin_role)
        self.staff = self.create_user("staff", self.staff_role)
        self.other_staff = self.create_user("other", self.staff_role)
        self.viewer = self.create_user("viewer", self.viewer_role)
        self.task = Task.objects.create(title="Private task", assigned_to=self.staff)

    def create_user(self, username, role):
        user = User.objects.create_user(username=username, password="StrongPass!123")
        UserProfile.objects.create(user=user, role=role)
        return user

    def test_anonymous_user_cannot_edit_users(self):
        response = self.client.get(reverse("edit_staff", args=[self.staff.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_non_admin_cannot_edit_users(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse("edit_staff", args=[self.other_staff.pk]))
        self.assertEqual(response.status_code, 403)

    def test_unassigned_staff_cannot_view_task_detail(self):
        self.client.force_login(self.other_staff)
        response = self.client.get(reverse("task_detail", args=[self.task.pk]))
        self.assertEqual(response.status_code, 403)

    def test_assigned_staff_can_view_task_detail(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse("task_detail", args=[self.task.pk]))
        self.assertEqual(response.status_code, 200)

    def test_viewer_reports_do_not_query_missing_task_field(self):
        self.client.force_login(self.viewer)
        response = self.client.get(reverse("reports"))
        self.assertEqual(response.status_code, 200)

    def test_user_deletion_rejects_get(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse("delete_staff", args=[self.staff.pk]))
        self.assertEqual(response.status_code, 405)
        self.assertTrue(User.objects.filter(pk=self.staff.pk).exists())

    def test_test_email_endpoints_are_disabled(self):
        self.assertEqual(self.client.get("/send-test-email/").status_code, 404)
        self.assertEqual(self.client.get("/mailer/send-test-email/").status_code, 404)

    def test_restricted_document_api_only_allows_selected_users(self):
        document = Document.objects.create(
            title="Restricted",
            uploaded_by=self.admin,
            access_level="restricted",
        )
        document.allowed_users.add(self.staff)

        self.client.force_login(self.viewer)
        viewer_response = self.client.get("/content/documents-api/")
        self.assertEqual(viewer_response.status_code, 200)
        self.assertEqual(viewer_response.json(), [])

        self.client.force_login(self.staff)
        staff_response = self.client.get("/content/documents-api/")
        self.assertEqual(staff_response.status_code, 200)
        self.assertEqual([item["id"] for item in staff_response.json()], [document.pk])

    def test_upload_form_rejects_executable_files(self):
        upload = SimpleUploadedFile(
            "malware.exe",
            b"MZ",
            content_type="application/x-msdownload",
        )
        form = DocumentUploadForm(
            data={"title": "Bad file", "access_level": "private"},
            files={"file": upload},
        )
        self.assertFalse(form.is_valid())
        self.assertIn("file", form.errors)

    def test_upload_form_rejects_executable_renamed_as_pdf(self):
        upload = SimpleUploadedFile(
            "malware.pdf",
            b"MZ executable",
            content_type="application/pdf",
        )
        form = DocumentUploadForm(
            data={"title": "Bad PDF", "access_level": "private"},
            files={"file": upload},
        )
        self.assertFalse(form.is_valid())
        self.assertIn("file", form.errors)

    def test_login_rate_limit_blocks_repeated_failures(self):
        for _ in range(5):
            self.client.post(
                reverse("login"),
                {"username": self.staff.username, "password": "wrong"},
            )
        response = self.client.post(
            reverse("login"),
            {"username": self.staff.username, "password": "StrongPass!123"},
        )
        self.assertEqual(response.status_code, 429)

    @patch("utils.supabase_client.get_supabase_client")
    def test_supabase_upload_preserves_validated_content_type(self, get_client):
        upload = SimpleUploadedFile(
            "document.pdf",
            b"%PDF-1.7",
            content_type="application/pdf",
        )
        upload_file(upload, "uploads/document.pdf")
        options = (
            get_client.return_value.storage.from_.return_value.upload.call_args.kwargs[
                "file_options"
            ]
        )
        self.assertEqual(options["content-type"], "application/pdf")
        self.assertEqual(options["upsert"], "false")
