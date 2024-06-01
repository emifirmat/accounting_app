from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from accounts.forms import CustomUserChangeForm, CustomUserCreationForm
from accounts.models import CustomUser


# Register your models here.
class CustomUserAdmin(UserAdmin):
    """Show custom user in admin page"""
    add_form = CustomUserChangeForm
    form = CustomUserCreationForm
    model = CustomUser
    list_display = ["username", "email", "is_staff"]
    fieldsets = UserAdmin.fieldsets
    add_fieldsets = UserAdmin.add_fieldsets


admin.site.register(CustomUser, CustomUserAdmin)
