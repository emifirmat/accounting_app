from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    """Create new user"""
    class Meta:
        model = CustomUser
        fields = UserCreationForm.Meta.fields


class CustomUserChangeForm(UserChangeForm):
    """Modify user fields"""
    class Meta:
        model = CustomUser
        fields = UserChangeForm.Meta.fields