from django.db import models
from datetime import datetime
import uuid
from django.urls import reverse
from django.conf import settings
from django.utils import timezone


# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=100, default="Select Category")
    date = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return self.name

    @staticmethod
    def getAllCategory():
        return Category.objects.all()


class Product(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    name = models.CharField(max_length=100)
    price = models.FloatField(default=0)
    description = models.TextField()
    # description = RichTextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    rating_count = models.FloatField(default=0)
    product_purchase = models.IntegerField(default=0)
    shipping_fee = models.FloatField(default=10)
    date_posted = models.DateTimeField(default=datetime.now)
    date_updated = models.DateTimeField(auto_now=True)
    delivery_period = models.IntegerField(default=0)

    class Meta:
        ordering = ["-date_posted"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("product-detail", kwargs={"pk": self.id})

    @staticmethod
    def getProductByFilter(category_id):
        if category_id:
            return Product.objects.filter(category=category_id)
        else:
            return Product.objects.all()

    def amount(self):
        total = self.price * self.product_purchase
        return total


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(default='2placeholder_test_b9l9NT5.png', upload_to='product_images')
    date_posted = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return f"{self.image}"


class ProductReview(models.Model):
    RATING_TYPES = (
        (1, "★☆☆☆☆ (1/5)"), (2, "★★☆☆☆ (2/5)"), (3, "★★★☆☆ (3/5)"),
        (4, "★★★★☆ (4/5)"), (5, "★★★★★ (5/5)")
    )

    customer_info = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    default_product = models.CharField(max_length=1000, null=True, blank=True)
    rating = models.IntegerField(choices=RATING_TYPES, null=True, blank=True)
    review = models.TextField()
    date_added = models.DateTimeField(default=datetime.now)

    class Meta:
        ordering = ["-date_added"]

    def __str__(self):
        return f'{self.customer_info.username} comment'


class Checkout(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    complete = models.BooleanField(default=False, null=True, blank=True)
    date_posted = models.DateTimeField(default=datetime.now)

    class Meta:
        ordering = ["-date_posted"]

    def __str__(self):
        return f'{self.quantity} of {self.product}'

    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=20,
                                     choices=(('percentage', 'Percentage'), ('fixed_amount', 'Fixed Amount')))
    discount_value = models.DecimalField(max_digits=5, decimal_places=2)
    active_from = models.DateTimeField(default=timezone.now)
    active_to = models.DateTimeField(null=True, blank=True)  # Optional for limited validity
    minimum_order_value = models.DecimalField(max_digits=10, decimal_places=2, null=True,
                                              blank=True)  # Optional minimum order amount

    def __str__(self):
        return f"{self.code}"

    def is_valid(self, order):
        now = timezone.now()
        return (
                self.active_from <= now and  # Check if active period has started
                (self.active_to is None or self.active_to >= now) and
                # Check if active period has ended (optional)
                (
                    self.minimum_order_value is None or self.minimum_order_value <= 0
                    or
                    self.minimum_order_value <= order
                )
                # Check minimum order amount (optional)
        )


class UserCoupon(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    used = models.BooleanField(default=False)
    used_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.coupon} used by {self.user} on {self.used_date}"


class Order(models.Model):
    ORDER_CATEGORIES = [
        ("Pending", "Pending"), ("Delivered", "Delivered"),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=30)
    order_item = models.ManyToManyField(Checkout, related_name="order_item")
    default_order_item = models.CharField(max_length=1000, null=True, blank=True)
    reference = models.CharField(max_length=500, null=True, blank=True)
    default_price = models.FloatField(default=0)
    ordered = models.BooleanField(default=False)
    date_posted = models.DateTimeField(default=datetime.now)
    address = models.CharField(max_length=500, null=True, blank=True)
    order_status = models.CharField(choices=ORDER_CATEGORIES, max_length=50)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)  # Optional foreign key

    class Meta:
        ordering = ["-date_posted"]

    def __str__(self):
        return f'{self.user}'

    def get_absolute_url(self):
        return reverse("order_summary", kwargs={"order_id": self.transaction_id})


    @property
    def total_order_item_price(self):
        total = self.order_item.all()
        total_price = sum([i.get_total for i in total])
        return total_price

    @classmethod
    def user_first_purchase(cls, user):
        return cls.objects.filter(user=user).exists()
