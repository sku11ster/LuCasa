from django.contrib import admin
from .models import Property,PropertyImage

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'property_type', 'status', 'price', 'date_listed')
    search_fields = ('title', 'description', 'address', 'city', 'state', 'postal_code', 'country')
    list_filter = ('property_type', 'status', 'city', 'state', 'country')



@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    list_display = ('property', 'image')
    search_fields = ('property__title',)
    list_filter = ('property__property_type', 'property__city', 'property__state', 'property__country')

# @admin.register(PropertyVideo)
# class PropertyVideoAdmin(admin.ModelAdmin):
#     list_display = ('property', 'video')
#     search_fields = ('property__title',)
#     list_filter = ('property__property_type', 'property__city', 'property__state', 'property__country')