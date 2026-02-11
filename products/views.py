from django.shortcuts import get_object_or_404, render
from django.core.paginator import Paginator
from django.db.models import Q, Avg, Count
from django.http import JsonResponse
from core.models import Brand, Cart, Category, Product, Review, WishList


# Create your views here.
def view_all_products(request):
   
    products_list = Product.objects.filter(status=True)
    
    # --- Logic Lọc Sản Phẩm ---
    selected_brands = request.GET.getlist('brand')
    selected_categories = request.GET.getlist('category')
    price_range = request.GET.get('price')

    if selected_brands:
        products_list = products_list.filter(brand__id__in=selected_brands)
    
    if selected_categories:
        products_list = products_list.filter(category__id__in=selected_categories)

    if price_range:
        try:
            min_price, max_price = price_range.split('-')
            if max_price == 'inf': # Trường hợp "Trên X triệu"
                products_list = products_list.filter(price__gte=int(min_price) * 1000000)
            else:
                products_list = products_list.filter(price__range=(int(min_price) * 1000000, int(max_price) * 1000000))
        except ValueError:
            pass # Bỏ qua nếu tham số giá không hợp lệ

    # Lấy tham số sort từ URL
    sort_by = request.GET.get('sort', 'default')
    if sort_by == 'price_asc':
        products_list = products_list.order_by('price')
    elif sort_by == 'price_desc':
        products_list = products_list.order_by('-price')
    else: # Mặc định
        products_list = products_list.order_by('-created_at')
    
    paginator = Paginator(products_list, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    wishlist_ids = []
    if request.user.is_authenticated:
        wishlist_ids = WishList.objects.filter(user=request.user).values_list('product_id', flat=True)

    # Lấy danh sách các thương hiệu và danh mục để hiển thị trong sidebar
    all_brands = Brand.objects.annotate(product_count=Count('products')).filter(product_count__gt=0)
    all_categories = Category.objects.annotate(product_count=Count('products')).filter(product_count__gt=0)

    price_ranges = [
        {'value': '0-10', 'label': 'Dưới 10 triệu'},
        {'value': '10-15', 'label': '10 - 15 triệu'},
        {'value': '15-20', 'label': '15 - 20 triệu'},
        {'value': '20-30', 'label': '20 - 30 triệu'},
        {'value': '30-inf', 'label': 'Trên 30 triệu'},
    ]

    context = {
        'products': page_obj,  
        'page_obj': page_obj,  
        'wishlist_ids': wishlist_ids,
        'sort_param': sort_by, # Truyền tham số sort sang template
        'all_brands': all_brands,
        'all_categories': all_categories,
        'selected_brands': selected_brands,
        'selected_categories': selected_categories,
        'selected_price': price_range,
        'price_ranges': price_ranges,
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

    # Thêm logic sắp xếp
    sort_by = request.GET.get('sort', 'default')
    if sort_by == 'price_asc':
        products_list = products_list.order_by('price')
    elif sort_by == 'price_desc':
        products_list = products_list.order_by('-price')
    # Mặc định đã order by '-created_at' ở trên

    # Phân trang: 12 sản phẩm/trang
    paginator = Paginator(products_list, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    wishlist_ids = []
    if request.user.is_authenticated:
        wishlist_ids = WishList.objects.filter(user=request.user).values_list('product_id', flat=True)

    context = {
        'products': page_obj,
        'page_obj': page_obj,
        'query': query,
        'wishlist_ids': wishlist_ids,
        'sort_param': sort_by,
    }
    return render(request, 'products/search-results.html', context)

def product_detail(request, slug):
    
    product = get_object_or_404(
        Product.objects.select_related('laptop_config', 'accessory_config', 'brand', 'category', 'inventory')
                       .prefetch_related('images', 'reviews', 'reviews__user__profile')
                       .annotate(avg_rating=Avg('reviews__rating'), review_count=Count('reviews')), 
        slug=slug
    )
    
    is_in_cart = False
    if request.user.is_authenticated:
        user_cart, created = Cart.objects.get_or_create(user=request.user)
        is_in_cart = user_cart.items.filter(product=product).exists()

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
        'is_in_cart': is_in_cart,
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
        action = request.POST.get('action', 'toggle') # Mặc định là 'toggle'
        product = get_object_or_404(Product, id=product_id)

        # Lấy hoặc tạo giỏ hàng cho user
        user_cart, created = Cart.objects.get_or_create(user=request.user)

        # Kiểm tra sản phẩm đã có trong CartItem chưa
        cart_item, item_created = user_cart.items.get_or_create( # Dùng get_or_create để đảm bảo sản phẩm được thêm nếu chưa có
            product=product
        )

        if action == 'add_only':
            # Nếu là hành động "Mua ngay", chỉ đảm bảo sản phẩm có trong giỏ và không làm gì khác
            return JsonResponse({'status': 'added', 'message': 'Sản phẩm đã sẵn sàng trong giỏ.'})

        # Logic cho nút "Thêm vào giỏ hàng" (toggle)
        if not item_created: # Nếu sản phẩm đã có trong giỏ
            # Nếu item đã tồn tại (không phải vừa được tạo), thì xóa nó đi
            cart_item.delete()
            # Tính lại tổng tiền sau khi xóa
            new_total = sum(item.product.final_price * item.quantity for item in user_cart.items.all())
            return JsonResponse({'status': 'removed', 'message': 'Đã xóa khỏi giỏ!', 'new_total': new_total})
        elif item_created: # Nếu sản phẩm vừa được thêm
            # Nếu item vừa được tạo, nghĩa là đã thêm thành công
            return JsonResponse({'status': 'added', 'message': 'Đã thêm vào giỏ!', 'product_name': product.name})

    return JsonResponse({'status': 'error', 'message': 'Chỉ chấp nhận POST'}, status=400)