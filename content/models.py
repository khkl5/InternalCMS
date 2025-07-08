# content/models.py
from django.db import models
from django.contrib.auth.models import User
from clients.models import Client

class Document(models.Model):
    ACCESS_CHOICES = [
        ('public', 'عام'),
        ('private', 'خاص'),
        ('restricted', 'مقيّد'),
        ('admin_only', 'للمدراء فقط'),
        ('client_shared', 'مشترك مع عميل'),
    ]

    title = models.CharField(max_length=255)
    file_url = models.URLField(max_length=1024, blank=True, null=True)
    file_path = models.CharField(max_length=512, blank=True, null=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True)
    access_level = models.CharField(max_length=20, choices=ACCESS_CHOICES, default='private')
    allowed_users = models.ManyToManyField(User, blank=True, related_name='permitted_documents')  # خاص بالمقيد
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def can_view(self, user):
        # صلاحيات العرض
        role = getattr(user.userprofile.role, 'name', None)
        if role == 'admin':
            return True
        if self.access_level == 'public':
            return True
        if self.access_level == 'private':
            return self.uploaded_by == user
        if self.access_level == 'restricted':
            return self.allowed_users.filter(id=user.id).exists() or self.uploaded_by == user
        if self.access_level == 'admin_only':
            return role == 'admin'
        if self.access_level == 'client_shared':
            # يشاهدها الموظف المسؤول أو العميل المرتبط فقط
            if self.client:
                return self.client.assigned_to == user or self.uploaded_by == user
        return False

    def can_edit(self, user):
        # فقط المالك أو المدير أو المستخدمين المسموح لهم بالتعديل (حسب نوع الصلاحية)
        role = getattr(user.userprofile.role, 'name', None)
        if role == 'admin':
            return True
        if self.access_level == 'private':
            return self.uploaded_by == user
        if self.access_level == 'restricted':
            return self.allowed_users.filter(id=user.id).exists()
        if self.access_level == 'client_shared' and self.client:
            return self.client.assigned_to == user or self.uploaded_by == user
        return False

    def can_delete(self, user):
        # المدير فقط أو مالك الملف في بعض الحالات
        role = getattr(user.userprofile.role, 'name', None)
        if role == 'admin':
            return True
        if self.access_level in ['private', 'restricted', 'client_shared']:
            return self.uploaded_by == user
        return False
