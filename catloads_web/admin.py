from django.contrib import admin
from .models import CustomUser,CartItem,Cart,OrderItem,Order

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(OrderItem)
admin.site.register(Order)



