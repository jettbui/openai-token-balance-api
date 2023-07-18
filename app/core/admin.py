"""
Django admin customization.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from core import models
from django.utils.translation import gettext_lazy as _


class UserAdmin(BaseUserAdmin):
    """Define the admin pages for Users."""
    ordering = ['id']
    list_display = ['id', 'email', 'name']

    # Editing
    fieldsets = [
        (None, {'fields': ('id', 'email', 'name', 'password')}),
        (_('Permissions'), {
         'fields': ('is_active', 'is_staff', 'is_superuser')}),
        (_('Important dates'), {'fields': ('last_login',)}),
    ]
    readonly_fields = ['id', 'last_login']

    # Adding
    add_fieldsets = [
        (None, {
            'classes': ('wide',),
            'fields': ('email',
                       'password1',
                       'password2',
                       'name',
                       'is_active',
                       'is_staff',
                       'is_superuser')
        }),
    ]


class BalanceAdmin(admin.ModelAdmin):
    """Define the admin pages for Balances."""
    ordering = ['id']
    list_display = ['user', 'balance']

    # Editing
    fieldsets = [
        (None, {'fields': ('user', 'balance')}),
    ]
    readonly_fields = ['user']

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# Register models here.
admin.site.register(models.User, UserAdmin)
admin.site.register(models.Balance, BalanceAdmin)
