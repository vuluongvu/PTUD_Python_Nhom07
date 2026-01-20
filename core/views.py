from django.shortcuts import render

def home(request):
    """View hiển thị trang chủ."""
    return render(request, 'core/home.html')