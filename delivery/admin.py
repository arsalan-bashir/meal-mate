from django.contrib import admin
from .models import Customer, Restaurant, Menu, Cart

# Register your models here.
admin.site.register(Customer)
admin.site.register(Restaurant)
admin.site.register(Menu)
admin.site.register(Cart)
