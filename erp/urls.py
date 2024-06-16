"""URL patterns for ERP app"""
from django.urls import path

from . import views, views_api

app_name = "erp"
urlpatterns = [
    # Client index page
    path("client", views.client_index, name="client_index"),
    # New client page
    path("client/new", views.client_new, name="client_new"),
    # Edit client page
    path("client/edit", views.client_edit, name="client_edit"),
    # Delete client page
    path("client/delete", views.client_delete, name="client_delete"),
    # Clients APIs
    path("api/clients", views_api.CompanyClientAPI.as_view(), name="clients_api"),
    path("api/clients/<int:pk>", views_api.DetailCompanyClientAPI.as_view(), 
        name="client_api"),
]
