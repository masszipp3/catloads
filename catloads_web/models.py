from django.db import models
from django.utils import timezone
import math
# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser,BaseUserManager
from django.db import models
import datetime
from django.db.models import F, Sum
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field

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

class Country(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)  
    symbol = models.CharField(max_length=10, default="$")
    default=models.BooleanField(default=False)

    def __str__(self):
        return self.name
    
    @staticmethod
    def get_default_country(): 
        return Country.objects.filter(default=True).first()


class CustomUser(AbstractUser):
    userchoices = (
        (1, "ADMIN"),
        (2, "CUSTOMER")

    )
    USERNAME_FIELD = "email"
    objects = UserManager()
    REQUIRED_FIELDS = ["phone"]
    usertype = models.IntegerField(default=2, choices=userchoices)
    name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(null=True, blank=True, unique=True)
    city = models.CharField(max_length=500, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True,null=True)
    updated_on = models.DateTimeField(auto_now=True,null=True)

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
    
    def get_unit_display(self):
        return dict(self.UNITCHOICES)[self.product_unit]  
    
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
    upload_order = models.IntegerField(default=0)

class ProductVideos(BaseModel):
    video = models.FileField(upload_to='products_videos',null=True,blank=True)
    product = models.ForeignKey("ProductSale",related_name="productssale_videos",null=True,on_delete=models.SET_NULL,blank=True)
    upload_order = models.IntegerField(default=0)

class Banner(BaseModel):
    image = models.ImageField(upload_to='banner_image',null=True,blank=True)
    banner_head = models.CharField(max_length=255,null=True,blank=True)

class ProductSale(BaseModel):
    sale_id = models.CharField(max_length=255,null=True,blank=True)
    product = models.ForeignKey(Product, related_name='products_sale', on_delete=models.SET_NULL,null=True,blank=True)
    name = models.CharField(max_length=255,null=True)   
    rating = models.DecimalField(max_digits=10,decimal_places=1,null=True,default=0)   
    slug = models.SlugField(max_length=255,null=False,unique=True)
    description = CKEditor5Field('Text',blank=True, null=True)
    sale_tag = models.CharField(max_length=255,default='LIMITED SALE')
    sale_tag_color = models.CharField(max_length=255,null=True,default='#FF0000')
    caption = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2,default=0.00)
    discount = models.DecimalField(max_digits=10, decimal_places=2,default=0.00)
    countries = models.ManyToManyField(
        Country, related_name="product_countries", through="CountryPrice"
    )
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

    def get_all_categories(self):
        sale_items = ProductSaleItems.objects.filter(sale_master=self)
        return sale_items.values_list('product__category__name', flat=True).distinct()

    def get_discount_percentage(self,country_id=None):
        default_country = Country.get_default_country()
        country_discount = self.country_sale_prices.filter(country_id=country_id).first() if country_id else  self.country_sale_prices.filter(country=default_country).first()
        if country_discount and country_discount.price >0:
            discount_amount= (country_discount.discount / (country_discount.discount+country_discount.price))* 100
            return math.floor(discount_amount)
        return 0
    
    def get_maxprice(self,country_id=None):
        default_country = Country.get_default_country()
        country_discount = self.country_sale_prices.filter(country_id=country_id).first() if country_id else  self.country_sale_prices.filter(country=default_country).first() 
        return country_discount.discount + country_discount.price if country_discount.discount > 0 else country_discount.discount
    
    def get_price_and_discount(self,country_id=None):
        try:
            if not country_id:
                country_price = self.country_sale_prices.first() 
            else:
                country_price = self.country_sale_prices.filter(country_id=country_id).first()
            if country_price is None:
                raise Exception("Country error")      
            return {
                'price': country_price.price,
                'discount': country_price.discount,
                'symbol':country_price.country.discount
            }
        except:
            default_country = Country.get_default_country()
            country_price = self.country_sale_prices.filter(country=default_country).first()
            return {
                'price': country_price.price or self.price,
                'discount': country_price.discount or self.discount,
                'symbol': Country.get_default_country().symbol or '$'
            }

class ProductSaleItems(BaseModel):
    product = models.ForeignKey(Product, related_name='products_saleitem', on_delete=models.SET_NULL,null=True,blank=True)
    sale_master = models.ForeignKey(ProductSale, related_name='products_salemaster', on_delete=models.SET_NULL,null=True,blank=True)
  

    def __str__(self):
        return self.name

