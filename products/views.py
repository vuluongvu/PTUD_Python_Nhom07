from django.shortcuts import get_object_or_404, render

from core.models import Product


# Create your views here.

def view_all_products(request):
    """View hiển thị trang chủ."""
    return render(request, 'products/view-all.html')

def search_results(request):
    """View hiển thị trang chủ."""
    return render(request, 'products/search-results.html')

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    context = {'product': product}
    return render(request, 'products/product-detail.html', context)