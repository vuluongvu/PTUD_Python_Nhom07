from django.contrib import admin
from core.models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    """
    Hiển thị các OrderItem ngay trong trang chi tiết của Order.
    """
    model = OrderItem
    # Các trường này chỉ để xem, không cho sửa để đảm bảo toàn vẹn dữ liệu
    readonly_fields = ('product', 'product_name', 'quantity', 'unit_price', 'subtotal')
    extra = 0  # Không hiển thị các dòng trống để thêm mới
    can_delete = False # Không cho phép xóa item khỏi đơn hàng đã đặt

    def has_add_permission(self, request, obj=None):
        # Không cho phép thêm item mới vào đơn hàng đã đặt từ trang admin
        return False

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Tùy chỉnh hiển thị cho model Order.
    """
    list_display = ('id', 'shipping_name', 'total_amount', 'order_status', 'created_at')
    list_filter = ('order_status', 'created_at')
    search_fields = ('id', 'shipping_name', 'shipping_phone', 'user__username')
    list_editable = ('order_status',)
    inlines = [OrderItemInline]
