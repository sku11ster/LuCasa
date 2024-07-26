from django.contrib import admin
from .models import Property

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'property_type', 'status', 'price', 'date_listed')
    search_fields = ('title', 'description', 'address', 'city', 'state', 'postal_code', 'country')
    list_filter = ('property_type', 'status', 'city', 'state', 'country')