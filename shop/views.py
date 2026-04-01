from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, CartItem
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from .forms import SignUpForm
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Sum
import json
from functools import wraps
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.mail import send_mail
import socket
import requests
from decouple import config
from django.db import transaction
from .models import Order, OrderItem 


# Загружает все товары (Product.objects.all()) и показывает их на главной странице.
def home(request):
    products = Product.objects.all()
    return render(request, 'shop/home.html', {'products': products})

# Загружает страницу «О нас».
def about(request):
    return render(request, 'shop/about.html')

# Загружает страницу контактов.
def contacts(request):
    return render(request, 'shop/contacts.html')

# Обрабатывает вход пользователя.
def login_view(request):
    if request.method == 'POST':
        login_input = request.POST.get('username')
        password = request.POST.get('password')

        # Проверка, содержит ли ввод символ '@' — предполагаем, что это email
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
            return redirect('home')  # ваш главный маршрут
        else:
            messages.error(request, 'Неверное имя пользователя или пароль.')
    return render(request, 'shop/login.html')

# Обрабатывает регистрацию новых пользователей.
# В случае POST — создает нового пользователя и вход в систему, иначе показывает форму.
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'shop/signup.html', {'form': form})

# Показывает текущие товары в корзине для авторизованного пользователя.
@login_required
def cart(request):
    items = CartItem.objects.filter(user=request.user)
    total = sum(item.product.price * item.quantity for item in items)
    return render(request, 'shop/cart.html', {'items': items, 'total': total})

# Альтернативный просмотр корзины, использующий сессионную корзину (неавторизованный пользователь).
def cart_view(request):
    cart = request.session.get('cart', {})
    products = []
    total_price = 0
    for product_id, qty in cart.items():
        product = Product.objects.get(id=product_id)
        products.append({
            'product': product,
            'quantity': qty,
            'total_price': product.price * qty,
        })
        total_price += product.price * qty
    return render(request, 'cart.html', {'products': products, 'total_price': total_price})

#  Добавляет выбранный товар в корзину (для авторизованных).
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    try:
        requested_quantity = int(request.POST.get('quantity', 1))
    except (ValueError, TypeError):
        requested_quantity = 1

    # Ищем товар в корзине пользователя
    item = CartItem.objects.filter(user=request.user, product=product).first()

    if item and item.quantity >= requested_quantity:
        # 1. УМЕНЬШАЕМ КОЛИЧЕСТВО В КОРЗИНЕ
        if item.quantity > requested_quantity:
            item.quantity -= requested_quantity
            item.save()
        else:
            item.delete() # Если купили всё, что было в корзине — удаляем запись

        # 2. УМЕНЬШАЕМ КОЛИЧЕСТВО НА СКЛАДЕ
        # (Только если на складе физически есть товар)
        if product.stock >= requested_quantity:
            product.stock -= requested_quantity
            product.save()
            messages.success(request, f"Вы купили {requested_quantity} шт. '{product.name}'.")
        else:
            messages.error(request, "Ошибка: на складе недостаточно товара для списания.")
    else:
        messages.error(request, "В корзине нет такого количества товара.")

    return redirect('cart')



# Очищает корзину.
@login_required
def clear_cart(request):
    if request.method == 'POST':
        # 1. Получаем все товары в корзине пользователя
        cart_items = CartItem.objects.filter(user=request.user).select_related('product')
        
        # 2. Возвращаем каждый товар на склад
        for item in cart_items:
            product = item.product
            product.stock += item.quantity  # Прибавляем столько, сколько было в корзине
            product.save()
        
        # 3. Теперь удаляем записи из корзины
        cart_items.delete()
        
        return JsonResponse({'success': True, 'total_items': 0})
    
    return JsonResponse({'success': False, 'error': 'Invalid method'}, status=400)


# Декоратор, проверяющий вход для AJAX-запросов.
# Если пользователь не залогинен — возвращает ошибку через JSON.
def ajax_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'Пожалуйста, войдите в аккаунт'}, status=401)
        return view_func(request, *args, **kwargs)
    return wrapper

# Асинхронно добавляет товар в корзину для авторизованных через AJAX.
# Увеличивает количество товара, возвращает статус и сообщение.
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
    else:
        item.save()

    total_items = CartItem.objects.filter(user=request.user).aggregate(total_qty=Sum('quantity'))['total_qty'] or 0

    return JsonResponse({
        'success': True,
        'product_name': product.name,
        'cart_total_items': total_items,
    })

# Уменьшает количество товара на один или удаляет его, если пришли к нулю.
@login_required
def remove_one_from_cart(request, product_id):
    if request.method == 'POST':
        item = get_object_or_404(CartItem, user=request.user, product_id=product_id)
        product = item.product # Берем сам товар

        if item.quantity > 1:
            item.quantity -= 1
            item.save()
        else:
            item.delete()

        # ВОЗВРАЩАЕМ 1 ШТУКУ НА СКЛАД
        product.stock += 1
        product.save()
        
    return redirect('cart')

# Показывает список доступных товаров, где available=True.
def product_list(request):
    query = request.GET.get('q', '')  # Получаем значение поиска, по умолчанию пустая строка
    products = Product.objects.filter(available=True)

    if query:
        products = products.filter(name__icontains=query)  # Добавляем фильтр по названию

    return render(request, 'shop/product_list.html', {
        'products': products,
        'query': query,  # Передать поисковый запрос в контекст
    })

# Загружает страницу с подробной информацией о товаре.
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'shop/product_detail.html', {'product': product})

@login_required
def buy_product(request, product_id):
    if request.method == 'POST':
        # Получаем корзину этой user
        item = get_object_or_404(CartItem, user=request.user, product_id=product_id)
        product = item.product

        # Получаем запрошенное количество (по умолчанию - текущая в корзине)
        try:
            requested_quantity = int(request.POST.get('quantity', item.quantity))
        except (ValueError, TypeError):
            requested_quantity = item.quantity

        # Ограничиваем, чтобы не уменьшить больше, чем есть
        requested_quantity = min(requested_quantity, item.quantity)

        # Проверяем, что на складе хватает этого количества
        if product.stock < requested_quantity:
            messages.error(request, f"На складе недостаточно товара (осталось: {product.stock})")
            return redirect('cart')

        # Уменьшаем количество в корзине
        if requested_quantity >= item.quantity:
            # Удаляем товар из корзины, если уменьшилось до нуля
            item.delete()
        else:
            # Иначе уменьшаем количество
            item.quantity -= requested_quantity
            item.save()

        # Уменьшаем количество на складе
        product.stock -= requested_quantity
        product.save()

        # Можно добавить сообщение
        messages.success(request, f"Вы приобрели {requested_quantity} шт. '{product.name}'.")
        return redirect('cart')
    
@login_required
def create_order(request):
    # Здесь вы можете кастомизировать выбор товаров, например, из корзины
    cart_items = CartItem.objects.filter(user=request.user)

    if not cart_items:
        messages.error(request, "Ваша корзина пуста.")
        return redirect('cart')
    
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    
    with transaction.atomic():
        order = Order.objects.create(user=request.user, total_price=total_price)
        for item in cart_items:
            # Создайте запись о покупке
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price_at_purchase=item.product.price
            )
        # После создания заказа очищайте корзину или оставьте в зависимости от логики

    # Можно также вывести сообщение или перенаправить на страницу с заказом
    messages.success(request, f"Ваш заказ #{order.id} успешно оформлен!")
    # Например, очистите корзину
    cart_items.delete()
    return redirect('order_detail', order_id=order.id)

@login_required
def user_orders(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items__product')
    return render(request, 'shop/user_orders.html', {'orders': orders})