from django.db.models import Count
from .models import Cart, WishList, Profile, Category, Brand

def global_context(request):
    """
    Cung cấp các biến global cho tất cả template, 
    ví dụ: số lượng sản phẩm trong giỏ hàng, wishlist và avatar người dùng.
    """
    cart_count = 0
    wishlist_count = 0
    user_avatar_url = None

    if request.user.is_authenticated:
        # Đếm cart
        try:
            # Lấy giỏ hàng của người dùng và đếm số lượng item
            user_cart = Cart.objects.get(user=request.user)
            cart_count = user_cart.items.count()
        except Cart.DoesNotExist:
            cart_count = 0

        # Đếm số lượng sản phẩm trong wishlist
        wishlist_count = WishList.objects.filter(user=request.user).count()

        # Lấy avatar
        profile = Profile.objects.filter(user=request.user).first()
        if profile and profile.avatar:
            user_avatar_url = profile.avatar

    # Lấy danh sách category cho mega menu (parent is Null)
    mega_categories = Category.objects.filter(parent__isnull=True).prefetch_related('children')
    
    # Filter options cho Megamenu và Sidebar
    all_brands = Brand.objects.annotate(product_count=Count('products')).filter(product_count__gt=0)
    all_categories = Category.objects.annotate(product_count=Count('products')).filter(product_count__gt=0)

    price_ranges = [
        {'value': '0-10', 'label': 'Dưới 10 triệu'},
        {'value': '10-15', 'label': '10 - 15 triệu'},
        {'value': '15-20', 'label': '15 - 20 triệu'},
        {'value': '20-30', 'label': '20 - 30 triệu'},
        {'value': '30-inf', 'label': 'Trên 30 triệu'},
    ]
    
    ram_options = [
        {'value': '8', 'label': '8 GB'},
        {'value': '16', 'label': '16 GB'},
        {'value': '32', 'label': '32 GB'},
        {'value': '64', 'label': '64 GB'},
    ]

    storage_options = [
        {'value': '256', 'label': '256 GB'},
        {'value': '512', 'label': '512 GB'},
        {'value': '1024', 'label': '1 TB'},
        {'value': '2048', 'label': '2 TB'},
    ]

    return {
        'cart_count': cart_count,
        'wishlist_count': wishlist_count,
        'user_avatar_url': user_avatar_url,
        'mega_categories': mega_categories,
        'all_brands': all_brands,
        'all_categories': all_categories,
        'price_ranges': price_ranges,
        'ram_options': ram_options,
        'storage_options': storage_options,
    }