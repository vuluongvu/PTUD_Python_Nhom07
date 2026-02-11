from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('product-detail/<slug:slug>/', views.product_detail, name='product-detail'),
    path('view-all-products/', views.view_all_products, name='view-all-products'),
    path('search-results/', views.search_results, name='search-results'),
    path('toggle-cart/', views.toggle_cart, name='toggle_cart'),
]