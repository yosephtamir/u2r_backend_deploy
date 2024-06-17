from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import UserProductRating, Product

@receiver(post_save, sender=UserProductRating)
@receiver(post_delete, sender=UserProductRating)
def update_product_rating(sender, instance, **kwargs):
    product = instance.product
    product.update_ave_rating()