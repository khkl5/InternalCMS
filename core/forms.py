from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction

from core.models import Role, UserProfile

User = get_user_model()


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
        empty_label=None,
    )

    def __init__(self, *args, **kwargs):
        self.user_instance = kwargs.pop("user_instance")
        self.profile_instance = kwargs.pop("profile_instance")
        super().__init__(*args, **kwargs)

        user = self.user_instance
        profile = self.profile_instance
        self.fields["first_name"].initial = user.first_name
        self.fields["last_name"].initial = user.last_name
        self.fields["username"].initial = user.username
        self.fields["email"].initial = user.email
        self.fields["is_active"].initial = user.is_active
        self.fields["phone_number"].initial = profile.phone_number
        self.fields["department"].initial = profile.department
        self.fields["role"].initial = profile.role

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.exclude(pk=self.user_instance.pk).filter(username=username).exists():
            raise ValidationError("اسم المستخدم موجود بالفعل.")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.exclude(pk=self.user_instance.pk).filter(email__iexact=email).exists():
            raise ValidationError("البريد الإلكتروني مستخدم بالفعل.")
        return email

    @transaction.atomic
    def save(self):
        user = self.user_instance
        profile = self.profile_instance

        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.username = self.cleaned_data["username"]
        user.email = self.cleaned_data["email"]
        user.is_active = self.cleaned_data["is_active"]
        user.save()

        profile.phone_number = self.cleaned_data["phone_number"]
        profile.department = self.cleaned_data["department"]
        profile.role = self.cleaned_data["role"]
        profile.save()
        return profile


class AddUserForm(forms.Form):
    full_name = forms.CharField(label="الاسم الكامل", max_length=150)
    username = forms.CharField(label="اسم المستخدم", max_length=150)
    email = forms.EmailField(label="البريد الإلكتروني")
    password = forms.CharField(label="كلمة المرور", widget=forms.PasswordInput)
    phone_number = forms.CharField(label="رقم الجوال", max_length=20, required=False)
    department = forms.CharField(label="القسم", max_length=100, required=False)
    role = forms.ModelChoiceField(
        queryset=Role.objects.all(),
        label="الدور",
        widget=forms.Select(),
        required=True,
    )

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exists():
            raise ValidationError("اسم المستخدم موجود بالفعل.")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("البريد الإلكتروني مستخدم بالفعل.")
        return email

    def clean_password(self):
        password = self.cleaned_data["password"]
        candidate = User(
            username=self.cleaned_data.get("username", ""),
            email=self.cleaned_data.get("email", ""),
        )
        validate_password(password, user=candidate)
        return password

    @transaction.atomic
    def save(self):
        name_parts = self.cleaned_data["full_name"].split(maxsplit=1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ""

        user = User.objects.create_user(
            username=self.cleaned_data["username"],
            password=self.cleaned_data["password"],
            email=self.cleaned_data["email"],
            first_name=first_name,
            last_name=last_name,
        )
        return UserProfile.objects.create(
            user=user,
            phone_number=self.cleaned_data["phone_number"],
            department=self.cleaned_data["department"],
            role=self.cleaned_data["role"],
        )
