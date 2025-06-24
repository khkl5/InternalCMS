from django.db import models
from django.contrib.auth.models import User
from clients.models import Client

class Document(models.Model):
    ACCESS_CHOICES = [
        ('public', 'عام'),
        ('private', 'خاص'),
        ('restricted', 'مقيّد'),
    ]

    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True)
    access_level = models.CharField(max_length=20, choices=ACCESS_CHOICES, default='private')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'مستند'
        verbose_name_plural = 'المستندات'
