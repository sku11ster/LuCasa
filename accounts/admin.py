from django.contrib import admin

from django.contrib import admin
from .models import CustomUser,PasswordResetToken

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'bio', 'address')
    search_fields = ['email', 'username']

@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ('user','token','created_at')
    search_fields = ('user__email', 'token')
    readonly_fields = ('token', 'created_at')

