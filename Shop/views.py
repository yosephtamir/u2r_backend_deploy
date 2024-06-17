from django.http import Http404
from drf_yasg.utils import swagger_auto_schema
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework import (
    generics,
    viewsets,
    permissions,
    response,
    status,
)

from .models import Shop
from Accounts.models import Company
from .serializers import *
from MarketPlace.serializers import ProductSerializer
from MarketPlace.models import Product
from helpers.err_response import CustomErrorResponse
from helpers.pagination import PaginatorGenerator
from helpers.permissions import IsCompanyAdmin

class ShopsListBaseView(generics.ListAPIView):
    """ List Shops Base view"""
    serializer_class = ShopSerializer
    permission_classes = [permissions.AllowAny]  
    pagination_class = PaginatorGenerator()(_page_size=15)   

    def get_shops(self, request, filters, message):
        try:
            queryset = Shop.objects.filter(**filters).order_by('-updated_at')
            serializer = ShopSerializer(queryset, many=True)

            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.serializer_class(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = self.serializer_class(queryset, many=True)
            
            # self.get_paginated_response(serializer.data)
            
            response_data = {
                "status_code": status.HTTP_200_OK,
                "message": message,
                "count": len(serializer.data),
                "data": serializer.data,
                "status": "success",
            }

            return response.Response(response_data, status=status.HTTP_200_OK)
        except Http404:
            return CustomErrorResponse(status.HTTP_404_NOT_FOUND, "Shop Not Found")
        except Exception as e:
            return CustomErrorResponse(status.HTTP_500_INTERNAL_SERVER_ERROR,
                                   f"An error occurred while retrieving {message}: {str(e)}")

class ShopListView(ShopsListBaseView):
    """ List all shops available """
    @swagger_auto_schema(tags=['Shops'])
    def list(self, request):
        shops = self.get_shops(request, {}, "All Shops")
        if shops:
            return shops
        else:
            return CustomErrorResponse(status.HTTP_404_NOT_FOUND, "Shop not found")
        
class ShopDetailView(generics.GenericAPIView):
    serializer_class = ShopSerializer
    permission_classes = [permissions.AllowAny]

    def get_shop(self, shop_id):
        try:
            return Shop.objects.get(id=shop_id)
        except Shop.DoesNotExist:
            return None

    @swagger_auto_schema(tags=['Shops'])
    def get(self, request, shop_id):
        """ A single Shop detail """
        try:
            current_shop = self.get_shop(shop_id)
            if not current_shop:
                return CustomErrorResponse(status.HTTP_404_NOT_FOUND, "Shop does not exist")

            serializer = self.get_serializer(current_shop)
            response_data = {
                    "status_code": status.HTTP_200_OK,
                    "data": serializer.data,
                    "status": "success",
                }
        
            return response.Response(response_data, status=status.HTTP_200_OK)
        except Http404:
            return CustomErrorResponse(status.HTTP_404_NOT_FOUND, "Shop Not Found")
        except Exception as e:
            return CustomErrorResponse(status.HTTP_500_INTERNAL_SERVER_ERROR,
                                   f"An error occurred while retrieving Shop with id-{shop_id}: {str(e)}")
              
class CompanyShopListCreateView(generics.ListCreateAPIView):
    """ List and Create Shops in a Company """
    serializer_class = ShopSerializer
    permission_classes = [IsCompanyAdmin]
    pagination_class = PaginatorGenerator()(_page_size=15)
    parser_classes = [MultiPartParser]

    def get_company(self, company_id):
        try:
            return Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return None
        
    def get_queryset(self, company_id):
        shops = Shop.objects.filter(company_id=company_id).order_by('-updated_at')
        if shops:
            return shops
        else:
            return None

    @swagger_auto_schema(tags=['Shops'])
    def list(self, request, company_id):
        """ List Shops in a Company """
        try:
            queryset = self.get_queryset(company_id)
            if not queryset:
                return CustomErrorResponse(status.HTTP_404_NOT_FOUND, "No Shop found")
            
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.serializer_class(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.serializer_class(queryset, many=True)
            response_data = {
                "status_code": status.HTTP_200_OK,
                "message": "All Shops of the company",
                "count": len(serializer.data),
                "data": serializer.data,
                "status": "success",
            }
            return response.Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return CustomErrorResponse(status.HTTP_500_INTERNAL_SERVER_ERROR,
                                   f"An error occurred while retrieving all shops: {str(e)}")

    @swagger_auto_schema(tags=['Shops'])
    def create(self, request, company_id):
        """ Create Shops in a Company """
        current_company = self.get_company(company_id)
        if not current_company:
            return CustomErrorResponse(status.HTTP_404_NOT_FOUND, "Company does not exist")
        
        shop_data = request.data.copy()
        shop_data['company'] = current_company.id

        serializer = self.get_serializer(data=shop_data)

        if serializer.is_valid():
            serializer.save()
            return response.Response({
                'message': 'Shop successfully Created.',
                'data': serializer.data,
                }, status=status.HTTP_201_CREATED)
        else:
            return CustomErrorResponse(status.HTTP_400_BAD_REQUEST, serializer.errors)       

class CompanyShopManageView(viewsets.GenericViewSet):
    """ API Viewset to perform CRUD operations on companies shop(s) """
    serializer_class = ShopSerializer
    permission_classes = []

    def get_company(self, company_id):
        try:
            return Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return None

    def get_shop(self, company, shop_id):
        try:
            return company.shops.get(id=shop_id)
        except Shop.DoesNotExist:
            return None

    @swagger_auto_schema(tags=['Shops'])
    def partial_update(self, request, company_id, shop_id):
        """ Update Company shop """
        current_company = self.get_company(company_id)
        if not current_company:
            return CustomErrorResponse(status.HTTP_404_NOT_FOUND, "Company does not exist")

        current_shop = self.get_shop(current_company, shop_id)
        if not current_shop:
            return CustomErrorResponse(status.HTTP_404_NOT_FOUND, "Shop does not exist")

        serializer = self.get_serializer(instance=current_shop, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return response.Response({
                'message': 'Shop successfully Edited.',
                'data': serializer.data,
                }, status=status.HTTP_200_OK)
        else:
            return CustomErrorResponse(status.HTTP_400_BAD_REQUEST, serializer.errors)
          
    @swagger_auto_schema(tags=['Shops'])
    def destroy(self, request, company_id, shop_id):
        """ Delete Company shop """
        current_company = self.get_company(company_id)
        if not current_company:
            return CustomErrorResponse(status.HTTP_404_NOT_FOUND, "Company does not exist")

        current_shop = self.get_shop(current_company, shop_id)
        if not current_shop:
            return CustomErrorResponse(status.HTTP_404_NOT_FOUND, "Shop does not exist")

        current_shop.delete()
        return response.Response({'message': 'Shop successfully deleted.'}, status=status.HTTP_204_NO_CONTENT)
    
    @swagger_auto_schema(tags=['Shops'])
    def shop_detail(self, request, company_id, shop_id):
        """ A single Shop detail """
        try:
            current_company = self.get_company(company_id)
            if not current_company:
                return CustomErrorResponse(status.HTTP_404_NOT_FOUND, "Company does not exist")

            current_shop = self.get_shop(current_company, shop_id)
            if not current_shop:
                return CustomErrorResponse(status.HTTP_404_NOT_FOUND, "Shop does not exist")

            serializer = self.get_serializer(current_shop)
            response_data = {
                    "status_code": status.HTTP_200_OK,
                    "data": serializer.data,
                    "status": "success",
                }
        
            return response.Response(response_data, status=status.HTTP_200_OK)
        except Http404:
            return CustomErrorResponse(status.HTTP_404_NOT_FOUND, "Shop Not Found")
        except Exception as e:
            return CustomErrorResponse(status.HTTP_500_INTERNAL_SERVER_ERROR,
                                   f"An error occurred while retrieving Shop with id-{shop_id}: {str(e)}")

class ShopProductListCreateView(generics.ListCreateAPIView):
    """Create a new product in the specified shop"""
    serializer_class = ProductSerializer
    permission_classes = [] # Is company admin Permission
    parser_classes = [MultiPartParser, JSONParser]

    def get_company(self, company_id):
        try:
            return Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return None

    def get_shop(self, company, shop_id):
        try:
            return company.shops.get(id=shop_id)
        except Shop.DoesNotExist:
            return None

    @swagger_auto_schema(tags=['Shops'])
    def create(self, request, company_id, shop_id):
        """Create a new product in the specified shop"""
        current_company = self.get_company(company_id)
        if not current_company:
            return CustomErrorResponse(status.HTTP_404_NOT_FOUND, "Company does not exist")
        
        current_shop = self.get_shop(current_company, shop_id)
        if not current_shop:
            return CustomErrorResponse(status.HTTP_404_NOT_FOUND, "Shop does not exist")

        data = request.data['shop'] = current_shop.id
        data = request.data['company'] = current_company.id
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            serializer.save(company=current_company, shop=current_shop)
            return response.Response({
                'message': 'Product successfully Created.',
                'data': serializer.data,
                }, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)
            return CustomErrorResponse(status.HTTP_400_BAD_REQUEST, serializer.errors)
        
    @swagger_auto_schema(tags=['Shops'])
    def list(self, request, company_id, shop_id):
        """ List Products in a Company's Shop """
        try:
            current_company = self.get_company(company_id)
            if not current_company:
                return CustomErrorResponse(status.HTTP_404_NOT_FOUND, "Company does not exist")
            
            current_shop = self.get_shop(current_company, shop_id)
            if not current_shop:
                return CustomErrorResponse(status.HTTP_404_NOT_FOUND, "Shop does not exist")
            
            products = Product.objects.filter(shop=current_shop) 
            page = self.paginate_queryset(products)
            if page is not None:
                serializer = self.serializer_class(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.serializer_class(products, many=True)
            response_data = {
                "status_code": status.HTTP_200_OK,
                "message": "All Products of the company's shop",
                "data": serializer.data,
                "status": "success",
                "page_info": {
                    "count": len(serializer.data),
                    "next": None,
                    "previous": None,
                }
            }
            return response.Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return CustomErrorResponse(status.HTTP_500_INTERNAL_SERVER_ERROR,
                                   f"An error occurred while retrieving all shops: {str(e)}")

class ShopProductManageView(viewsets.GenericViewSet):
    """API Viewset to perform CRUD operations on products in a shop"""
    serializer_class = ProductSerializer
    permission_classes = []

    def get_company(self, company_id):
        try:
            return Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return None

    def get_shop(self, company, shop_id):
        try:
            return company.shops.get(id=shop_id)
        except Shop.DoesNotExist:
            return None

    def get_product(self, shop, product_id):
        try:
            return shop.products.get(id=product_id)
        except Product.DoesNotExist:
            return None
      
    @swagger_auto_schema(tags=['Shops'])
    def retrieve(self, request, company_id, shop_id, product_id):
        """Retrieve a specific product from the specified shop"""
        current_company = self.get_company(company_id)
        if not current_company:
            return CustomErrorResponse(status.HTTP_404_NOT_FOUND, "Company does not exist")

        current_shop = self.get_shop(current_company, shop_id)
        if not current_shop:
            return CustomErrorResponse(status.HTTP_404_NOT_FOUND, "Shop does not exist")

        current_product = self.get_product(current_shop, product_id)
        if not current_product:
            return CustomErrorResponse(status.HTTP_404_NOT_FOUND, "Product does not exist")

        serializer = self.get_serializer(current_product)
        return response.Response({
            'message': 'Product retrieved.',
            'data': serializer.data,
        }, status=status.HTTP_200_OK)

    @swagger_auto_schema(tags=['Shops'])
    def partial_update(self, request, company_id, shop_id, product_id):
        """Update a product in the specified shop"""
        current_company = self.get_company(company_id)
        if not current_company:
            return CustomErrorResponse(status.HTTP_404_NOT_FOUND, "Company does not exist")

        current_shop = self.get_shop(current_company, shop_id)
        if not current_shop:
            return CustomErrorResponse(status.HTTP_404_NOT_FOUND, "Shop does not exist")

        current_product = self.get_product(current_shop, product_id)
        if not current_product:
            return CustomErrorResponse(status.HTTP_404_NOT_FOUND, "Product does not exist")

        serializer = self.get_serializer(instance=current_product, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return response.Response({
                'message': 'Product successfully updated.',
                'data': serializer.data,
            }, status=status.HTTP_200_OK)
        else:
            return CustomErrorResponse(status.HTTP_400_BAD_REQUEST, serializer.errors)

    @swagger_auto_schema(tags=['Shops'])
    def destroy(self, request, company_id, shop_id, product_id):
        """Delete a product from the specified shop"""
        current_company = self.get_company(company_id)
        if not current_company:
            return CustomErrorResponse(status.HTTP_404_NOT_FOUND, "Company does not exist")

        current_shop = self.get_shop(current_company, shop_id)
        if not current_shop:
            return CustomErrorResponse(status.HTTP_404_NOT_FOUND, "Shop does not exist")

        current_product = self.get_product(current_shop, product_id)
        if not current_product:
            return CustomErrorResponse(status.HTTP_404_NOT_FOUND, "Product does not exist")

        current_product.delete()
        return response.Response({
            'message': 'Product successfully deleted.'
        }, status=status.HTTP_204_NO_CONTENT)
