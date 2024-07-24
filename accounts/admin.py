from django.contrib import admin

from django.contrib import admin
from .models import CustomUser 

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'bio', 'address')
    search_fields = ['email', 'username']