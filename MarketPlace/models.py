from django.db import models
from cloudinary.models import CloudinaryField

from helpers.models import TimestampsModel
from Accounts.models import CustomUser, Company;
from Shop.models import Shop;

class ProductStatus(models.TextChoices):
    inStoke = 'In Stoke'
    lowStoke = 'Low Stoke'
    outOfStoke = 'Out of Stoke'

class ProductAdminStatus(models.TextChoices):
    approved = 'approved' 
    notApproved = 'notApproved'

class ProductCategory(TimestampsModel):
    name = models.CharField(max_length=225)
    description = models.CharField(max_length=255, blank=True,)

    def __str__(self) -> str:
        return self.name
    
class CategoryThumbnailImage(TimestampsModel):
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    url = models.CharField(max_length=255)    

class ProductSubCategory(TimestampsModel):
    name = models.CharField(max_length=225, blank=True, null=True)
    description = models.CharField(max_length=255)
    parent_category = models.ForeignKey(ProductCategory, blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.name

class ProductCurrency(models.TextChoices):
    ETB = 'ETB'

class Product(TimestampsModel):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='products')
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    sub_category = models.ForeignKey(ProductSubCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    product_thumbnail = CloudinaryField()
    product_image2 = CloudinaryField(blank=True, null=True)
    product_image3 = CloudinaryField(blank=True, null=True)
    product_image4 = CloudinaryField(blank=True, null=True)
    product_image5 = CloudinaryField(blank=True, null=True)
    product_image6 = CloudinaryField(blank=True, null=True)
    status = models.CharField(max_length=25, choices=ProductStatus.choices)
    quantity = models.BigIntegerField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    has_discount = models.BooleanField(default=False)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    tax = models.DecimalField(max_digits=10, decimal_places=2)
    admin_status = models.TextField(choices=ProductAdminStatus.choices, blank=True, null=True)
    is_published = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    currency = models.CharField(choices=ProductCurrency.choices, max_length=10)
    product_file = models.FileField(upload_to='product_files', blank=True, null=True)
    ave_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)

    def update_ave_rating(self):
        ratings = self.userProductRating_set.all()
        if ratings.exists():
            self.ave_rating = ratings.aggregate(models.Avg('rating'))['rating__avg']
            self.save()

    def __str__(self) -> str:
        return self.name

# class ProductImageVariations(TimestampsModel):
#     product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_images')
#     product_image = CloudinaryField()  

# class ProductFile(TimestampsModel):
#     product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_file')
#     product_file = models.FileField()

class InteractionChoices(models.TextChoices):
    viewed = 'Viewed',
    purchased = 'Purchased'
    liked = 'Liked'

class UserProductInteraction(TimestampsModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True, null=True)
    interaction_type = models.CharField(choices=InteractionChoices.choices, blank=True, null=True, max_length=10)

class LastViewedProduct(TimestampsModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField()

class ProductReview(TimestampsModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    comment = models.TextField(blank=True, null=True)
    reply = models.ForeignKey('self', blank=True, null=True, on_delete=models.CASCADE)

class UserProductRating(TimestampsModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='userProductRating_set')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    rating = models.IntegerField()

class Cart(TimestampsModel):
    owner = models.ForeignKey(CustomUser, related_name='cart', on_delete=models.CASCADE)
    delivery_address = models.CharField(max_length=255, blank=True)

    @property
    def _summary(self):
        cart_items = self.items.prefetch_related('product').all()
        
        if not cart_items:
            return {'sub_total': 0, 'total_discount': 0, 'currency': 'ETB', 'count': 0}

        subtotal = total_discount = total_tax = 0
        count = len(cart_items)
        for cart_item in cart_items:
            product = cart_item.product
            actual_price = product.price
            selling_price = (actual_price - product.discount_price) if product.has_discount else actual_price
            total_tax += product.tax * cart_item.quantity

            # Calculate subtotal and total discount
            subtotal += actual_price * cart_item.quantity
            total_discount += (actual_price - selling_price) * cart_item.quantity
        
        # Return summary as a dictionary
        return {
            'currency': 'ETB',
            'delivery_address': self.delivery_address,
            'sub_total': subtotal,
            'total_discount': total_discount,
            'vat': total_tax,
            'total': subtotal + total_tax - total_discount,
            'count': count,
        }

    def __str__(self) -> str:
        return 'Cart owned by ' + self.owner.__str__()

class CartItem(TimestampsModel):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='cart_items', on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1) 

    @property
    def _product_details(self):
        product = self.product
        return {
            'name': product.name,
            'description': product.description,
            'price': product.price,
            'discount_price': product.discount_price,
        }

    @property
    def _product_thumbnail(self):
        product = self.product
        print(product.product_thumbnail)
        return product.product_thumbnail
    
class Wishlist(TimestampsModel):
    owner = models.ForeignKey(CustomUser, related_name='wishList', on_delete=models.CASCADE)

    def __str__(self) -> str:
        return 'WishList owned by ' + self.owner.__str__() 

class WishlistItem(TimestampsModel):
    wishlist = models.ForeignKey(Wishlist, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='wishlist_items', on_delete=models.CASCADE)

    @property
    def _product_details(self):
        product = self.product
        return {
            'name': product.name,
            'description': product.description,
            'price': product.price,
            'discount_price': product.discount_price,
            'stock_status': product.status
        }

    @property
    def _product_thumbnail(self):
        product = self.product
        print(product.product_thumbnail)
        return product.product_thumbnail 

class Promotion(TimestampsModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    code = models.CharField(max_length=255)
    promotion_type = models.CharField(max_length=255)
    discount_type = models.TextField(blank=True, null=True)
    quantity = models.BigIntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    maximum_discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

class PromoProduct(TimestampsModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    promo = models.ForeignKey(Promotion, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)    

class Order(TimestampsModel):
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    
    @property
    def items_count(self):
        return self.orderItems.count()

    def __str__(self) -> str:
        return 'Orders by: ' + self.customer.__str__()

class OrderItem(TimestampsModel):
    ORDER_STATUS_CHOICES = [
        ('shipped', 'En route'),
        ('cancelled', 'Cancelled'),
        ('delivered', 'Delivered')
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='orderItems')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    promo = models.ForeignKey(Promotion, blank=True, null=True, on_delete=models.CASCADE)
    merchant_company = models.ForeignKey(Company, related_name='orderItem_merchant', on_delete=models.CASCADE)
    order_price = models.DecimalField(max_digits=10, decimal_places=2)
    order_tax = models.DecimalField(db_column='order_VAT', max_digits=10, decimal_places=2)
    order_discount = models.DecimalField(max_digits=10, decimal_places=2)
    deleted_at = models.DateTimeField(blank=True, null=True)
    is_deleted = models.BooleanField(blank=True, null=True, default=False)
    status = models.TextField(blank=True, null=True, choices=ORDER_STATUS_CHOICES)

    @property
    def _product_details(self):
        product = self.product
        return {
            'name': product.name,
            'description': product.description,
            'price': product.price,
            'discount_price': product.discount_price,
        }

    @property
    def _product_thumbnail(self):
        product = self.product
        print(product.product_thumbnail)
        return product.product_thumbnail