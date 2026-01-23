from django.shortcuts import render, redirect

app_name = 'orders'

# Create your views here.
def view_cart(request):
    """View hiển thị giỏ hàng."""
    # This view will eventually need to fetch cart data
    # For now, we pass an empty context
    return render(request, 'orders/cart.html')

def checkout(request):
    """View for the checkout page."""
    return render(request, 'orders/checkout.html')

def wishlist(request):
    """View for the wishlist page."""
    return render(request, 'orders/wishlist.html')


