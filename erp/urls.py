"""URL patterns for ERP app"""
from django.urls import path

from . import views, views_api

app_name = "erp"
urlpatterns = [
    # Client index webpage
    path("client", views.client_index, name="client_index"),
    # Suppliers webpage
    path("supplier", views.supplier_index, name="supplier_index"),
    # Add a new client or supplier web page
    path("<str:person_type>/new", views.person_new, name="person_new"),
    # Edit existing client or supplier web page
    path("<str:person_type>/edit", views.person_edit, name="person_edit"),
    # Delete a client or supplier web page
    path("<str:person_type>/delete", views.person_delete, name="person_delete"),
    # Clients APIs
    path("api/clients", views_api.CompanyClientAPI.as_view(), name="clients_api"),
    path("api/clients/<int:pk>", views_api.DetailCompanyClientAPI.as_view(), 
        name="client_api"),
    # Suppliers APIS
    path("api/suppliers", views_api.SupplierAPI.as_view(), name="suppliers_api"),
    path("api/suppliers/<int:pk>", views_api.DetailSupplierAPI.as_view(), 
        name="supplier_api"),
]
