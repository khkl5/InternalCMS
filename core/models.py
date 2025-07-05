from django.db import models
from django.contrib.auth.models import User
from .role import Role  # استيراد الدور الجديد
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django import forms
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)
    phone_number = models.CharField(max_length=20, blank=True)
    department = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f'{self.user.username} ({self.role})'

    class Meta:
        verbose_name = 'ملف المستخدم'
        verbose_name_plural = 'ملفات المستخدمين'


# core/forms.py

class StaffUserForm(forms.ModelForm):
    full_name = forms.CharField(label="الاسم الكامل", max_length=150)

    class Meta:
        model = User
        fields = ['username', 'email']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['role', 'phone_number', 'department']
