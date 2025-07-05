from django.db import models
from django.contrib.auth.models import User
from .role import Role  # استيراد الدور الجديد
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)
    phone_number = models.CharField(max_length=20, blank=True)
    department = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f'{self.user.username} ({self.role})'

    class Meta:
        verbose_name = 'ملف المستخدم'
        verbose_name_plural = 'ملفات المستخدمين'


@login_required
def profile_view(request):
    profile = UserProfile.objects.select_related('role').get(user=request.user)
    return render(request, 'core/profile.html', {
        'role': profile.role.name if profile.role else 'غير محدد',
        'phone': profile.phone_number,
        'department': profile.department,
    })