class CountryPrice(BaseModel):
    product = models.ForeignKey(Product, related_name='product_country', on_delete=models.CASCADE, null=True, blank=True)
    product_sale = models.ForeignKey(ProductSale, related_name='country_sale_prices', on_delete=models.CASCADE, null=True, blank=True)
    country = models.ForeignKey(Country, related_name='country_prices', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2,default=0.00)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        unique_together = ('product', 'country') 

class Order(BaseModel):
    PAYMENT_TYPE = (
        (1, "Online"),
        (2, "Paypal"),
    )

    ORDER_STATUS = (
        (1, "Pending"),
        (2, "Completed"),
        (3, "Failed"),

    )
    user = models.ForeignKey(CustomUser, related_name='orders',  on_delete=models.SET_NULL,null=True,blank=True)
    promocode = models.ForeignKey("PromoCode",related_name='order_promocode',on_delete=models.SET_NULL,null=True,blank=True)
    paid = models.BooleanField(default=False)
    tax = models.DecimalField(max_digits=10,decimal_places=2,default=0.00)
    discount = models.DecimalField(max_digits=10,decimal_places=2,default=0.00)
    total_price = models.DecimalField(max_digits=10,decimal_places=2,default=0.00)
    payment_method = models.IntegerField(choices=PAYMENT_TYPE,null=True,blank=True,default=1)
    order_status = models.IntegerField(choices=ORDER_STATUS,null=True,blank=True,default=1)
    order_id  = models.CharField(max_length=255,null=True)
    razorpay_id = models.CharField(max_length=200,null=True,blank=True)
    country = models.ForeignKey(Country,on_delete=models.SET_NULL,null=True,blank=True)


    def get_order_total(self):
        return (
            self.items.annotate(
                total_item=F('quantity') * F('price')
            ).aggregate(total=Sum('total_item'))['total']
            or 0.00 

        )

    def get_status_display(self):
        return dict(self.ORDER_STATUS)[self.order_status]  
    
    def get_orderitemcount(self):
        return self.items.count()
    
    def get_order_discount(self):
        order_total = self.items.annotate(
                total_item=F('quantity') * F('price')
            ).aggregate(total=Sum('total_item'))['total'] or 0.00
        order_discount = self.items.aggregate(total=Sum('product__discount'))['total'] or 0.00
        return (
            order_total-order_discount
        )

    def __str__(self):
        return f'Order {self.id}'
    
    
    def save(self, *args, **kwargs):
        self.order_id = f"ORDER-{self.id}"
        super(Order, self).save(*args, **kwargs)

class OrderItem(BaseModel):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(ProductSale, related_name='order_items', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2,default=0.00)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return str(self.id)
    
    def get_subtotal(self):
        return self.price * self.quantity

class Payment(BaseModel):
    PAYMENT_STATUS = (
        (0, "Failed"),
        (1, "Pending"),
        (2, "Completed"),
    )
    order = models.ForeignKey(Order, related_name='payment', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2,default=0.00)
    reason = models.TextField(max_length=255,null=True)
    transaction_id = models.CharField(max_length=255,null=True)
    signature = models.CharField(max_length=255,null=True)
    payment_method = models.CharField(max_length=50,null=True)  # E.g., 'PayPal', 'Credit card', 'Stripe'
    status = models.CharField(max_length=50,choices=PAYMENT_STATUS,default=1)  # E.g., 'Pending', 'Completed', 'Failed'

    def __str__(self):
        return f'Payment {self.transaction_id} for Order {self.order_id}'

class Cart(BaseModel):
    user = models.ForeignKey(CustomUser, related_name='cart', on_delete=models.SET_NULL,null=True,blank=True)
    cart_total = models.DecimalField(max_digits=10,decimal_places=2,default=0.00)
    country = models.ForeignKey(Country,on_delete=models.SET_NULL,null=True,blank=True)


    def __str__(self):
        return f'Cart {self.id}'
    
    def update_and_get_cart_total(self):
        self.cart_total = self.items.annotate(
            total_item=F('quantity') * F('product__price')
        ).aggregate(total=Sum('total_item'))['total'] or 0.00
        self.save()
        return self.cart_total
class CartItem(BaseModel):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(ProductSale, related_name='cart_items', on_delete=models.CASCADE)
    price =  models.DecimalField(max_digits=10, decimal_places=2,default=0.00)
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
        current_time = timezone.now() # This ensures the datetime is timezone-aware
        print(current_time)
        if not self.active:
            return False
        if self.used >= (self.usage_limit or float('inf')):
            return False
        if self.valid_from and self.valid_from > current_time:
            return False
        if self.valid_to and self.valid_to < current_time:
            return False
        return True

    def __str__(self):
        return self.code