from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField

from .models import *
from Shop.models import Shop

class ShopSerializer1(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ['id', 'name']

class ProductSubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSubCategory
        fields = ['id', 'name']

class CategoryThumbnailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryThumbnailImage
        fields = ['id', 'url']        

class ProductCategorySerializer(serializers.ModelSerializer):
    thumbnail = CategoryThumbnailSerializer(many=False, read_only=True)

    class Meta:
        model = ProductCategory
        fields = ['id', 'name', 'thumbnail']

    def to_representation(self, instance):
        thumbnails = CategoryThumbnailImage.objects.filter(category=instance)
        thumbnails_data = CategoryThumbnailSerializer(thumbnails, many=True).data
        representation = super().to_representation(instance)
        representation['thumbnails'] = thumbnails_data
        return representation   

# class ProductFileSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ProductFile
#         fields = '__all__' 

# class ProductImageSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ProductImageVariations
#         fields = '__all__'


    def validate_product_image(self, value):
        # Check file type (e.g., allow only image types)
        allowed_file_types = ['image/jpeg', 'image/png']
        if value.content_type not in allowed_file_types:
            raise serializers.ValidationError("Invalid file type. Only JPEG and PNG files are allowed.")

        # Check file size if necessary
        max_file_size = 5 * 1024 * 1024  # 5MB
        if value.size > max_file_size:
            raise serializers.ValidationError("File size exceeds 5MB.")

        return value
                      

class ProductSerializer(serializers.ModelSerializer):
    shop = ShopSerializer1(many=False, read_only=True)

    class Meta:
        model = Product
        fields = '__all__'


class UserProductInteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProductInteraction
        fields = '__all__'

class CartSerializer(serializers.ModelSerializer):
    summary = serializers.JSONField(source='_summary')

    class Meta:
        model = Cart
        fields = '__all__'


class CartItemSerializer(serializers.ModelSerializer):
    product_details = serializers.JSONField(
        source='_product_details', read_only=True
    )

    image = serializers.SerializerMethodField(
        source='_product_thumbnail', read_only=True
    )

    class Meta:
        model = CartItem
        fields = '__all__'

    def get_image(self, obj):
        # `product_thumbnail` is a `CloudinaryResource` object
        return obj.product.product_thumbnail.url if obj.product.product_thumbnail else None

class WishListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wishlist
        fields = '__all__'

class WishListItemSerializer(serializers.ModelSerializer):
    product_details = serializers.JSONField(
        source='_product_details', read_only=True
    )

    image = serializers.SerializerMethodField(
        source='_product_thumbnail', read_only=True
    )

    class Meta:
        model = WishlistItem
        fields = '__all__'

    def get_image(self, obj):
        # `product_thumbnail` is a `CloudinaryResource` object
        return obj.product.product_thumbnail.url if obj.product.product_thumbnail else None
    
class OrderSerializer(serializers.ModelSerializer):
    order_items_count = serializers.JSONField(
        source='items_count', read_only=True
    )

    class Meta:
        model = Order
        fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
    product_details = serializers.JSONField(
        source='_product_details', read_only=True
    )

    image = serializers.SerializerMethodField(
        source='_product_thumbnail', read_only=True
    )

    class Meta:
        model = OrderItem
        fields = '__all__'

    def get_image(self, obj):
        # `product_thumbnail` is a `CloudinaryResource` object
        return obj.product.product_thumbnail.url if obj.product.product_thumbnail else None    