from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.db import transaction

# --- Utilities ---
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

# --- User và Profile ---
class Profile(TimeStampedModel):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('admin', 'Admin'),
        ('staff', 'Staff'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    avatar = models.URLField(max_length=500, blank=True, null=True) 
    status = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} ({self.full_name})"

class Address(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    receiver_name = models.CharField(max_length=100)
    receiver_phone = models.CharField(max_length=15)
    province = models.CharField(max_length=100, blank=True) 
    district = models.CharField(max_length=100, blank=True) 
    ward = models.CharField(max_length=100, blank=True)
    specific_address = models.CharField(max_length=255, blank=True) 
    is_default = models.BooleanField(default=False)

    @property
    def full_address(self):
        return f"{self.specific_address}, {self.ward}, {self.district}, {self.province}"

    def save(self, *args, **kwargs):
        if self.is_default:
            with transaction.atomic():
                Address.objects.filter(user=self.user, is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.receiver_name} - {self.full_address}"

# --- Catalog ---
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True) 
    parent = models.ForeignKey(
        'self', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='children'
    )
    image_url = models.URLField(blank=True, null=True) # Ảnh đại diện danh mục

    class Meta:
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Brand(models.Model):
    name = models.CharField(max_length=100)
    logo_url = models.URLField(blank=True, null=True)
    country = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name

class Warranty(models.Model):
    period = models.IntegerField(help_text="Warranty period in months")
    policy = models.TextField()

    def __str__(self):
        return f"{self.period} Tháng"

class Product(TimeStampedModel):
    name = models.CharField(max_length=200, db_index=True) 
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    description = models.TextField()
    is_lap = models.BooleanField(default=False)
    
    # Giá bán
    price = models.DecimalField(
        max_digits=15, decimal_places=0, 
        validators=[MinValueValidator(0)],
        help_text="Giá niêm yết"
    )
    discount_price = models.DecimalField(
        max_digits=15, decimal_places=0, null=True, blank=True,
        validators=[MinValueValidator(0)],
        help_text="Giá khuyến mãi (nếu có)"
    )

    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name='products')
    warranty = models.ForeignKey(Warranty, on_delete=models.SET_NULL, null=True, blank=True)
    
    status = models.BooleanField(default=True) # Active/Inactive
    view_count = models.PositiveIntegerField(default=0) # Đếm lượt xem
    
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='products_created'
    )

    @property
    def final_price(self):
        return self.discount_price if self.discount_price and self.discount_price < self.price else self.price

    @property
    def price_vn(self):
        """Trả về giá niêm yết định dạng VND (VD: 20.000.000 đ)"""
        return "{:,.0f} đ".format(self.price).replace(",", ".")

    @property
    def discount_price_vn(self):
        """Trả về giá khuyến mãi định dạng VND"""
        if self.discount_price:
            return "{:,.0f} đ".format(self.discount_price).replace(",", ".")
        return ""

    @property
    def is_laptop(self):
        """Kiểm tra xem sản phẩm có cấu hình laptop hay không"""
        return hasattr(self, 'laptop_config') and self.laptop_config is not None

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image_url = models.URLField(max_length=500) # Tăng độ dài link
    is_primary = models.BooleanField(default=False)
    sort_order = models.IntegerField(default=0)
    image_video_url = models.URLField(max_length=500, blank=True, null=True) # Đã sửa: Cho phép null
    image_url_feature = models.URLField(max_length=500, null=True, blank=True)
    class Meta:
        ordering = ['sort_order']

class Inventory(TimeStampedModel):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='inventory')
    quantity = models.PositiveIntegerField(default=0)
    sold_count = models.PositiveIntegerField(default=0) # Thống kê số lượng đã bán

    def __str__(self):
        return f"{self.product.name} - Kho: {self.quantity}"

class Specification(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='specifications')
    spec_name = models.CharField(max_length=100)
    spec_value = models.CharField(max_length=255)

