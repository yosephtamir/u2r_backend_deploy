from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from helpers.models import TimestampsModel
from django.db import models
from cloudinary.models import CloudinaryField


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_companyAdmin', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)


class UserType(models.TextChoices):
    SELLER = 'seller'
    BUYER = 'buyer'

class CustomUser(AbstractBaseUser, PermissionsMixin, TimestampsModel):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    is_companyAdmin = models.BooleanField(default=False)

    @property
    def is_staff(self):
        return self.is_companyAdmin

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'


class UserProfile(TimestampsModel):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='user_profile')
    userFirstName = models.CharField(max_length=30)
    userMiddleName = models.CharField(max_length=30)
    userLastName = models.CharField(max_length=30)
    userCountry = models.CharField(max_length=50)
    userRegion = models.CharField(max_length=50)
    userZone = models.CharField(max_length=50)
    userWoreda = models.CharField(max_length=50)
    userKebele = models.CharField(max_length=50)
    userPhoneNumber = models.CharField(max_length=15, blank=True)
    userRole = models.CharField(max_length=25, choices=UserType.choices)
    userRenewedIDFront = CloudinaryField()
    userRenewedIDBack = CloudinaryField()
    profilePic = CloudinaryField(null=True, blank=True)

    def __str__(self) -> str:
        return self.userFirstName + self.userMiddleName + self.userLastName


class Company(TimestampsModel):
    companyAdmin = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='user_company')
    companyName = models.CharField(max_length=50)
    companyCountry = models.CharField(max_length=50)
    companyRegion = models.CharField(max_length=50)
    companyZone = models.CharField(max_length=50)
    companyWoreda = models.CharField(max_length=50)
    companyKebele = models.CharField(max_length=50)
    companyHN = models.CharField(max_length=25)
    companyTIN = models.CharField(max_length=25)
    companyPhoneNumber = models.CharField(max_length=15, blank=True)
    companyLicense = CloudinaryField()
    companyLogo = CloudinaryField(null=True, blank=True)

    def __str__(self) -> str:
        return self.companyName + " -- "+ self.companyAdmin.email
