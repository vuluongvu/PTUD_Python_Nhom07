from django.shortcuts import render

# Create your views here.

def product_detail(request):
    """View hiển thị trang chủ."""
    return render(request, 'products/product-detail.html')

def view_all_products(request):
    """View hiển thị trang chủ."""
    return render(request, 'products/view-all.html')

def search_results(request):
    """View hiển thị trang chủ."""
    return render(request, 'products/search-results.html')