from django.db import models

# Create your models here.


class Customer(models.Model):

    name = models.CharField(max_length=20)
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=20)
    role = models.CharField(max_length=20)
    email = models.EmailField(max_length=100)
    address = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    
    def __str__(self):
        return f"{self.name} | {self.username} | {self.password} | {self.role} | {self.email} | {self.address} | {self.phone}"
    
    
class Restaurant(models.Model):
    name = models.CharField(max_length=20)
    address = models.CharField(max_length=100)
    phone = models.CharField(max_length=13)
    picture = models.URLField(max_length=200)
    cuisine = models.CharField(max_length=200)
    rating = models.FloatField()
    
    def __str__(self):
        return f"{self.name} | {self.address} | {self.phone} | {self.cuisine} | {self.rating}"


class Menu(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menu')
    name = models.CharField(max_length=20)
    picture = models.URLField(max_length=200)
    description = models.CharField(max_length=200)
    price = models.FloatField()
    type = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.name} | {self.price} | {self.type} | {self.description}"


class Cart(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='cart')
    items = models.ManyToManyField(Menu, through="CartItem", related_name='carts')

    def add_item(self, menu_item):
        cart_item, created = CartItem.objects.get_or_create(cart=self, item=menu_item)
        if not created:
            cart_item.quantity += 1
        cart_item.save()

    def clear_cart(self):
        try:
            self.cartitem_set.all().delete()
        except CartItem.DoesNotExist:
            pass

    def update_item(self, menu_item, quantity):
        cart_item = CartItem.objects.get(cart=self, item=menu_item)

        # Decrease Quantity
        if quantity == 0:
            try:
                    if cart_item.quantity > 1:
                        cart_item.quantity -= 1
                        cart_item.save()
                    else:
                        cart_item.delete()

            except CartItem.DoesNotExist:
                pass
        elif quantity == 1:
            cart_item.quantity += 1
            cart_item.save()

    def total_price(self):
        return sum(cart_item.item_total() for cart_item in self.cartitem_set.all())

    def additional_charges(self):
        return self.total_price() * 0.05

    def grand_total(self):
        return self.additional_charges() + self.total_price() + 10

    def __str__(self):
        return f"{self.customer.name} | {self.items.count()} | {self.total_price()}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    item = models.ForeignKey(Menu, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def item_total(self):
        return self.quantity * self.item.price

    def __str__(self):
        return f"{self.item.name} | {self.item.restaurant.name} | {self.quantity} | {self.item.price}"


