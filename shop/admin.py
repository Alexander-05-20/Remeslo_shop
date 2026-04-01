from django.contrib import admin
from .models import Product, ProductImage, Order, OrderItem,AboutPageMedia

admin.site.register(AboutPageMedia)

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 2
    readonly_fields = ('current_image',)

    def current_image(self, obj):
        if obj and obj.image:
            return f'<img src="{obj.image.url}" width="100" />'
        return "Нет изображения"
    current_image.allow_tags = True
    current_image.short_description = 'Текущее изображение'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'available','created_at')
    list_filter = ('available',)
    search_fields = ('name',)
    inlines = [ProductImageInline]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'total_price')
    list_filter = ('created_at', 'user')
    search_fields = ('user__username',)

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price_at_purchase')
    list_filter = ('product',)
    search_fields = ('product__name',)