from django.db import models
from django.contrib.auth.models import User
from clients.models import Client

class Task(models.Model):
    STATUS_CHOICES = [
        ('pending', 'قيد التنفيذ'),
        ('completed', 'منتهية'),
        ('overdue', 'متأخرة'),
    ]

    title = models.CharField(max_length=255, verbose_name='عنوان المهمة')
    description = models.TextField(blank=True, verbose_name='الوصف')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='الموظف المكلّف')
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='العميل')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='الحالة')
    due_date = models.DateField(null=True, blank=True, verbose_name='تاريخ الاستحقاق')

    file_url = models.URLField(max_length=1024, blank=True, null=True, verbose_name='رابط الملف')
    file_path = models.CharField(max_length=512, blank=True, null=True, verbose_name='مسار الملف')
    
    # ❗ كتابة المسار كنص لحل مشكلة الاستيراد الدائري + تدقيق الأدوات
    documents = models.ManyToManyField('content.Document', blank=True, verbose_name='مستندات إضافية')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'مهمة'
        verbose_name_plural = 'المهام'
        ordering = ['-created_at']  # ترتيب المهام الأحدث أولاً
