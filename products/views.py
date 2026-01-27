from django.shortcuts import get_object_or_404, render
from django.core.paginator import Paginator

from core.models import Product


# Create your views here.

def view_all_products(request):
    """View hiển thị tất cả sản phẩm có phân trang."""
    # 1. Lấy tất cả sản phẩm đang active, sắp xếp mới nhất
    products_list = Product.objects.filter(status=True).order_by('-created_at')
    
    # 2. Cấu hình phân trang (12 sản phẩm/trang)
    paginator = Paginator(products_list, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # 3. Truyền dữ liệu vào template
    context = {
        'products': page_obj,  # Biến này để vòng lặp {% for p in products %} chạy
        'page_obj': page_obj,  # Biến này để hiển thị thanh phân trang
    }
    return render(request, 'products/view-all.html', context)

def search_results(request):
    """View hiển thị trang chủ."""
    return render(request, 'products/search-results.html')

def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.select_related('laptop_config', 'accessory_config', 'brand', 'category', 'inventory')
                       .prefetch_related('images', 'reviews'), 
        slug=slug
    )
    related_products = Product.objects.filter(category=product.category).exclude(slug=slug).order_by('?')[:4] 
    context = {'p': product}
    return render(request, 'products/product-detail.html', context)