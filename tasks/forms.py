from django import forms
from .models import Task
from django.contrib.auth.models import User

class TaskForm(forms.ModelForm):
    file = forms.FileField(
        required=False,
        label="مرفق المهمة (اختياري)",
        help_text="مثل PDF أو صورة"
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
