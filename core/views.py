from django.shortcuts import render
from .models import Product

def home(request):
    """View hiển thị trang chủ."""
    products = Product.objects.all()
    context = {'products': products}
    
    return render(request, 'core/home.html', context)

