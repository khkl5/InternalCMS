from django import forms
from .models import Document

class DocumentUploadForm(forms.ModelForm):
    file = forms.FileField(label='اختر الملف', required=True)

    class Meta:
        model = Document
        fields = ['title', 'client', 'access_level']
        labels = {
            'title': 'عنوان المستند',
            'client': 'العميل المرتبط',
            'access_level': 'مستوى الوصول',
        }
