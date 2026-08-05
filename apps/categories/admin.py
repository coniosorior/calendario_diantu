from django.contrib import admin
from .models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'color', 'icon', 'is_default')
    list_filter = ('is_default',)
    search_fields = ('name', 'owner__username')
    ordering = ('owner', 'name')
    show_facets = admin.ShowFacets.ALWAYS
