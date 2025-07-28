from django import forms
from .models import Task
from django.contrib.auth.models import User
from content.models import Document  # تأكدي من المسار الصحيح للموديل

class TaskForm(forms.ModelForm):
    file = forms.FileField(
        required=False,
        label="مرفق المهمة (اختياري)",
        help_text="مثل PDF أو صورة"
    )

    documents = forms.ModelMultipleChoiceField(
        queryset=Document.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="المستندات المرتبطة"
    )

    class Meta:
        model = Task
        fields = ['title', 'description', 'assigned_to', 'client', 'status', 'due_date', 'documents', 'file']
        labels = {
            'title': 'عنوان المهمة',
            'description': 'الوصف',
            'assigned_to': 'الموظف المكلّف',
            'client': 'العميل',
            'status': 'الحالة',
            'due_date': 'تاريخ الاستحقاق',
            'documents': 'المستندات المرتبطة',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_to'].queryset = User.objects.filter(userprofile__role__name='staff')
