from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify

# --- Utilities ---
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

# --- User & Profile ---
class Profile(TimeStampedModel):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('admin', 'Admin'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username

class Address(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    receiver_name = models.CharField(max_length=100)
    receiver_phone = models.CharField(max_length=15)
    full_address = models.TextField()
    is_default = models.BooleanField(default=False) # Thêm field này để chọn địa chỉ mặc định

    def __str__(self):
        return f"{self.receiver_name} - {self.full_address}"

# --- Catalog ---
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True) # SEO Friendly URL
    parent = models.ForeignKey(
        'self', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='children'
    )

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
    country = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Warranty(models.Model):
    period = models.IntegerField(help_text="Warranty period in months")
    policy = models.TextField()

    def __str__(self):
        return f"{self.period} months"

class Product(TimeStampedModel):
    name = models.CharField(max_length=200, db_index=True) # Index để search nhanh
    slug = models.SlugField(max_length=250, unique=True, blank=True) # SEO
    description = models.TextField()
    
    # Validation: Giá không được âm
    price = models.DecimalField(
        max_digits=10, decimal_places=2, 
        validators=[MinValueValidator(0)]
    )
    discount_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0)]
    )

    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name='products')
    warranty = models.ForeignKey(Warranty, on_delete=models.SET_NULL, null=True)
    
    status = models.BooleanField(default=True)
    
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, # Nếu xóa ông Admin, sản phẩm vẫn còn (nhưng mất tên người tạo)
        null=True, 
        blank=True,
        related_name='products_created',
        verbose_name="Người tạo"
    )
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image_url = models.URLField()
    is_primary = models.BooleanField(default=False)
    sort_order = models.IntegerField(default=0)

class Inventory(TimeStampedModel):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='inventory')
    quantity = models.PositiveIntegerField(default=0) # Không được âm

class Specification(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='specifications')
    spec_name = models.CharField(max_length=100)
    spec_value = models.CharField(max_length=255)

# --- Shopping Cart ---
class Cart(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    status = models.CharField(max_length=20, default='active')

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    # Lưu ý: unit_price ở đây có thể bỏ nếu muốn tính realtime, 
    # nhưng giữ lại nếu muốn snapshot giá lúc add vào giỏ.

# --- Order System (Critical Logic Changes) ---
class Coupon(TimeStampedModel):
    code = models.CharField(max_length=50, unique=True)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    expired_date = models.DateTimeField()
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.code

class Order(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PROCESSING = 'processing', 'Processing'
        SHIPPED = 'shipped', 'Shipped'
        DELIVERED = 'delivered', 'Delivered'
        CANCELLED = 'cancelled', 'Cancelled'

    # Nếu user xóa tài khoản, đơn hàng vẫn phải còn để báo cáo doanh thu -> SET_NULL
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='orders')
    
    # SNAPSHOT ADDRESS: Lưu cứng thông tin giao hàng
    # Không dùng ForeignKey tới Address để tránh việc user sửa địa chỉ làm sai đơn cũ
    shipping_name = models.CharField(max_length=100)
    shipping_phone = models.CharField(max_length=15)
    shipping_address = models.TextField()
    
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    order_status = models.CharField(
        max_length=20, 
        choices=Status.choices, 
        default=Status.PENDING
    )

    def __str__(self):
        return f"Order #{self.id} - {self.user}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    # Nếu sản phẩm bị xóa khỏi DB, OrderItem vẫn nên tồn tại (hoặc set null)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    
    # Snapshot thông tin sản phẩm lúc mua
    product_name = models.CharField(max_length=200) # Backup tên sản phẩm
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2) # Giá lúc mua
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

# --- Post-Purchase ---
class Payment(TimeStampedModel):
    class Method(models.TextChoices):
        COD = 'cod', 'Cash on Delivery'
        BANKING = 'banking', 'Bank Transfer'
        MOMO = 'momo', 'Momo Wallet'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    payment_method = models.CharField(max_length=50, choices=Method.choices)
    payment_status = models.CharField(max_length=30, choices=Status.choices, default=Status.PENDING)

class RefundRequest(TimeStampedModel):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    refund_status = models.CharField(max_length=30, default='pending')

class Review(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField()

class WishList(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'product') # Một user không thể wish 1 món 2 lần
class Specification(models.Model):
    # Nối với sản phẩm (Một cái Laptop có nhiều dòng thông số)
    product = models.ForeignKey(Product, on_delete=models.CASCADE) 
    
    # Tên thông số (Ví dụ: "RAM", "CPU", "Màn hình")
    spec_name = models.CharField(max_length=100) 
    
    # Giá trị (Ví dụ: "16GB", tg"Core i5", "14 inch OLED")
    spec_value = models.CharField(max_length=255)