from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser,BaseUserManager
from django.db import models
import datetime
from django.utils.text import slugify

class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, is_superuser=False, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.username = email
        user.set_password(password)
        user.is_staff = is_superuser
        user.is_superuser = is_superuser
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        return self.create_user(email, password, is_superuser=True, **extra_fields)


class BaseModel(models.Model):
    """
    model for saving common fields .
    """

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True
        ordering = ["-created_on"]


class CustomUser(AbstractUser):
    userchoices = (
        (1, "ADMIN"),
        (2, "CUSTOMER")

    )
    USERNAME_FIELD = "email"
    objects = UserManager()
    REQUIRED_FIELDS = ["phone"]
    usertype = models.IntegerField(default=0, choices=userchoices)
    name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(null=True, blank=True, unique=True)
    city = models.CharField(max_length=500, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.username

class Category(BaseModel):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    icon = models.ImageField(upload_to='category',null=True, blank=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:  # If there's no slug (new or being reset)
            self.slug = slugify(self.name)
            original_slug = self.slug
            count = 1
            while Category.objects.filter(slug=self.slug).exists():
                self.slug = f'{original_slug}-{count}'  # Append a number until unique
                count += 1
        super().save(*args, **kwargs)

class Tag(BaseModel):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Product(BaseModel):
    UNITCHOICES = (
        (1, "KB"),
        (2, "MB"),
        (3, "GB"),
        (4, "TB"),
    )
    category = models.ForeignKey(Category, related_name='products_category', on_delete=models.SET_NULL,null=True,blank=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    product_code = models.CharField(max_length=255)
    product_size = models.DecimalField( max_digits=10, decimal_places=2)
    download_link = models.URLField(max_length=200, blank=True,null=True) 
    product_unit = models.IntegerField(choices=UNITCHOICES,null=True,blank=True)
    tag = models.ForeignKey(Tag, related_name='products_tag', on_delete=models.SET_NULL,null=True,blank=True)
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        creating = self._state.adding  
        if creating:
            super(Product, self).save(*args, **kwargs) 
        if not self.product_code:
            self.product_code = f"P-{self.id}"
        super(Product, self).save(*args, **kwargs)


class ProductImages(BaseModel):
    image = models.ImageField(upload_to='productSale',null=True,blank=True)
    product = models.ForeignKey("ProductSale",related_name="products_images",null=True,on_delete=models.SET_NULL,blank=True)

class ProductVideos(BaseModel):
    video = models.FileField(upload_to='products_videos',null=True,blank=True)
    product = models.ForeignKey("ProductSale",related_name="productssale_videos",null=True,on_delete=models.SET_NULL,blank=True)

class Banner(BaseModel):
    image = models.ImageField(upload_to='banner_image',null=True,blank=True)
    banner_head = models.CharField(max_length=255,null=True,blank=True)

class ProductSale(BaseModel):
    sale_id = models.CharField(max_length=255,null=True,blank=True)
    product = models.ForeignKey(Product, related_name='products_sale', on_delete=models.SET_NULL,null=True,blank=True)
    name = models.CharField(max_length=255,null=True)   
    slug = models.SlugField(max_length=255,null=False,unique=True)
    description = models.TextField(blank=True, null=True)
    caption = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2,default=0.00)
    discount = models.DecimalField(max_digits=10, decimal_places=2,default=0.00)
    thumbnail = models.ImageField(upload_to='products_thumbnail',null=True,blank=True)
    available = models.BooleanField(default=True)


    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        creating = self._state.adding  
        if creating:
            if not self.slug:  # If there's no slug (new or being reset)
                self.slug = slugify(self.name)
                original_slug = self.slug
                count = 1
                while ProductSale.objects.filter(slug=self.slug).exists():
                    self.slug = f'{original_slug}-{count}'  # Append a number until unique
                    count += 1
            super(ProductSale, self).save(*args, **kwargs) 
        if not self.sale_id:
            self.sale_id = f"SALE-{self.id}"
        super(ProductSale, self).save(*args, **kwargs)

class ProductSaleItems(BaseModel):
    product = models.ForeignKey(Product, related_name='products_saleitem', on_delete=models.SET_NULL,null=True,blank=True)
    sale_master = models.ForeignKey(ProductSale, related_name='products_salemaster', on_delete=models.SET_NULL,null=True,blank=True)
  

    def __str__(self):
        return self.name
    
class Order(BaseModel):
    PAYMENT_TYPE = (
        (1, "Online"),
        (2, "Paypal"),
    )

    ORDER_STATUS = (
        (1, "Pending"),
        (2, "Completed"),
        (2, "Failed"),

    )
    user = models.ForeignKey(CustomUser, related_name='orders',  on_delete=models.SET_NULL,null=True,blank=True)
    promocode = models.ForeignKey("PromoCode",related_name='order_promocode',on_delete=models.SET_NULL,null=True,blank=True)
    paid = models.BooleanField(default=False)
    tax = models.DecimalField(max_digits=10,decimal_places=2,default=0.00)
    discount = models.DecimalField(max_digits=10,decimal_places=2,default=0.00)
    total_price = models.DecimalField(max_digits=10,decimal_places=2,default=0.00)
    payment_method = models.IntegerField(choices=PAYMENT_TYPE,null=True,blank=True)
    order_status = models.IntegerField(choices=ORDER_STATUS,null=True,blank=True,default=1)
    order_id  = models.CharField(max_length=255,null=False,unique=True)


    def __str__(self):
        return f'Order {self.id}'
    
    def save(self, *args, **kwargs):
        creating = self._state.adding  
        if creating:
            super(Order, self).save(*args, **kwargs) 
        if not self.order_id:
            self.order_id = f"ORDER-{self.id}"
        super(Order, self).save(*args, **kwargs)

class OrderItem(BaseModel):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(ProductSale, related_name='order_items', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2,default=0.00)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return str(self.id)

class Payment(BaseModel):
    PAYMENT_STATUS = (
        (0, "Failed"),
        (1, "Pending"),
        (2, "Completed"),
    )
    order = models.OneToOneField(Order, related_name='payment', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=255)
    payment_method = models.CharField(max_length=50)  # E.g., 'PayPal', 'Credit card', 'Stripe'
    status = models.CharField(max_length=50,choices=PAYMENT_STATUS,default=1)  # E.g., 'Pending', 'Completed', 'Failed'

    def __str__(self):
        return f'Payment {self.transaction_id} for Order {self.order_id}'

class Cart(BaseModel):
    user = models.ForeignKey(CustomUser, related_name='cart', on_delete=models.SET_NULL,null=True,blank=True)
    cart_total = models.DecimalField(max_digits=10,decimal_places=2,default=0.00)

    def __str__(self):
        return f'Cart {self.id}'

class CartItem(BaseModel):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(ProductSale, related_name='cart_items', on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return str(self.id)


class PromoCode(BaseModel):
    code = models.CharField(max_length=50, unique=True)
    active = models.BooleanField(default=True)
    discount_value = models.DecimalField(max_digits=6, decimal_places=2,default=0.00)
    valid_from = models.DateTimeField(null=True,blank=True)
    valid_to = models.DateTimeField(null=True,blank=True)
    minimum_order_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    usage_limit = models.IntegerField(help_text="How many times this promo code can be used in total", null=True, blank=True,default=1)
    used = models.IntegerField(default=0)  # Counter for how many times the promo code has been used

    def is_valid(self):
        return (
            self.active and
            self.used < (self.usage_limit or float('inf')) and
            self.valid_from <= datetime.datetime.now() <= self.valid_to
        )

    def __str__(self):
        return self.code