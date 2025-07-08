from django import forms
from django.contrib.auth.models import User
from .models import Document

class DocumentUploadForm(forms.ModelForm):
    file = forms.FileField(label='اختر الملف', required=True)

    allowed_users = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),  # سيتم تعيينها في __init__
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'checkbox-list'  # ✅ كلاس واضح نستخدمه في التنسيق بدون مشاكل
        }),
        label='الموظفون المسموح لهم (للمستند المقيّد فقط)'
    )

    class Meta:
        model = Document
        fields = ['title', 'client', 'access_level', 'allowed_users']
        labels = {
            'title': 'عنوان المستند',
            'client': 'العميل المرتبط',
            'access_level': 'مستوى الوصول',
            'allowed_users': 'الموظفون المسموح لهم',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['allowed_users'].queryset = User.objects.all()
        self.fields['client'].required = False
        self.fields['allowed_users'].label_from_instance = lambda obj: obj.get_full_name() or obj.username

    def clean(self):
        cleaned_data = super().clean()
        access_level = cleaned_data.get('access_level')
        client = cleaned_data.get('client')
        allowed_users = cleaned_data.get('allowed_users')

        if access_level == 'client_shared' and not client:
            self.add_error('client', 'الرجاء اختيار العميل المرتبط عند اختيار "مشاركة مع عميل".')

        if access_level == 'restricted' and (not allowed_users or allowed_users.count() == 0):
            self.add_error('allowed_users', 'الرجاء تحديد الموظفين المسموح لهم عند اختيار "مقيّد".')

        return cleaned_data
