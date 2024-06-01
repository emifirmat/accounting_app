"""URL patterns for ERP app"""
from django.urls import path

from . import views

app_name = "erp"
urlpatterns = [
    # Company index page
    path("clients/", views.clients_index, name="clients_index"),
]
