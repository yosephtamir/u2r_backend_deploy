from django.http import Http404, request
from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework import generics,permissions
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.parsers import MultiPartParser, FormParser

from helpers.err_response import CustomErrorResponse
from .serializers import LogoutSerializer, RegistrationSerializer, CheckEmailSerializer, AuthorizeSerializer, UserCompanySerializer, UserInformationSerializer, LoginSerializer, UserProfileSerializer
from drf_yasg.utils import swagger_auto_schema
from .models import Company, CustomUser, UserProfile
from rest_framework import status
from rest_framework.response import Response
from rest_framework import generics
from .serializers import RegistrationSerializer
from .models import CustomUser, UserProfile, Company
from django.db import transaction

class RegistrationAPIView(generics.GenericAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    parser_classes = (MultiPartParser, FormParser)

    @swagger_auto_schema(tags=['Accounts'])
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        print("Before serialization: ", request.data)

        user_profile_data = {}
        user_company_data = {}

        for key, value in request.data.items():
            if key.startswith('user_profile'):
                sub_key = key.split('user_profile[')[-1].rstrip(']')
                if isinstance(value, list):
                    user_profile_data[sub_key] = value[0] if value else None
                else:
                    user_profile_data[sub_key] = value
            elif key.startswith('user_company'):
                sub_key = key.split('user_company[')[-1].rstrip(']')
                if isinstance(value, list):
                    user_company_data[sub_key] = value[0] if value else None
                else:
                    user_company_data[sub_key] = value


        if serializer.is_valid():
            print("After serialization: ", serializer.validated_data)
            with transaction.atomic():
                user = serializer.save()

                print("------------------------------------\n")
                print("User:", serializer.validated_data)
                print("User Profile Data:", user_profile_data)
                print("User Company Data:", user_company_data)
                print("------------------------------------\n")

                existing_profile = UserProfile.objects.filter(user=user).first()
                if not existing_profile:
                    profile_serializer = UserProfileSerializer(data=user_profile_data)
                    if profile_serializer.is_valid():
                        print("profile is valid")
                        UserProfile.objects.create(user=user, **user_profile_data)
                    else:
                        return Response(profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
                existing_company = Company.objects.filter(companyAdmin=user).first()
                if not existing_company:
                    company_serializer = UserCompanySerializer(data=user_company_data)
                    if company_serializer.is_valid():
                        print("company is valid")
                        Company.objects.create(companyAdmin=user, **user_company_data)
                    else:
                        return Response(company_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print("After serialization error: ", serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer
    @swagger_auto_schema(tags=['Accounts'])
    def post(self, *args, **kwargs):
        return super().post(*args, **kwargs)

class LoginRefreshView(TokenRefreshView):
    @swagger_auto_schema(tags=['Accounts'])
    def post(self, *args, **kwargs):
        return super().post(*args, **kwargs)

class LogoutAPIView(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = []

    @swagger_auto_schema(tags=['Accounts'])
    def post(self, request):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({'message':'You have logged out successfully'},status=status.HTTP_204_NO_CONTENT)

class CheckEmailView(generics.GenericAPIView):
    permission_classes = []
    serializer_class = CheckEmailSerializer

    @swagger_auto_schema(tags=['Accounts'])
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        is_email_available = not CustomUser.objects.filter(email=email).exists()

        return Response({'is_email_available': is_email_available}, status=status.HTTP_200_OK)

class AuthorizeView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class  = AuthorizeSerializer

    @swagger_auto_schema(tags=['Accounts'])
    def post(self, request, *args, **kwargs):
        auth_header = request.headers.get('Authorization')
        token_str = auth_header.split(" ")[1] 
        if not token_str:
            return Response({'detail': 'Authentication credentials were not provided.'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            token = AccessToken(token_str)
        except TokenError as e:
            # Handle token errors including expired and invalid tokens
            return Response(
                {'detail': 'Token is expired or invalid.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        except Exception as e:
            # Handle unexpected errors
            return Response(
                {'detail': f"Unexpected error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        return Response({'message': 'User is authenticated'}, status=status.HTTP_200_OK)
    
class UserInformation(generics.GenericAPIView):
    permission_classes = []
    serializer_class = UserInformationSerializer

    @swagger_auto_schema(tags=['Accounts'])
    def get(self, request, user_id):
        try:
            user = CustomUser.objects.get(id=user_id)
            serializer = UserInformationSerializer(user)
            user_profile = UserProfile.objects.get(user=user)
            profile_data = UserProfileSerializer(user_profile)
            company = user.user_company
            

            response_data = {
                    "status_code": status.HTTP_200_OK,
                    "user_info": profile_data.data,
                    "company": {
                        "id": company.id if company else None,
                        "name": company.companyName if company else None,
                    },
                    "data": serializer.data,
                    "status": "success",
                }
        
            return Response(response_data, status=status.HTTP_200_OK)
        except Http404:
            return CustomErrorResponse(status.HTTP_404_NOT_FOUND, "User Not Found")
        except Exception as e:
            return CustomErrorResponse(status.HTTP_500_INTERNAL_SERVER_ERROR,
                                   f"An error occurred while retrieving User with id-{user_id}: {str(e)}")