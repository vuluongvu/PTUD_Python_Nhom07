from .models import Cart, WishList, Profile

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

    return {
        'cart_count': cart_count,
        'wishlist_count': wishlist_count,
        'user_avatar_url': user_avatar_url,
    }