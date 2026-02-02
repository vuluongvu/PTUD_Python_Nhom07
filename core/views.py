from django.shortcuts import render
from .models import Product
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q


def home(request):
    products = Product.objects.all()
    components = Product.objects.filter(Q(is_vga=True) | Q(is_cpu=True) | Q(is_ram=True))[:5]
    return render(request, 'core/home.html', {'products': products, 'components': components})

