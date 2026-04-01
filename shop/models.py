from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    available = models.BooleanField(default=True, verbose_name='В наличии')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    stock = models.PositiveIntegerField(default=0, verbose_name='Остаток на складе')

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name='Товар')
    image = models.ImageField(upload_to='products/%Y/%m/%d/', verbose_name='Изображение')
    alt_text = models.CharField(max_length=255, blank=True, verbose_name='Описание изображения (alt)')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')

    def __str__(self):
        return f"Изображение для {self.product.name}"
    

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Покупатель')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата заказа')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Общая цена')
    # Можно добавить статус, адрес доставки и другие поля

    def __str__(self):
        return f"Заказ #{self.id} от {self.user.username}"
    

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='Заказ')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    quantity = models.PositiveIntegerField(verbose_name='Количество')
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена на момент покупки')

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    
# class AboutPageMedia(models.Model):
#     image = models.ImageField(upload_to='about/media/')
#     caption = models.CharField(max_length=255, blank=True)  # необязательно

#     def __str__(self):
#         return self.caption or f'Изображение {self.id}'