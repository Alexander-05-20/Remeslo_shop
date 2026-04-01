from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.home, name='home'),  # главная - каталог товаров
    path('products/', views.product_list, name='products'), # Страница со списком всех товаров
    path('product/<int:pk>/', views.product_detail, name='product_detail'), # Детальная страница товара
    path('cart/', views.cart, name='cart'),  # Страница корзины
    path('cart/remove_one/<int:product_id>/', views.remove_one_from_cart, name='remove_one_from_cart'), # Удаление одного товара из корзины
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'), # Добавление товара в корзину
    path('cart/add_ajax/<int:product_id>/', views.add_to_cart_ajax, name='add_to_cart_ajax'), # Асинхронное добавление товара
    path('cart/clear/', views.clear_cart, name='clear_cart'), # Очистка корзины
    path('about/', views.about, name='about'),  # Страница о нас 
    path('signup/', views.signup, name='signup'), # Страница регистрации нового пользователя
    path('login/', views.login_view, name='login'), # Страница входа в аккаунт
    path('buy/<int:product_id>/', views.buy_product, name='buy_product'),

]
# + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)