from django.shortcuts import get_object_or_404, render
from django.core.paginator import Paginator
from django.db.models import Q, Avg, Count
from django.http import JsonResponse
from django.db import transaction
from core.models import Brand, Cart, CartItem, Category, Product, Review, WishList, Coupon
from django.utils import timezone


# Create your views here.
def view_all_products(request):
   
    products_list = Product.objects.filter(status=True)
    
    # --- Lọc Sản Phẩm ---
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
            if max_price == 'inf': 
                products_list = products_list.filter(price__gte=int(min_price) * 1000000)
            else:
                products_list = products_list.filter(price__range=(int(min_price) * 1000000, int(max_price) * 1000000))
        except ValueError:
            pass 

    # Lấy tham số sort từ URl
    sort_by = request.GET.get('sort', 'default')
    if sort_by == 'price_asc':
        products_list = products_list.order_by('price')
    elif sort_by == 'price_desc':
        products_list = products_list.order_by('-price')
    else: 
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
    related_query = Product.objects.filter(
        category=product.category, status=True
    ).exclude(slug=slug).select_related('laptop_config').prefetch_related('images')

    if sort_by == 'price_asc':
        related_products = related_query.order_by('price')
        related_products = related_query.order_by('price')[:5]
    elif sort_by == 'price_desc':
        related_products = related_query.order_by('-price')
        related_products = related_query.order_by('-price')[:5]
    else:
        related_products = related_query.order_by('?')[:5]

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
        product = get_object_or_404(Product, id=product_id)

        # Lấy hoặc tạo giỏ hàng cho user
        user_cart, _ = Cart.objects.get_or_create(user=request.user)

        # Kiểm tra sản phẩm đã có trong CartItem chưa
        cart_item, item_created = user_cart.items.get_or_create(product=product)

        if item_created:
            status = 'added'
            message = 'Đã thêm sản phẩm vào giỏ hàng!'
        else:
            # Nếu sản phẩm đã tồn tại, không làm gì cả, chỉ thông báo
            status = 'exists'
            message = 'Sản phẩm đã có trong giỏ hàng.'

        # Lấy số lượng mới nhất
        cart_count = user_cart.items.count()

        return JsonResponse({
            'status': status,
            'message': message,
            'cart_count': cart_count
        })

    return JsonResponse({'status': 'error', 'message': 'Chỉ chấp nhận POST'}, status=400)

def remove_from_cart(request):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'login_required', 'message': 'Bạn phải đăng nhập để thực hiện thao tác này.'}, status=401)

    if request.method == "POST":
        # Giả định rằng 'id' được gửi từ trang giỏ hàng là ID của CartItem, không phải Product ID.
        # Đây là cách tiếp cận trực tiếp và an toàn hơn để xóa một mục cụ thể.
        item_id = request.POST.get('id')
        sub_total = 0
        cart_count = 0
        status = 'error'
        message = 'Có lỗi xảy ra.'

        if not item_id:
            return JsonResponse({'status': 'error', 'message': 'Cần có ID của mục trong giỏ hàng.'}, status=400)

        try:
            user_cart = Cart.objects.get(user=request.user)
            try:
                cart_item = user_cart.items.get(id=item_id)
                cart_item.delete()
                status = 'removed'
                message = 'Đã xóa sản phẩm khỏi giỏ hàng.'
            except CartItem.DoesNotExist:
                status = 'not_found'
                message = 'Sản phẩm không có trong giỏ hàng.'

            # --- Re-calculate totals and check coupon ---
            remaining_items = user_cart.items.select_related('product').all()
            cart_count = remaining_items.count()
            sub_total = sum(item.product.final_price * item.quantity for item in remaining_items)

            coupon_id = request.session.get('coupon_id')
            discount_amount = 0
            coupon_removed_flag = False
            if coupon_id:
                try:
                    coupon = Coupon.objects.get(id=coupon_id)
                    if coupon.status and coupon.expired_date >= timezone.now() and sub_total >= coupon.min_order_value:
                        discount_amount = coupon.discount_value
                    else: # Coupon is no longer valid
                        del request.session['coupon_id']
                        coupon_removed_flag = True
                except Coupon.DoesNotExist:
                    del request.session['coupon_id']
                    coupon_removed_flag = True
            
            final_total = sub_total - discount_amount

        except Cart.DoesNotExist:
            message = 'Không tìm thấy giỏ hàng.'
            # cart_count and sub_total are already 0, status is 'error'
            final_total = 0
            discount_amount = 0
            coupon_removed_flag = False

        return JsonResponse({
            'status': status,
            'message': message,
            'cart_count': cart_count,
            'sub_total': sub_total,
            'discount_amount': discount_amount,
            'final_total': final_total,
            'coupon_removed': coupon_removed_flag,
        })

    return JsonResponse({'status': 'error', 'message': 'Yêu cầu không hợp lệ.'}, status=400)

