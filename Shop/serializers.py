from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField

from MarketPlace.serializers import ProductSerializer
from .models import Shop                     

class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = '__all__'
