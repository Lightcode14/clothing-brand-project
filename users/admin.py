from django.contrib import admin
from .models import CartItem,OrderItem,Order,Profile

admin.site.register(CartItem)

admin.site.register(OrderItem)

admin.site.register(Order)

admin.site.register(Profile)
