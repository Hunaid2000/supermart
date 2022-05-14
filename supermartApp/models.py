from django.db import models

class Account(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=20)
    is_seller = models.BooleanField(default=False)

class Store(models.Model):
    store_name = models.CharField(max_length=50, unique=True)
    contact = models.CharField(max_length=20)
    location = models.TextField()
    seller = models.ForeignKey(Account, on_delete=models.CASCADE)

class Product(models.Model):
    name = models.CharField(max_length=50)
    brand = models.CharField(max_length=50)
    price = models.FloatField()
    total_stock = models.IntegerField()
    small = models.IntegerField(null=True, blank=True, default=None)
    medium = models.IntegerField(null=True, blank=True, default=None)
    large = models.IntegerField(null=True, blank=True, default=None)
    description = models.TextField()
    store = models.ForeignKey(Store, on_delete=models.CASCADE)

class ProductImages(models.Model):
    image = models.ImageField(upload_to="product_images/")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

class Cart(models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE)
    total = models.FloatField(blank=True)

class Item(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    item_total = models.FloatField(blank=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)

class Order(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    shipping_address = models.CharField(max_length=100)
    shipping_option = models.CharField(max_length=50)
    payment_option = models.CharField(max_length=50)
    shipping_fee = models.FloatField(blank=True)
    order_total = models.FloatField(blank=True)

class CardDetails(models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE)
    accountname = models.CharField(max_length=100)
    cvv = models.IntegerField()
    expiry_date = models.DateField()