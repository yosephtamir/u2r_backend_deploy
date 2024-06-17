from django.contrib import admin
from .models import *

@admin.register(Product)
class ProductModelAdmin(admin.ModelAdmin):
    model = Product
    list_display = ['id', 'name', 'category', 'shop', 'company']

@admin.register(ProductCategory)
class ProductCategoryModelAdmin(admin.ModelAdmin):
    model = ProductCategory
    list_display = ['id', 'name']

@admin.register(CategoryThumbnailImage)
class CategoryThumbnailModelAdmin(admin.ModelAdmin):
    model = CategoryThumbnailImage
    list_display = ['url']     

@admin.register(ProductSubCategory)
class ProductSubCategoryModelAdmin(admin.ModelAdmin):
    model = ProductSubCategory
    list_display = ['id', 'name']

# @admin.register(ProductImageVariations)
# class ProductImageModelAdmin(admin.ModelAdmin):
#     model = ProductImageVariations
#     list_display = ['product_image', 'product']

# @admin.register(ProductFile)
# class ProductFileModelAdmin(admin.ModelAdmin):
#     model = ProductFile
#     list_display = ['product_file', 'product']  

@admin.register(UserProductRating)
class UserProductRatingModelAdmin(admin.ModelAdmin):
    model = UserProductRating

@admin.register(Cart)
class UserCartModelAdmin(admin.ModelAdmin):
    model = Cart

@admin.register(CartItem)
class UserCartItemModelAdmin(admin.ModelAdmin):
    model = CartItem

@admin.register(Wishlist)
class UserWishlistModelAdmin(admin.ModelAdmin):
    model = Wishlist

@admin.register(WishlistItem)
class UserWishlistItemModelAdmin(admin.ModelAdmin):
    model = WishlistItem

@admin.register(Order)
class UserOrderModelAdmin(admin.ModelAdmin):
    model = Order

@admin.register(OrderItem)
class UserOrderItemModelAdmin(admin.ModelAdmin):
    model = OrderItem