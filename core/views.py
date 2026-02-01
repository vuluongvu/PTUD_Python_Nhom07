from django.shortcuts import render
from .models import Product
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

# core/views.py
def home(request):
    products = Product.objects.all()
    # Không cần tính toán avatar ở đây nữa vì đã có context_processor lo
    return render(request, 'core/home.html', {'products': products})