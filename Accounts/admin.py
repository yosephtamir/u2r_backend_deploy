from django.contrib import admin
from .models import UserProfile, Company
from django.contrib.auth import get_user_model
UserModel = get_user_model()

@admin.register(UserModel)
class UserModelAdmin(admin.ModelAdmin):
    model = UserModel
    list_display = ("email",)
    list_display_links = ("email",)

@admin.register(UserProfile)
class UserProfileModelAdmin(admin.ModelAdmin):
    model = UserProfile
    list_display = ['userFirstName', 'userMiddleName', 'userLastName', 'userCountry', 'userRole']

@admin.register(Company)
class CompanyModelAdmin(admin.ModelAdmin):
    model = Company
    list_display = ['id', 'companyName', 'companyAdmin']