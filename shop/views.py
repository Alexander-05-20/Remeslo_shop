from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Sum
from django.urls import reverse
from functools import wraps
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import transaction

from .models import Product, CartItem, Order, OrderItem  # Импорт моделей
from .forms import SignUpForm

# Вспомогательные функции

def decrease_stock(product, quantity):
    """Уменьшает запас продукта, если хватает."""
    if product.stock < quantity:
        raise ValueError('Недостаточно товара на складе')
    product.stock -= quantity
    product.save()

def add_product_to_cart(user, product, quantity):
    """Добавляет товар в корзину, уменьшая запас продукта."""
    try:
        decrease_stock(product, quantity)
        cart_item, created = CartItem.objects.get_or_create(user=user, product=product)
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()
    except ValueError as e:
        raise e

# Страницы сайта

def home(request):
    products = Product.objects.all()
    return render(request, 'shop/home.html', {'products': products})

def about(request):
    return render(request, 'shop/about.html')

def contacts(request):
    return render(request, 'shop/contacts.html')

def login_view(request):
    if request.method == 'POST':
        login_input = request.POST.get('username')
        password = request.POST.get('password')

        # Проверка, содержит ли ввод '@' — предполагаем, что это email
        if '@' in login_input:
            try:
                user_obj = User.objects.get(email=login_input)
                username = user_obj.username
            except User.DoesNotExist:
                username = None
        else:
            username = login_input

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль.')
    return render(request, 'shop/login.html')

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'shop/signup.html', {'form': form})

@login_required
def cart(request):
    items = CartItem.objects.filter(user=request.user)
    total = sum(item.product.price * item.quantity for item in items)
    return render(request, 'shop/cart.html', {'items': items, 'total': total})

def cart_view(request):
    cart = request.session.get('cart', {})
    products = []
    total_price = 0
    for product_id, qty in cart.items():
        product = get_object_or_404(Product, id=product_id)
        products.append({
            'product': product,
            'quantity': qty,
            'total_price': product.price * qty,
        })
        total_price += product.price * qty
    return render(request, 'shop/cart.html', {'products': products, 'total_price': total_price})

@login_required
@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        cart[str(product_id)] += 1
    else:
        cart[str(product_id)] = 1
    request.session['cart'] = cart

    response_data = {
        'success': True,
        'product': {
            'id': product.id,
            'name': product.name,
            'price': str(product.price),
            'image_url': product.images.first().image.url if product.images.exists() else '',
            'hover_image_url': '',  # Тут можно добавить, если есть
            'detail_url': reverse('product_detail', args=[product.id]),
            'cart_url': reverse('add_to_cart', args=[product.id]),
        }
    }
    return JsonResponse(response_data)

@login_required
def clear_cart(request):
    if request.method == 'POST':
        cart_items = CartItem.objects.filter(user=request.user).select_related('product')
        for item in cart_items:
            product = item.product
            product.stock += item.quantity
            product.save()
        cart_items.delete()
        return JsonResponse({'success': True, 'total_items': 0})
    return JsonResponse({'success': False, 'error': 'Invalid method'}, status=400)

def ajax_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'Пожалуйста, войдите в аккаунт'}, status=401)
        return view_func(request, *args, **kwargs)
    return wrapper

@require_POST
@ajax_login_required
def add_to_cart_ajax(request, product_id):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Пожалуйста, войдите или зарегистрируйтесь, чтобы добавить товар в корзину.'})

    product = get_object_or_404(Product, id=product_id)
    item, created = CartItem.objects.get_or_create(user=request.user, product=product)

    if not created:
        item.quantity += 1
        item.save()

    total_items = CartItem.objects.filter(user=request.user).aggregate(total_qty=Sum('quantity'))['total_qty'] or 0

    return JsonResponse({
        'success': True,
        'product_name': product.name,
        'cart_total_items': total_items,
    })

@login_required
def remove_one_from_cart(request, product_id):
    if request.method == 'POST':
        item = get_object_or_404(CartItem, user=request.user, product_id=product_id)
        product = item.product

        if item.quantity > 1:
            item.quantity -= 1
            item.save()
        else:
            item.delete()

        product.stock += 1
        product.save()
    return redirect('cart')

def product_list(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(available=True)
    if query:
        products = products.filter(name__icontains=query)
    return render(request, 'shop/product_list.html', {
        'products': products,
        'query': query,
    })

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'shop/product_detail.html', {'product': product})

@login_required
def buy_product(request, product_id):
    if request.method == 'POST':
        item = get_object_or_404(CartItem, user=request.user, product_id=product_id)
        product = item.product

        try:
            requested_quantity = int(request.POST.get('quantity', item.quantity))
        except (ValueError, TypeError):
            requested_quantity = item.quantity

        requested_quantity = min(requested_quantity, item.quantity)

        if product.stock < requested_quantity:
            messages.error(request, f"На складе недостаточно товара (осталось: {product.stock})")
            return redirect('cart')

        if requested_quantity >= item.quantity:
            item.delete()
        else:
            item.quantity -= requested_quantity
            item.save()

        product.stock -= requested_quantity
        product.save()

        messages.success(request, f"Вы приобрели {requested_quantity} шт. '{product.name}'.")
        return redirect('cart')

@login_required
def create_order(request):
    cart_items = CartItem.objects.filter(user=request.user)
    if not cart_items:
        messages.error(request, "Ваша корзина пуста.")
        return redirect('cart')
    
    total_price = sum(item.product.price * item.quantity for item in cart_items)

    with transaction.atomic():
        order = Order.objects.create(user=request.user, total_price=total_price)
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price_at_purchase=item.product.price
            )
        # После создания заказа, очищаем корзину
        cart_items.delete()

    messages.success(request, f"Ваш заказ #{order.id} успешно оформлен!")
    return redirect('order_detail', order_id=order.id)
# @login_required
# def user_orders(request):
#     orders = Order.objects.filter(user=request.user).prefetch_related('items__product')
#     return render(request, 'shop/user_orders.html', {'orders': orders})