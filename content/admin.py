from django.contrib import admin
from .models import Document

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_by', 'client', 'access_level', 'created_at')
    list_display_links = ('title',)
    search_fields = ('title', 'uploaded_by__username')
    list_filter = ('access_level', 'created_at', 'uploaded_by')
    ordering = ('-created_at',)
