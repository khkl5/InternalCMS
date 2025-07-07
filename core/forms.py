from django import forms
from django.contrib.auth.models import User
from core.models import UserProfile, Role
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

class AddStaffForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    email = forms.EmailField()
    phone_number = forms.CharField(max_length=20, required=False)
    department = forms.CharField(max_length=100, required=False)
    full_name = forms.CharField(label="الاسم الكامل", max_length=150)

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
        # معالجة الاسم الكامل
        full_name = self.cleaned_data['full_name']
        first_name = full_name.split()[0]
        last_name = ' '.join(full_name.split()[1:]) if len(full_name.split()) > 1 else ''

        # إنشاء المستخدم
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password'],
            email=self.cleaned_data['email'],
            first_name=first_name,
            last_name=last_name,
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

User = get_user_model()

# ✅ هذا هو النموذج الصحيح لتعديل بيانات الموظف (مع الدور):
class StaffEditForm(forms.Form):
    first_name = forms.CharField(label="الاسم الأول", max_length=150)
    last_name = forms.CharField(label="اسم العائلة", max_length=150)
    username = forms.CharField(label="اسم المستخدم", max_length=150)
    email = forms.EmailField(label="البريد الإلكتروني")
    is_active = forms.BooleanField(label="نشط", required=False)
    phone_number = forms.CharField(label="رقم الجوال", max_length=20, required=False)
    department = forms.CharField(label="القسم", max_length=100, required=False)
    role = forms.ModelChoiceField(
        queryset=Role.objects.all(),
        label="الدور",
        widget=forms.Select(),
        required=True,
        empty_label=None
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user_instance', None)
        userprofile = kwargs.pop('profile_instance', None)
        super().__init__(*args, **kwargs)
        if user and userprofile:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['username'].initial = user.username
            self.fields['email'].initial = user.email
            self.fields['is_active'].initial = user.is_active
            self.fields['phone_number'].initial = userprofile.phone_number
            self.fields['department'].initial = userprofile.department
            self.fields['role'].initial = userprofile.role

    def save(self, user_instance, profile_instance):
        user_instance.first_name = self.cleaned_data['first_name']
        user_instance.last_name = self.cleaned_data['last_name']
        user_instance.username = self.cleaned_data['username']
        user_instance.email = self.cleaned_data['email']
        user_instance.is_active = self.cleaned_data['is_active']
        user_instance.save()

        profile_instance.phone_number = self.cleaned_data['phone_number']
        profile_instance.department = self.cleaned_data['department']
        profile_instance.role = self.cleaned_data['role']
        profile_instance.save()
