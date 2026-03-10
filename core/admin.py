import json
from datetime import timedelta

from django.contrib import admin
from django.contrib.auth.models import User
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from django.utils import timezone

from .models import (
    Category, Brand, Product, Profile, Address, Warranty,
    Inventory, Cart, Coupon, Payment, Review, Order, OrderItem,
    ProductImage, Specification, LaptopConfig, AccessoryConfig
)


# =========================================
#  CUSTOM ADMIN SITE — Dashboard tích hợp
# =========================================
class LapStoreAdminSite(admin.AdminSite):
    site_header = 'LapStore Admin'
    site_title = 'LapStore Admin'
    index_title = 'Quản trị cửa hàng'

    def index(self, request, extra_context=None):
        """Override index to inject dashboard statistics."""
        extra_context = extra_context or {}

        # --- KPI ---
        total_products = Product.objects.filter(status=True).count()
        total_orders = Order.objects.count()
        total_revenue = Order.objects.filter(
            order_status=Order.Status.DELIVERED
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        total_users = User.objects.count()

        # --- Top Selling Products (Bar Chart) ---
        top_products = Inventory.objects.filter(
            sold_count__gt=0
        ).select_related('product').order_by('-sold_count')[:10]

        top_labels = [inv.product.name[:30] for inv in top_products]
        top_data = [inv.sold_count for inv in top_products]

        if not top_labels:
            top_from_orders = OrderItem.objects.values(
                'product__name'
            ).annotate(total_sold=Sum('quantity')).order_by('-total_sold')[:10]
            top_labels = [i['product__name'][:30] for i in top_from_orders]
            top_data = [i['total_sold'] for i in top_from_orders]

        # --- Monthly Revenue (Line Chart) ---
        now = timezone.now()
        six_months_ago = now - timedelta(days=180)

        monthly = Order.objects.filter(
            order_status=Order.Status.DELIVERED,
            created_at__gte=six_months_ago
        ).annotate(month=TruncMonth('created_at')).values('month').annotate(
            revenue=Sum('total_amount')
        ).order_by('month')

        rev_labels, rev_data = [], []
        for e in monthly:
            rev_labels.append(e['month'].strftime('T%m/%Y'))
            rev_data.append(float(e['revenue']))

        if not rev_labels:
            monthly = Order.objects.filter(
                created_at__gte=six_months_ago
            ).exclude(order_status=Order.Status.CANCELLED).annotate(
                month=TruncMonth('created_at')
            ).values('month').annotate(revenue=Sum('total_amount')).order_by('month')
            for e in monthly:
                rev_labels.append(e['month'].strftime('T%m/%Y'))
                rev_data.append(float(e['revenue']))

        # --- Order Status Distribution (Doughnut) ---
        status_counts = Order.objects.values('order_status').annotate(
            count=Count('id')
        ).order_by('order_status')
        status_map = dict(Order.Status.choices)
        status_labels = [status_map.get(s['order_status'], s['order_status']) for s in status_counts]
        status_data = [s['count'] for s in status_counts]

        # --- Recent Orders ---
        recent_orders = Order.objects.select_related('user').order_by('-created_at')[:5]

        extra_context['dashboard'] = {
            'total_products': total_products,
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'total_users': total_users,
            'top_products_labels': json.dumps(top_labels, ensure_ascii=False),
            'top_products_data': json.dumps(top_data),
            'revenue_labels': json.dumps(rev_labels, ensure_ascii=False),
            'revenue_data': json.dumps(rev_data),
            'order_status_labels': json.dumps(status_labels, ensure_ascii=False),
            'order_status_data': json.dumps(status_data),
            'recent_orders': recent_orders,
        }

        return super().index(request, extra_context=extra_context)


# Tạo instance custom admin site
lapstore_admin = LapStoreAdminSite(name='admin')

# Copy tất cả registry từ default admin site
# (Để các @admin.register decorator ở orders/admin.py vẫn hoạt động)


# =========================================
#  INLINE CONFIGS
# =========================================
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class SpecificationInline(admin.TabularInline):
    model = Specification
    extra = 3

class LaptopConfigInline(admin.StackedInline):
    model = LaptopConfig
    can_delete = False
    verbose_name_plural = 'Cấu hình Laptop'

class AccessoryConfigInline(admin.StackedInline):
    model = AccessoryConfig
    can_delete = False
    verbose_name_plural = 'Cấu hình Linh kiện'


# =========================================
#  ĐĂNG KÝ MODELS vào custom admin site
# =========================================
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'category', 'price', 'status')
    list_filter = ('status', 'brand', 'category', 'is_lap')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, SpecificationInline, LaptopConfigInline, AccessoryConfigInline]

    fieldsets = (
        (None, {'fields': ('name', 'slug', 'description', 'brand', 'category')}),
        ('Phân loại sản phẩm', {'fields': ('is_lap', 'is_vga', 'is_cpu', 'is_keyboard', 'is_ram', 'is_headphone', 'is_mouse', 'is_screen')}),
        ('Giá & Bảo hành', {'fields': ('price', 'discount_price', 'warranty')}),
        ('Trạng thái', {'fields': ('status', 'view_count')}),
    )

class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_value', 'min_order_value', 'expired_date', 'quantity', 'status')
    list_filter = ('status', 'expired_date')
    search_fields = ('code',)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')
    prepopulated_fields = {'slug': ('name',)}

class BrandAdmin(admin.ModelAdmin):
    search_fields = ('name',)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ('product', 'product_name', 'quantity', 'unit_price', 'subtotal')
    extra = 0
    can_delete = False
    def has_add_permission(self, request, obj=None):
        return False

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'shipping_name', 'total_amount', 'order_status', 'created_at')
    list_filter = ('order_status', 'created_at')
    search_fields = ('id', 'shipping_name', 'shipping_phone', 'user__username')
    list_editable = ('order_status',)
    inlines = [OrderItemInline]


# Đăng ký tất cả vào custom admin site
lapstore_admin.register(Product, ProductAdmin)
lapstore_admin.register(Coupon, CouponAdmin)
lapstore_admin.register(Category, CategoryAdmin)
lapstore_admin.register(Brand, BrandAdmin)
lapstore_admin.register(Order, OrderAdmin)
lapstore_admin.register(Profile)
lapstore_admin.register(Address)
lapstore_admin.register(Warranty)
lapstore_admin.register(Inventory)
lapstore_admin.register(Cart)
lapstore_admin.register(Payment)
lapstore_admin.register(Review)