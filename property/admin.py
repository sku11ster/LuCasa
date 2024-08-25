from django.contrib import admin
from .models import *

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

@admin.register(PropertyVideo)
class PropertyVideoAdmin(admin.ModelAdmin):
    list_display = ('property', 'video')
    search_fields = ('property__title',)
    list_filter = ('property__property_type', 'property__city', 'property__state', 'property__country')
@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'property','property_id', 'created_at','id')
    list_filter = ('user', 'property')
    search_fields = ('user__username', 'property__address')  # Adjust fields as needed


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('property', 'seller', 'buyer', 'date', 'amount')
    list_filter = ('date', 'property__property_type')
    search_fields = ('property__name', 'seller__username', 'buyer__username')
    date_hierarchy = 'date'
    ordering = ('-date',)

