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
    path("<str:person_type>/new_multiple", views.person_new_multiple, 
        name="person_new_multiple"),
    # Edit existing client or supplier web page
    path("<str:person_type>/edit", views.person_edit, name="person_edit"),
    # Delete a client or supplier web page
    path("<str:person_type>/delete", views.person_delete, name="person_delete"),
    # Payment conditions
    path("payment_conditions", views.payment_conditions, name="payment_conditions"),
    # Point of sells
    path("points_of_sell", views.point_of_sell, name="points_of_sell"),
    # Document types
    path("document_types", views.doc_types, name="doc_types"),
    # Sales index webpage
    path("sales", views.sales_index, name="sales_index"),
    # Create new sale invoice webpage
    path("sales/invoices/new", views.sales_new, name="sales_new"),
    path("sales/invoices/new_massive", views.sales_new_massive, 
        name="sales_new_massive"),
    # Specific sale invoice webpage
    path("sales/invoices/<int:inv_pk>", views.sales_invoice, name="sales_invoice"),
    # Search invoices webpage
    path("sales/invoices/search", views.sales_search, name="sales_search"),
    # Edit an invoice webpage
    path("sales/invoices/<int:inv_pk>/edit", views.sales_edit, name="sales_edit"),
    # Show invoice list
    path("sales/invoices/list", views.sales_list, name="invoice_list"),
    # Receivables index webpage
    path("receivables", views.receivables_index, name="receivables_index"),
    # New Receipt webpage
    path("receivables/receipts/new", views.receivables_new, name="receivables_new"),
    path("receivables/receipts/new_massive", views.receivables_new_massive, 
        name="receivables_new_massive"),
    # Specific sale receipt webpage
    path("receivables/receipts/<int:rec_pk>", views.receivables_receipt, 
        name="receivables_receipt"),
    # Edit a receipt webpage
    path("receivables/receipts/<int:rec_pk>/edit", views.receivables_edit, name="receivables_edit"),
    # Search receipts webpage
    path("receivables/receipts/search", views.receivables_search, name="receivables_search"),
    # Show receipt list
    path("receivables/receipts/list", views.receivables_list, name="receipt_list"),


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
    # Sale invoices APIs
    path("api/sale_invoices", views_api.SaleInvoicesAPI.as_view(), 
        name="sale_invoices_api"),
    path("api/sale_invoices/<int:pk>", views_api.SaleInvoiceAPI.as_view(), 
        name="sale_invoice_api"),
    # Sale receipts APIs
    path("api/sale_receipts", views_api.SaleReceiptsAPI.as_view(), 
        name="sale_receipts_api"),
    path("api/sale_receipts/<int:pk>", views_api.SaleReceiptAPI.as_view(), 
        name="sale_receipt_api"),
]
