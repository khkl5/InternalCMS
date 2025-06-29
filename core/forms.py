from django import forms
from django.contrib.auth.models import User
from core.models import UserProfile
from core.role import Role
from django.core.exceptions import ValidationError

class AddStaffForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    email = forms.EmailField()
    phone_number = forms.CharField(max_length=20, required=False)
    department = forms.CharField(max_length=100, required=False)

    class Meta:
        model = UserProfile
        fields = ['phone_number', 'department']

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise ValidationError("اسم المستخدم موجود بالفعل.")
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError("البريد الإلكتروني مستخدم بالفعل.")
        return email

    def save(self, commit=True):
        # إنشاء المستخدم
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password'],
            email=self.cleaned_data['email'],
        )

        # تحديد الدور
        try:
            role = Role.objects.get(name='staff')
        except Role.DoesNotExist:
            raise ValidationError("الدور 'staff' غير موجود. تأكدي من وجوده في قاعدة البيانات.")

        # إنشاء ملف المستخدم
        user_profile = super().save(commit=False)
        user_profile.user = user
        user_profile.role = role

        if commit:
            user_profile.save()
        return user_profile
