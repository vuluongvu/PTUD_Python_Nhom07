from django.contrib import admin

from .models import (
    Profile, Address, Category, Brand, Warranty, 
    Product, ProductImage, Inventory, Specification, 
    Cart, Order, OrderItem, Coupon, Payment, Review
)

#   1. Cấu hình hiển thị User Profile  
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'role', 'status')
    list_filter = ('role', 'status')
    search_fields = ('user__username', 'full_name')

#   2. Cấu hình Product (Có logic tự lưu người tạo)  
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1 # Cho phép thêm nhanh 1 ảnh

class SpecificationInline(admin.TabularInline):
    model = Specification
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # Hiển thị các cột này ra ngoài danh sách
    list_display = ('name', 'category', 'price', 'created_by', 'status', 'created_at')
    
    # Tạo bộ lọc bên tay phải
    list_filter = ('status', 'category', 'brand')
    
    # Thanh tìm kiếm
    search_fields = ('name', 'description')
    
    # Tự động tạo slug từ tên (nếu Heo dùng code cũ có slug)
    prepopulated_fields = {'slug': ('name',)} 
    
    # Cho phép sửa nhanh ảnh và thông số ngay trong trang Product
    inlines = [ProductImageInline, SpecificationInline]

    # Ẩn field created_by để tự động điền
    readonly_fields = ('created_by',)

    # Hàm tự động lưu người tạo (như mình đã chỉ ở trên)
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

#   3. Cấu hình Order (Để xem chi tiết món hàng bên trong)  
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ('product', 'quantity', 'unit_price', 'subtotal')
    extra = 0 # Không cho thêm, rread only

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_amount', 'order_status', 'created_at')
    list_filter = ('order_status', 'created_at')
    inlines = [OrderItemInline] # Xem chi tiết đơn hàng ngay
    
class SpecificationInline(admin.TabularInline):
    model = Specification
    extra = 1
#   4. Đăng ký các bảng còn lại  
admin.site.register(Address)
admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(Warranty)
admin.site.register(Inventory)
admin.site.register(Cart)
admin.site.register(Coupon)
admin.site.register(Payment)
admin.site.register(Review)