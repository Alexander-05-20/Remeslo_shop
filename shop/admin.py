from django.contrib import admin
from .models import Product, ProductImage


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
