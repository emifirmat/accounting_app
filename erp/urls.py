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
    # Sales index webpage
    path("sales", views.sales_index, name="sales_index"),
    # Create new sale invoice webpage
    path("sales/new_invoice", views.sales_new, name="sales_new"),
    # Payment conditions
    path("payment_conditions", views.payment_conditions, name="payment_conditions"),
    # Point of sells
    path("points_of_sell", views.point_of_sell, name="points_of_sell"),
    # Document types
    path("document_types", views.doc_types, name="doc_types"),

    # Clients APIs
    path("api/clients", views_api.CompanyClientAPI.as_view(), name="clients_api"),
    path("api/clients/<int:pk>", views_api.DetailCompanyClientAPI.as_view(), 
        name="client_api"),
    # Suppliers APIS
    path("api/suppliers", views_api.SupplierAPI.as_view(), name="suppliers_api"),
    path("api/suppliers/<int:pk>", views_api.DetailSupplierAPI.as_view(), 
        name="supplier_api"),
    # Payment_conditions APIS
    path("api/payment_conditions/methods", views_api.PaymentMethodAPI.as_view(),
        name="payment_methods_api"), 
    path("api/payment_conditions/methods/<int:pk>", views_api.DetailPaymentMethodAPI.as_view(),
        name="payment_method_api"), 
    path("api/payment_conditions/terms", views_api.PaymentTermAPI.as_view(),
        name="payment_terms_api"),
    path("api/payment_conditions/terms/<int:pk>", views_api.DetailPaymentTermAPI.as_view(),
        name="payment_term_api"),
    # POS APIS
    path("api/points_of_sell", views_api.PointOfSellAPI.as_view(), 
        name="pos_api"),
    path("api/points_of_sell/<int:pk>", views_api.DetailPointOfSellAPI.as_view(), 
        name="detail_pos_api"),
    # Doc Types APIS
    path("api/document_types", views_api.DocTypesAPI.as_view(), 
        name="doc_types_api"),
    path("api/document_types/<int:pk>", views_api.DocTypeAPI.as_view(), 
        name="doc_type_api"),
]
