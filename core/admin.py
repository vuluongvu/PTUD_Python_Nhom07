from django.contrib import admin
from .models import (
    Category, Brand, Product, Profile, Address, Warranty, 
    Inventory, Cart, Coupon, Payment, Review,
    ProductImage, Specification, LaptopConfig, AccessoryConfig
)

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1 # Hiển thị 1 dòng trống để thêm ảnh

class SpecificationInline(admin.TabularInline):
    model = Specification
    extra = 3 # Hiển thị 3 dòng trống để thêm thông số

class LaptopConfigInline(admin.StackedInline):
    model = LaptopConfig
    can_delete = False
    verbose_name_plural = 'Cấu hình Laptop'

class AccessoryConfigInline(admin.StackedInline):
    model = AccessoryConfig
    can_delete = False
    verbose_name_plural = 'Cấu hình Linh kiện'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'category', 'price', 'status')
    list_filter = ('status', 'brand', 'category', 'is_lap')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, SpecificationInline, LaptopConfigInline, AccessoryConfigInline]

    # Tùy chỉnh form để dễ nhập liệu hơn
    fieldsets = (
        (None, {'fields': ('name', 'slug', 'description', 'brand', 'category')}),
        ('Phân loại sản phẩm', {'fields': ('is_lap', 'is_vga', 'is_cpu', 'is_keyboard', 'is_ram', 'is_headphone', 'is_mouse', 'is_screen')}),
        ('Giá & Bảo hành', {'fields': ('price', 'discount_price', 'warranty')}),
        ('Trạng thái', {'fields': ('status', 'view_count')}),
    )
    
# Đăng ký các model còn lại để có thể quản lý trong trang admin
admin.site.register(Profile)
admin.site.register(Address)
admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(Warranty)
admin.site.register(Inventory)
admin.site.register(Cart)
admin.site.register(Coupon)
admin.site.register(Payment)
admin.site.register(Review)