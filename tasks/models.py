from django.db import models
from django.contrib.auth.models import User
from clients.models import Client
from content.models import Document

class Task(models.Model):
    STATUS_CHOICES = [
        ('pending', 'قيد التنفيذ'),
        ('completed', 'منتهية'),
        ('overdue', 'متأخرة'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    due_date = models.DateField(null=True, blank=True)
    documents = models.ManyToManyField(Document, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'مهمة'
        verbose_name_plural = 'المهام'
