from django.contrib import admin

from .models import (
    Profile, Address, Category, Brand, Warranty, 
    Product, ProductImage, Inventory, 
    LaptopConfig, AccessoryConfig, 
    Cart, Order, OrderItem, Coupon, Payment, Review
)

# ---  User Profile ---
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'role', 'status')
    list_filter = ('role', 'status')
    search_fields = ('user__username', 'full_name')

# ---  Product ---
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class LaptopConfigInline(admin.StackedInline):
    model = LaptopConfig
    can_delete = False
    verbose_name_plural = 'Cấu hình Laptop (Chỉ nhập nếu là Laptop)'


class AccessoryConfigInline(admin.StackedInline):
    model = AccessoryConfig
    can_delete = False
    verbose_name_plural = 'Thông số Linh kiện (Chỉ nhập nếu là Chuột/Phím/Loa...)'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'created_by', 'status', 'created_at')
    list_filter = ('status', 'category', 'brand')
    search_fields = ('name', 'description')
    
    # slug auto
    prepopulated_fields = {'slug': ('name',)}
    
    inlines = [ProductImageInline, LaptopConfigInline, AccessoryConfigInline]

    readonly_fields = ('created_by',)

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

# --- Order ---
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    # readonly
    readonly_fields = ('product', 'quantity', 'unit_price', 'subtotal')
    extra = 0
    can_delete = False

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_amount', 'order_status', 'created_at')
    list_filter = ('order_status', 'created_at')
    inlines = [OrderItemInline]

admin.site.register(Address)
admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(Warranty)
admin.site.register(Inventory)
admin.site.register(Cart)
admin.site.register(Coupon)
admin.site.register(Payment)
admin.site.register(Review)