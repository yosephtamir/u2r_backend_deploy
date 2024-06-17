from django.contrib import admin
from .models import *

@admin.register(Shop)
class ShopModelAdmin(admin.ModelAdmin):
    model = Shop
    list_display = ['id', 'name', 'company']