def update_cart_quantity(request):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'login_required', 'message': 'Bạn phải đăng nhập.'}, status=401)

    if request.method == "POST":
        item_id = request.POST.get('id')
        action = request.POST.get('action') # 'increase' or 'decrease'

        if not item_id or action not in ['increase', 'decrease']:
            return JsonResponse({'status': 'error', 'message': 'Yêu cầu không hợp lệ.'}, status=400)

        try:
            with transaction.atomic():
                user_cart = Cart.objects.select_for_update().get(user=request.user)
                cart_item = user_cart.items.select_related('product').get(id=item_id)

                if action == 'increase':
                    # TODO: Có thể thêm kiểm tra tồn kho sản phẩm ở đây
                    cart_item.quantity += 1
                    cart_item.save()
                    status = 'updated'
                    message = 'Đã cập nhật số lượng.'
                
                elif action == 'decrease':
                    if cart_item.quantity > 1:
                        cart_item.quantity -= 1
                        cart_item.save()
                        status = 'updated'
                        message = 'Đã cập nhật số lượng.'
                    else:
                        # Nếu số lượng là 1, không cho giảm thêm.
                        status = 'limit_reached'
                        message = 'Số lượng tối thiểu là 1.'

                # Tính tổng tiền cho riêng item này
                item_subtotal = cart_item.product.final_price * cart_item.quantity

                # --- Re-calculate totals and check coupon ---
                remaining_items = user_cart.items.select_related('product').all()
                cart_count = remaining_items.count()
                sub_total = sum(item.product.final_price * item.quantity for item in remaining_items)
                
                coupon_id = request.session.get('coupon_id')
                discount_amount = 0
                coupon_removed_flag = False
                if coupon_id:
                    try:
                        coupon = Coupon.objects.get(id=coupon_id)
                        if coupon.status and coupon.expired_date >= timezone.now() and sub_total >= coupon.min_order_value:
                            discount_amount = coupon.discount_value
                        else: # Coupon is no longer valid
                            del request.session['coupon_id']
                            coupon_removed_flag = True
                    except Coupon.DoesNotExist:
                        del request.session['coupon_id']
                        coupon_removed_flag = True
                
                final_total = sub_total - discount_amount
                
                return JsonResponse({
                    'status': status, 'message': message, 'cart_count': cart_count,
                    'sub_total': sub_total, 'discount_amount': discount_amount, 'final_total': final_total,
                    'item_quantity': cart_item.quantity,
                    'item_subtotal': item_subtotal,
                    'coupon_removed': coupon_removed_flag,
                })

        except (Cart.DoesNotExist, CartItem.DoesNotExist):
            return JsonResponse({'status': 'error', 'message': 'Sản phẩm hoặc giỏ hàng không tồn tại.'}, status=404)

    return JsonResponse({'status': 'error', 'message': 'Chỉ chấp nhận POST.'}, status=400)

