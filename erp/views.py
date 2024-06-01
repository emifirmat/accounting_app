from django.shortcuts import render

# Create your views here.
def clients_index(request):
    """Company's home page"""
    return render(request, "erp/clients_index.html")