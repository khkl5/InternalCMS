from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone_number', 'department')
    list_display_links = ('user',)
    search_fields = ('user__username', 'phone_number', 'department')
    list_filter = ('role',)
    ordering = ('user__username',)
