from django.contrib import admin
from .models import UserProfile
from .role import Role  # استيراد نموذج الدور

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_role_name', 'phone_number', 'department')
    list_display_links = ('user',)
    search_fields = ('user__username', 'phone_number', 'department')
    list_filter = ('role__name',)
    ordering = ('user__username',)

    def get_role_name(self, obj):
        return obj.role.name if obj.role else '-'
    get_role_name.short_description = 'الدور'

# تسجيل جدول الأدوار
@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
