"""URLs patterns for company app"""
from django.urls import path

from . import views, views_api

app_name="company"
urlpatterns = [
    # Index page
    path("", views.index, name="index"),
    # Create a company page
    path("company/settings", views.company_settings, name="settings"),
    # Company's Financial year
    path("company/year", views.company_year, name="year"),
    # Financial years API
    path("api/company/years", views_api.CompanyYearAPI.as_view(), name="years_api"),
    # Especific f. year API
    path("api/company/years/<int:pk>", views_api.DetailCompanyYearAPI.as_view(),
        name="year_api"),
]