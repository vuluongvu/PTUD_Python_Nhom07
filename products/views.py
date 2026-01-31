from django.shortcuts import get_object_or_404, render
from django.core.paginator import Paginator
from django.db.models import Q, Avg, Count

from core.models import Product


# Create your views here.

def view_all_products(request):
    """View hiển thị tất cả sản phẩm có phân trang."""
    products_list = Product.objects.filter(status=True).order_by('-created_at')
    
    paginator = Paginator(products_list, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'products': page_obj,  
        'page_obj': page_obj,  
    }
    return render(request, 'products/view-all.html', context)

def search_results(request):
    query = request.GET.get('q', '')
    if query:
        products_list = Product.objects.filter(
            Q(name__icontains=query),
            status=True
        ).select_related('laptop_config').prefetch_related('images').order_by('-created_at')
    else:
        products_list = Product.objects.none()

    # Phân trag: 12 sản phẩm/trang
    paginator = Paginator(products_list, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'products': page_obj,
        'page_obj': page_obj,
        'query': query,
    }
    return render(request, 'products/search-results.html', context)

def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.select_related('laptop_config', 'accessory_config', 'brand', 'category', 'inventory')
                       .prefetch_related('images', 'reviews', 'reviews__user__profile')
                       .annotate(avg_rating=Avg('reviews__rating'), review_count=Count('reviews')), 
        slug=slug
    )
    related_products = Product.objects.filter(category=product.category).exclude(slug=slug).order_by('?')[:4] 
    
    context = {
        'p': product,
        'related_products': related_products,
        'avg_rating': round(product.avg_rating or 0, 1),
        'review_count': product.review_count,
        'profile': related_products,
    }
    return render(request, 'products/product-detail.html', context)
