from django.contrib import admin
from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'message_type', 'resolved', 'created_at')
    list_filter = ('message_type', 'resolved')
    list_editable = ('resolved',)
    search_fields = ('name', 'email', 'message')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    show_facets = admin.ShowFacets.ALWAYS
