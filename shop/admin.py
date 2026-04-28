from django.contrib import admin
from django.utils.html import format_html
from .models import Product, ProductImage

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 2
    #readonly_fields = ('current_image',)

    #   if obj and obj.image:
     #       return format_html('<img src="{}" width="100" />', obj.image.url)
      #  return "Нет изображения"
   # current_image.short_description = 'Текущее изображение fghjkjhgfd'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'available', 'created_at')
    list_filter = ('available',)
    search_fields = ('name',)
    inlines = [ProductImageInline]