import os
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponse
from razorpay.resources import item

from delivery.models import Customer, Restaurant, Menu, Cart
import cloudinary
import cloudinary.uploader
import razorpay

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
    )



# Create your views here.
def index(request):
    return render(request, 'delivery/index.html')

def user_index(request):
    return render(request, 'delivery/user-index.html')

def handle_signup(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        if Customer.objects.filter(username = username).exists():
            return render(request, 
                          'delivery/user-index.html', 
                          {'signup_error': 'Username already exists!!'})
        else:
            customer = Customer(name=name, username=username, password=password,
                                role="user", email=email, address=address, phone=phone)
            customer.save()
            return render(request, 'delivery/user-index.html')
    else:
        return HttpResponse("Invalid request")

def handle_signin(request):
    if request.method == 'POST':
        
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            cust = Customer.objects.get(username = username)
            if cust.password == password:
                request.session['customer_id'] = cust.id
                request.session['customer_name'] = cust.name
                if cust.role == 'admin':
                    return redirect('res_dashboard')
                elif cust.role == 'user':
                    cart, created = Cart.objects.get_or_create(customer=cust)
                    return redirect('user_dashboard')
            else:
                return render(request, 'delivery/user-index.html', 
                              {'signin_error': 'Wrong Password!!'})
        except Exception as e:
            print(e)
            return render(request, 'delivery/user-index.html', 
                          {'signin_error': "User doesn't Exist!!"})
            
    else:
        return HttpResponse("Invalid request")


def logout(request):
    request.session.flush()
    return redirect('user_index')
        
    
def res_dashboard(request):
    customer_name = request.session.get('customer_name')
    if not customer_name:
        return redirect('user_index')
    return render(request, 'delivery/res-dashboard.html', {'cus_name': customer_name})
    
def add_restaurant_page(request):
    if not request.session.get('customer_id'):
        return redirect('user_index')
    customer_name = request.session.get('customer_name')
    return render(request, 'delivery/add-restaurant.html',{'cus_name':customer_name})


def handle_add_restaurant(request):
    if request.method == 'POST':
        name = request.POST.get('restaurant-name')
        address = request.POST.get('restaurant-address')
        phone = request.POST.get('restaurant-phone')
        picture = request.FILES.get('restaurant-photo')
        cuisine = request.POST.get('restaurant-cuisine')
        rating = request.POST.get('restaurant-rating')
        try:
            upload_picture = cloudinary.uploader.upload(
                picture,
                folder="mealmate/restaurants/",
                public_id=name,
                )
            res = Restaurant(name=name, address=address, phone=phone,
                             picture=upload_picture.get("url"),
                             cuisine=cuisine, rating=rating)
            res.save()

        except Exception as e:
            messages.error(request, f"Failed to add the restaurant: {e}")
            return redirect('add_restaurant_page')

        restaurants = Restaurant.objects.all()
        return redirect('show_restaurants')
    else:
        messages.error(request, "Invalid Request")
        return redirect('add_restaurant_page')
    
def show_restaurants(request):
    if not request.session.get('customer_id'):
        return redirect('user_index')
    customer_name = request.session.get('customer_name')
    restaurants = Restaurant.objects.all()
    return render(request, 'delivery/restaurant-list.html',
                  {"restaurants" : restaurants,
                            'cus_name':customer_name,
                            })


def restaurant_menu(request, restaurant_id):
    if not request.session.get('customer_id'):
        return redirect('user_index')
    customer_name = request.session.get('customer_name')
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    menu = Menu.objects.filter(restaurant = restaurant)

    
    return render(request, 'delivery/menu.html',
                  {'restaurant': restaurant,
                            'menu': menu,
                            'cus_name': customer_name,
                        })


def add_item_page(request, restaurant_id):
    if not request.session.get('customer_id'):
        return redirect('user_index')
    customer_name = request.session.get('customer_name')
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    return render(request, 'delivery/add-item.html',
                  {'restaurant': restaurant,
                   'cus_name': customer_name,
                   })


def handle_add_item(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)

    if request.method == 'POST':
        name = request.POST.get('item-name')
        price = request.POST.get('item-price')
        description = request.POST.get('item-description')
        type = request.POST.get('item-type')
        picture = request.FILES.get('item-photo')
        try:
            upload_picture = cloudinary.uploader.upload(
                picture,
                folder="mealmate/menuitems/",
                public_id=name
                )
            menu = Menu(restaurant=restaurant, name=name, price=price, type=type,
                        description=description, picture=upload_picture.get("url"))
            menu.save()
        except Exception as e:
            messages.error(request, f"Failed to update the restaurant: {e}")
            return redirect('add_item_page', restaurant_id = restaurant.id)

        return redirect('restaurant_menu', restaurant_id = restaurant.id)
    else:
        messages.error(request, "Invalid Request")
        return redirect('add_item_page', restaurant_id = restaurant.id)


def update_restaurants(request):
    if not request.session.get("customer_id"):
        return redirect('user_index')

    customer_name = request.session.get("customer_name")
    restaurants = Restaurant.objects.all()
    return render(request, 'delivery/update-restaurants.html',
                  {"restaurants": restaurants, 'cus_name': customer_name,
                   })


def edit_restaurant(request, restaurant_id):
    if not request.session.get('customer_id'):
        return redirect('user_index')

    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    customer_name = request.session.get('customer_name')

    return render(request, 'delivery/edit-restaurant.html',{
        'restaurant': restaurant,
        'cus_name': customer_name
    })


def handle_edit_restaurant(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)

    if request.method == 'POST':
        restaurant.name = request.POST.get("restaurant-name")
        restaurant.address = request.POST.get('restaurant-address')
        restaurant.phone = request.POST.get('restaurant-phone')
        restaurant.cuisine = request.POST.get('restaurant-cuisine')
        restaurant.rating = request.POST.get('restaurant-rating')
        if not request.POST.get('restaurant-photo'):
            pass
        else:
            restaurant.picture = request.FILES.get('restaurant-photo')

        try:
            upload_picture = cloudinary.uploader.upload(
                restaurant.picture,
                folder="mealmate/restaurants/",
                public_id=restaurant.name,
            )
            restaurant.save()

            return redirect('update_restaurants')
        except Exception as e:
            messages.error(request, f"Failed to update the restaurant: {e}")
            return redirect('edit_restaurant', restaurant_id = restaurant.id)

    else:
        messages.error(request, "Invalid Request")
        return redirect('edit_restaurant', restaurant_id = restaurant.id)


def update_menu(request, restaurant_id):
    if not request.session.get('customer_id'):
        return redirect('user_index')

    customer_name = request.session.get('customer_name')
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    menu = Menu.objects.filter(restaurant=restaurant)

    return render(request, 'delivery/update-menu.html',
                  {'restaurant': restaurant,
                   'menu': menu,
                   'cus_name': customer_name,
                   })


def delete_restaurant(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    restaurant.delete()

    return redirect('update_restaurants')


def delete_item(request, menu_id):
    menu = get_object_or_404(Menu, id=menu_id)
    restaurant = menu.restaurant
    menu.delete()

    return redirect('update_menu', restaurant_id = restaurant.id)


def edit_item(request, menu_id):
    if not request.session.get('customer_id'):
        return redirect('user_index')
    customer_name = request.session.get('customer_name')
    menu = get_object_or_404(Menu, id=menu_id)
    return render(request, 'delivery/edit-item.html',
                  {'menu': menu,
                   'cus_name': customer_name})


def handle_edit_item(request, menu_id):
    menu = get_object_or_404(Menu, id=menu_id)
    restaurant = menu.restaurant
    if request.method == "POST":
        menu.name = request.POST.get('item-name')
        menu.price = request.POST.get('item-price')
        menu.type = request.POST.get('item-type')
        menu.description = request.POST.get('item-description')

        if not request.POST.get('item-photo'):
            pass
        else:
            menu.picture = request.FILES.get('restaurant-photo')

        try:
            upload_picture = cloudinary.uploader.upload(
                menu.picture,
                folder="mealmate/menuitems/",
                public_id=menu.name,
            )
            menu.save()
            return redirect('update_menu', restaurant_id = restaurant.id)
        except Exception as e:
            messages.error(request, f"Failed to update the menu item: {e}")
            return redirect('edit_item', menu_id=menu.id)

    else:
        messages.error("Invalid Request")
        return redirect('edit_item', menu_id=menu.id)


def user_dashboard(request):
    if not request.session.get('customer_id'):
        return redirect('user_index')
    restaurants = Restaurant.objects.all()
    customer_name = request.session.get('customer_name')
    return render(request, 'delivery/user-dashboard.html',
                  { 'cus_name': customer_name })



def view_restaurants(request):
    if not request.session.get('customer_id'):
        return redirect('user_index')

    customer_name = request.session.get('customer_name')
    restaurants = Restaurant.objects.all()

    return render(request, 'delivery/show-restaurants.html', {
        'restaurants': restaurants, 'cus_name': customer_name
    })


def view_menu(request, restaurant_id):
    if not request.session.get('customer_id'):
        return redirect('user_index')

    customer_name = request.session.get('customer_name')
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    menu = Menu.objects.filter(restaurant=restaurant)
    customer = get_object_or_404(Customer, id=request.session.get('customer_id'))
    cart = get_object_or_404(Cart, customer=customer)

    return render(request, 'delivery/show-menu.html', {
        'restaurant': restaurant,
        'menu': menu,
        'cart': cart,
        'cus_name': customer_name })

def open_cart(request):
    if not request.session.get('customer_id'):
        return redirect('user_index')
    customer_name = request.session.get('customer_name')
    customer = get_object_or_404(Customer, id=request.session.get('customer_id'))
    cart = get_object_or_404(Cart, customer=customer)

    return render(request, 'delivery/cart.html',
                  {'cus_name': customer_name,
                   'customer': customer,
                   'cart': cart})

def add_to_cart(request, menu_id):
    if not request.session.get('customer_id'):
        return redirect('user_index')

    customer = get_object_or_404(Customer, id=request.session.get('customer_id'))
    item = get_object_or_404(Menu, id=menu_id)

    cart, _ = Cart.objects.get_or_create(customer=customer)
    cart.add_item(item)

    return redirect('view_menu', restaurant_id = item.restaurant.id)

def update_cart(request, item_id, quantity):
    if not request.session.get('customer_id'):
        return redirect('user_index')

    customer = get_object_or_404(Customer, id=request.session.get('customer_id'))
    cart = get_object_or_404(Cart, customer=customer)
    cart_item = get_object_or_404(Menu, id=item_id)
    cart.update_item(cart_item, quantity)

    return redirect('open_cart')



def checkout(request):
    if not request.session.get('customer_id'):
        return redirect('user_index')

    customer = get_object_or_404(Customer, id=request.session.get('customer_id'))
    cart = get_object_or_404(Cart, customer=customer)
    cart_items = cart.cartitem_set.all()
    if cart:
        items = cart.items.all()
        if items:
            item_price = cart.total_price()
            additional_charges = cart.additional_charges()
            grand_total = item_price + additional_charges
        else:
            item_price = 0
            additional_charges = 0
            grand_total = 0
    else:
        messages.error(request, f"Empty cart")
        return redirect('open_cart')

    client = razorpay.Client(auth=(os.getenv("RAZORPAY_API_KEY"), os.getenv("RAZORPAY_API_SECRET")))

    order_data = {
        'amount': int(grand_total * 100),
        'currency': 'INR',
        'payment_capture': '1',
    }
    order = client.order.create(data=order_data)

    return render(request, 'delivery/checkout.html', {
        'cus_name': customer.name,
        'item_price': item_price,
        'additional_charges': additional_charges,
        'total_price': grand_total,
        'razorpay_key_id': os.getenv("RAZORPAY_API_KEY"),
        'cart_items': cart_items,
        'cart': items,
        'order_id': order['id'],
        'amount': grand_total,
    })

def order(request):
    if not request.session.get('customer_id'):
        return redirect('user_index')

    customer = get_object_or_404(Customer, id=request.session.get('customer_id'))
    cart = get_object_or_404(Cart, customer=customer)

    if cart:
        cart.clear_cart()

    return render(request, 'delivery/order-success.html', {
        'customer': customer})