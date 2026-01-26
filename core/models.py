from django.db import models
from django.contrib.auth.models import User
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
# Create your models here.
#User
class Profile(TimeStampedModel):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('admin', 'Admin'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username
#Address
class Address(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    receiver_name = models.CharField(max_length=100)
    receiver_phone = models.CharField(max_length=15)
    full_address = models.TextField()

    def __str__(self):
        return self.full_address
#Category
class Category(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey(
        'self', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='children'
    )

    def __str__(self):
        return self.name
#Brand
class Brand(models.Model):
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    def __str__(self):
        return self.name
#Warranty
class Warranty(models.Model):
    period = models.IntegerField()  # months
    policy = models.TextField()

    def __str__(self):
        return f"{self.period} months"
#Product
class Product(TimeStampedModel):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    warranty = models.ForeignKey(Warranty, on_delete=models.SET_NULL, null=True)

    status = models.BooleanField(default=True)

    def __str__(self):
        return self.name
#Inventory
class Inventory(TimeStampedModel):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
#ProductImage
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image_url = models.URLField()
    is_primary = models.BooleanField(default=False)
    sort_order = models.IntegerField(default=0)
#Specification
class Specification(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    spec_name = models.CharField(max_length=100)
    spec_value = models.CharField(max_length=255)
#Cart
class Cart(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, default='active')
#CartItem
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
#Coupon
class Coupon(TimeStampedModel):
    code = models.CharField(max_length=50, unique=True)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    expired_date = models.DateTimeField()
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.code
#Order
class Order(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)

    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    order_status = models.CharField(max_length=30)
#OrderItem
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
#Payment
class Payment(TimeStampedModel):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=50)
    payment_status = models.CharField(max_length=30)
#RefundRequest
class RefundRequest(TimeStampedModel):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    refund_status = models.CharField(max_length=30)
#Review
class Review(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()
#WishList
class WishList(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)