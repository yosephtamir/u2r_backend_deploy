from rest_framework import serializers
from .models import CustomUser, UserProfile, Company
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            'userFirstName', 
            'userMiddleName', 
            'userLastName', 
            'userCountry', 
            'userRegion', 
            'userZone', 
            'userWoreda', 
            'userKebele', 
            'userPhoneNumber', 
            'userRole',
            'userRenewedIDFront',
            'userRenewedIDBack',
            'profilePic'
        ]

class UserCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = [
            'companyName',
            'companyCountry',
            'companyRegion',
            'companyZone',
            'companyWoreda',
            'companyKebele',
            'companyHN',
            'companyTIN',
            'companyLicense',
            'companyLogo'
        ]    

class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)

    class Meta:
        model = CustomUser
        fields = '__all__' 

class LoginSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        return {**super().validate(attrs), **{
            'id': self.user.id,
            'email': self.user.email,
        }}

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    default_error_message = {
        'bad_token': ('Token is expired or invalid')
    }

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):

        try:
            RefreshToken(self.token).blacklist()

        except TokenError:
            return self.default_error_message

class CheckEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()

class AuthorizeSerializer(serializers.Serializer):
    pass   

class UserInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'is_verified', 'is_active', 'is_companyAdmin']