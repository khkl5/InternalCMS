from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'assigned_to', 'client', 'status', 'due_date', 'created_at')
    list_display_links = ('title',)
    search_fields = ('title', 'description', 'assigned_to__username')
    list_filter = ('status', 'due_date', 'assigned_to')
    ordering = ('-due_date',)
