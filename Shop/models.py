from django.db import models
from cloudinary.models import CloudinaryField

from helpers.fields import ValidatedImageField
from helpers.models import TimestampsModel
from Accounts.models import CustomUser, Company

class Shop(TimestampsModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='shops')
    # shopAdmin = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_shops')
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    logo = CloudinaryField(null=True, blank=True)
    cover_image = CloudinaryField(null=True, blank=True)
    is_deleted = models.TextField(default=False)

    def __str__(self) -> str:
        return self.name.__str__()