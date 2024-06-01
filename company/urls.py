"""URLs patterns for company app"""
from django.urls import path

from . import views

app_name="company"
urlpatterns = [
    # Index page
    path("", views.index, name="index"),
    # Create a company page
    path("company/settings", views.company_settings, name="company_settings")
]