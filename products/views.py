from django.shortcuts import get_object_or_404, render
from django.core.paginator import Paginator
from django.db.models import Q, Avg, Count
from django.http import JsonResponse
from core.models import Cart, Product, Review


# Create your views here.
def view_all_products(request):
   
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

    # Phân trang: 12 sản phẩm/trang
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

    #  Xử lý Avatar người dùng 
    avatar_url = None
    if request.user.is_authenticated:
        user_profile = getattr(request.user, 'profile', None)        
        if user_profile and user_profile.avatar:
            try:
                avatar_url = user_profile.avatar.url
            except:
                avatar_url = str(user_profile.avatar)

    # XỬ LÝ POST (Bình luận AJAX)
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({'status': 'error', 'message': 'Bạn cần đăng nhập!'}, status=403)

        rating = request.POST.get('rating')
        content = request.POST.get('content')

        if not rating or not content:
            return JsonResponse({'status': 'error', 'message': 'Vui lòng nhập đủ thông tin!'}, status=400)

        try:
            # Lưu Review 
            new_review = Review.objects.create(
                product=product,
                user=request.user,
                rating=int(rating),
                comment=content 
            )

            return JsonResponse({
                'status': 'success',
                'username': request.user.username,
                'full_name': getattr(request.user.profile, 'full_name', request.user.username),
                'avatar': avatar_url,
                'rating': new_review.rating,
                'comment': new_review.comment,
                'created_at': 'Vừa xong'
            })
        except Exception as e:
           
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    # XỬ LÝ GET 
    # Khai báo giá trị mặc định để tránh  UnboundLocalError
    related_products = Product.objects.none() 
    
    sort_by = request.GET.get('sort', 'id')
    related_query = Product.objects.filter(category=product.category).exclude(slug=slug)

    if sort_by == 'price_asc':
        related_products = related_query.order_by('price')
    elif sort_by == 'price_desc':
        related_products = related_query.order_by('-price')
    else:
        related_products = related_query.order_by('?')[:4]

    context = {
        'p': product,
        'related_products': related_products,
        'avg_rating': round(product.avg_rating or 0, 1),
        'review_count': product.review_count,
        'profile': related_products,
        'avatar': avatar_url,
        'reviews': [
            {
                'avatar': (getattr(getattr(r.user, 'profile', None), 'avatar', None)) or None,
                'username': r.user.username,
                'full_name': (getattr(getattr(r.user, 'profile', None), 'full_name', None)) or r.user.username,
                'created_at': r.created_at,
                'rating': r.rating,
                'comment': r.comment,
            }
            for r in product.reviews.all()
        ],
        'products_by_price': related_products,
    }
    return render(request, 'products/product-detail.html', context)

def toggle_cart(request):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'login_required', 'message': 'Bạn phải đăng nhập!'}, status=200)

    if request.method == "POST":
        product_id = request.POST.get('id')
        product = get_object_or_404(Product, id=product_id)

        # Lấy hoặc tạo giỏ hàng cho user
        user_cart, created = Cart.objects.get_or_create(user=request.user)

        # Kiểm tra sản phẩm đã có trong CartItem chưa
        cart_item, item_created = user_cart.items.get_or_create(
            product=product
        )

        if not item_created:
            # Nếu item đã tồn tại (không phải vừa được tạo), thì xóa nó đi
            cart_item.delete()
            return JsonResponse({'status': 'removed', 'message': 'Đã xóa khỏi giỏ!'})
        else:
            # Nếu item vừa được tạo, nghĩa là đã thêm thành công
            return JsonResponse({'status': 'added', 'message': 'Đã thêm vào giỏ!'})

    return JsonResponse({'status': 'error', 'message': 'Chỉ chấp nhận POST'}, status=400)