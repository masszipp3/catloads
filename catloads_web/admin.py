from django.contrib import admin
from .models import CustomUser,CartItem,Cart,OrderItem,Order,Product,ProductImages,ProductVideos,Category,ProductSale,ProductSaleItems,Country,CountryPrice

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(OrderItem)
admin.site.register(Order)
admin.site.register(ProductVideos)
admin.site.register(ProductImages)
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(CountryPrice)
admin.site.register(Country)









