from django.shortcuts import render
from . models import Product, ProductImage

def home(request):
    """View hiển thị trang chủ."""
    return render(request, 'core/home.html')

def home_product_view(request):
    pass