# --- Shopping Cart ---
class Cart(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    
    def __str__(self):
        return f"Cart of {self.user.username}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    class Meta:
        unique_together = ('cart', 'product') # Tránh trùng sản phẩm trong 1 giỏ hàng

# --- Hệ thống đặt hàng (Order) ---
class Coupon(TimeStampedModel):
    code = models.CharField(max_length=50, unique=True)
    discount_value = models.DecimalField(max_digits=10, decimal_places=0)
    min_order_value = models.DecimalField(max_digits=12, decimal_places=0, default=0) # Đơn tối thiểu
    expired_date = models.DateTimeField()
    quantity = models.PositiveIntegerField(default=100) # Số lượng mã
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.code

class Order(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Chờ xác nhận'
        PROCESSING = 'processing', 'Đang xử lý'
        SHIPPED = 'shipped', 'Đang giao'
        DELIVERED = 'delivered', 'Đã giao'
        CANCELLED = 'cancelled', 'Đã hủy'

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='orders')
    
    # Snapshot thông tin giao hàng
    shipping_name = models.CharField(max_length=100)
    shipping_phone = models.CharField(max_length=15)
    shipping_address = models.TextField()
    note = models.TextField(blank=True, null=True) # Ghi chú của khách
    
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=15, decimal_places=0) # Tổng tiền cuối cùng
    
    order_status = models.CharField(
        max_length=20, 
        choices=Status.choices, 
        default=Status.PENDING
    )

    def __str__(self):
        return f"Order #{self.id} - {self.user}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    
    # Snapshot sản phẩm
    product_name = models.CharField(max_length=200) 
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=15, decimal_places=0) # Giá tại thời điểm mua
    subtotal = models.DecimalField(max_digits=15, decimal_places=0)

    def save(self, *args, **kwargs):
        self.subtotal = self.unit_price * self.quantity
        super().save(*args, **kwargs)

# --- Post-Mua ---
class Payment(TimeStampedModel):
    class Method(models.TextChoices):
        COD = 'cod', 'Thanh toán khi nhận hàng'
        BANKING = 'banking', 'Chuyển khoản ngân hàng'
        MOMO = 'momo', 'Ví Momo'
        VNPAY = 'vnpay', 'VNPay'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Chờ thanh toán'
        COMPLETED = 'completed', 'Đã thanh toán'
        FAILED = 'failed', 'Thất bại'

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    payment_method = models.CharField(max_length=50, choices=Method.choices)
    payment_status = models.CharField(max_length=30, choices=Status.choices, default=Status.PENDING)
    transaction_id = models.CharField(max_length=100, blank=True, null=True) # Mã giao dịch từ cổng thanh toán

class Review(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField()

    class Meta:
        unique_together = ('user', 'product') # Quan trọng: Mỗi người chỉ review 1 lần/sp

class WishList(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'product')

# --- CẤU HÌNH LAPTOP (QUAN TRỌNG: Cải tiến bộ lọc) ---
class LaptopConfig(models.Model):
    product = models.OneToOneField(
        Product, 
        on_delete=models.CASCADE, 
        related_name='laptop_config' 
    )
    
    # CPU
    cpu = models.CharField(max_length=100, help_text="VD: Intel Core i5 12400H")
    
    # RAM - Tách ra để lọc
    ram_gb = models.PositiveIntegerField(help_text="Dung lượng RAM (số) để lọc. VD: 8, 16",null=True) 
    ram_desc = models.CharField(max_length=100, verbose_name="Mô tả RAM", help_text="VD: 16GB DDR4 3200MHz",null=True)
    
    # Ổ cứng - Tách ra để lọc
    storage_gb = models.PositiveIntegerField(help_text="Dung lượng ổ cứng (GB). VD: 512, 1024", null=True)
    storage_desc = models.CharField(max_length=100, verbose_name="Mô tả ổ cứng", help_text="VD: 512GB SSD NVMe",null=True)
    
    # VGA - Có thể tách VRAM nếu cần
    vga = models.CharField(max_length=100, verbose_name="Card đồ họa")
    
    # Màn hình
    screen_size = models.FloatField(help_text="Kích thước màn hình (inch). VD: 15.6",null=True)
    screen_desc = models.CharField(max_length=100, verbose_name="Chi tiết màn hình", null=True)
    
    battery = models.CharField(max_length=50, verbose_name="Pin", blank=True)
    weight = models.DecimalField(max_digits=4, decimal_places=2, verbose_name="Trọng lượng (kg)")
    
    def __str__(self):
        return f"Config: {self.product.name}"

# --- CẤU HÌNH LINH KIỆN ---
class AccessoryConfig(models.Model):
    product = models.OneToOneField(
        Product, 
        on_delete=models.CASCADE, 
        related_name='accessory_config'
    )
    
    TYPE_CHOICES = (
        ('mouse', 'Chuột'),
        ('keyboard', 'Bàn phím'),
        ('headphone', 'Tai nghe'),
        ('screen', 'Màn hình rời'),
        ('vga', 'Card đồ họa'),
        ('cpu', 'CPU'),
        ('ram', 'RAM PC'),
        ('other', 'Khác'),
    )
    
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='other')
    connect_type = models.CharField(max_length=50, blank=True, verbose_name="Kết nối")
    is_led_rgb = models.BooleanField(default=False)
    detail = models.TextField(verbose_name="Thông số chi tiết", blank=True) # Có thể blank

    def __str__(self):
        return f"Linh kiện: {self.type} - {self.product.name}"