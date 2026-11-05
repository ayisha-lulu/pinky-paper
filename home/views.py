from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from .models import Product
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.contrib import messages
from.models import Order, OrderItem,Wishlist


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect('dashboard')

        else:
            return HttpResponse("Invalid username or password")

    return render(request, 'home/index.html')

def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            return HttpResponse("Username already exists!")

        if len(password) < 8:
            return HttpResponse("password must be at least 8 characters !")

        User.objects.create_user(
            username=username,
            password=password
        )

        return redirect("home")

    return render(request, 'home/register.html')

@login_required
def edit_profile(request):
    if request.method == 'POST':

        username = request.POST.get('username', '').strip()

        if not username:
            messages.error(request, 'Username cannot be empty!')
            return redirect('edit_profile')

        if User.objects.exclude(id=request.user.id).filter(username=username).exists():
            messages.error(request, 'Username already taken!')
            return redirect('edit_profile')

        request.user.username = username
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.email = request.POST.get('email', '')

        request.user.save()

        messages.success(request, 'Profile updated successfully!')
        return redirect('dashboard')

    return render(request, 'home/edit_profile.html')


def dashboard(request):
    cart = request.session.get('cart', {})

    cart_count = sum(cart.values())

    recent_orders = Order.objects.filter(
        customer=request.user
    ).order_by('-created_at')[:5]

    order_count = Order.objects.filter(
        customer=request.user
    ).count()

    context = {
        'cart_count': cart_count,
        'order_count': order_count,
        'wishlist_count': Wishlist.objects.filter(customer=request.user).count(),

        'recent_orders': recent_orders,
    }

    return render(request, 'home/dashboard.html', context)

@require_POST
def user_logout(request):
    logout(request)
    return redirect('home')

from .models import Product



    
def store_home(request):
    search_query = request.GET.get('q', '')
    category = request.GET.get('category', '')

    products = Product.objects.all()

    if search_query:
        products = products.filter(name__icontains=search_query)

    if category:
        products = products.filter(category__iexact=category)

    return render(
        request,
        'home/store.html',
        {
            'products': products,
            'search_query': search_query,
            'selected_category': category
        }
    )
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    return render(
        request,
        'home/product_detail.html',
        {'product': product}
    )
def add_to_cart(request, product_id):
    if request.method == "POST":
        product = get_object_or_404(Product, id=product_id)

        cart = request.session.get('cart', {})
        product_id = str(product.id)

        if product.stock > 0:
            current_quantity = cart.get(product_id, 0)

            if current_quantity < product.stock:
                cart[product_id] = current_quantity + 1
                request.session['cart'] = cart
                messages.success(request, "Product added to cart!")

    return redirect('home')
def cart_view(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0

    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)
        subtotal = product.price * quantity
        total += subtotal

        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal
        })

    return render(request, 'home/cart.html', {
        'cart_items': cart_items,
        'total': total
    })

@require_POST
def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})

    product_id = str(product_id)

    if product_id in cart:
        del cart[product_id]
        request.session['cart'] = cart

    return redirect('cart')

@require_POST
def update_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id = str(product_id)

    try:
        quantity = int(request.POST.get('quantity', 1))
    except ValueError:
        quantity = 1

    product = get_object_or_404(Product, id=product_id)

    if quantity <= 0:
        cart.pop(product_id, None)
    elif quantity <= product.stock:
        cart[product_id] = quantity

    request.session['cart'] = cart
    return redirect('cart')

@login_required
@require_POST
def place_order(request):
    cart = request.session.get('cart', {})

    if not cart:
        return redirect('cart')

    total = 0
    products = []

    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)

        if quantity < 1 or quantity > product.stock:
            messages.error(request, "Product stock is not available.")
            return redirect('cart')

        total += product.price * quantity
        products.append((product, quantity))

    order = Order.objects.create(
        customer=request.user,
        total_amount=total
    )

    for product, quantity in products:
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price=product.price
        )

        product.stock -= quantity
        product.save()

    request.session['cart'] = {}
    messages.success(request, "Your order was placed successfully!")

    return redirect('dashboard')

@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    Wishlist.objects.get_or_create(
        customer=request.user,
        product=product
    )

    messages.success(request, "Added to your wishlist! ♡")
    return redirect('home')

@login_required
def wishlist_view(request):
    wishlist_items = Wishlist.objects.filter(
        customer=request.user
    ).select_related('product')

    return render(request, 'home/wishlist.html', {
        'wishlist_items': wishlist_items
    })

@login_required
@require_POST
def remove_from_wishlist(request, item_id):
    item = get_object_or_404(
        Wishlist,
        id=item_id,
        customer=request.user
    )
    item.delete()
    messages.success(request, "Removed from your wishlist!")
    return redirect('wishlist')

@login_required
def order_history(request):
    orders = Order.objects.filter(
        customer=request.user
    ).order_by('-created_at')

    return render(request, 'home/order_history.html', {
        'orders': orders
    })

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        customer=request.user
    )

    return render(request, 'home/order_detail.html', {
        'order': order
    })

@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0

    if not cart:
        messages.warning(request, "Your cart is empty!")
        return redirect('cart')

    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)

        if quantity < 1 or quantity > product.stock:
            messages.error(request, "Product stock is not available.")
            return redirect('cart')

        subtotal = product.price * quantity
        total += subtotal

        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal
        })

    if request.method == "POST":
        full_name = request.POST.get('full_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        pincode = request.POST.get('pincode', '').strip()
        payment_method = request.POST.get('payment_method', '')

        if not all([full_name, phone, address, pincode]):
            messages.error(request, "Please fill all delivery details.")
        elif not phone.isdigit() or len(phone) != 10:
            messages.error(request, "Enter a valid 10-digit phone number.")
        elif not pincode.isdigit() or len(pincode) != 6:
            messages.error(request, "Enter a valid 6-digit pincode.")
        elif payment_method not in ['COD', 'ONLINE']:
            messages.error(request, "Please select a payment method.")
        else:
            order = Order.objects.create(
                customer=request.user,
                total_amount=total,
                full_name=full_name,
                phone=phone,
                address=address,
                pincode=pincode,
                payment_method=payment_method,
                payment_status='PENDING'
            )

            for item in cart_items:
                product = item['product']
                quantity = item['quantity']

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=product.price
                )

                product.stock -= quantity
                product.save()

            request.session['cart'] = {}

            if payment_method == 'COD':
                messages.success(request, "Your COD order was placed successfully!")
                return redirect('order_detail', order_id=order.id)

            messages.info(
                request,
                "Online payment is not connected yet. Your order is pending payment."
            )
            return redirect('order_detail', order_id=order.id)

    return render(request, 'home/checkout.html', {
        'cart_items': cart_items,
        'total': total
    })