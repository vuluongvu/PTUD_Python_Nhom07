from django.shortcuts import render

# Create your views here.

def login_view(request):
    """View hiển thị trang đăng nhập."""
    return render(request, 'users/login.html')