from django.contrib import admin
from .models import Client

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'assigned_to', 'created_at')
    list_display_links = ('name',)
    search_fields = ('name', 'email', 'phone', 'assigned_to__username')
    list_filter = ('assigned_to', 'created_at')
    ordering = ('-created_at',)
