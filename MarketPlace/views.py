from datetime import datetime
from drf_yasg.utils import swagger_auto_schema
from django.http import Http404
from django_filters import rest_framework as filters
from rest_framework import (
    generics,
    viewsets,
    views,
    permissions,
    response,
    status);
from .filters import ProductFilter, ProductSearch
from .models import *
from .serializers import *
from Shop.serializers import ShopSerializer
from helpers.err_response import CustomErrorResponse
from helpers.pagination import PaginatorGenerator


class ProductRecommendationView(generics.ListAPIView):
    """ List recommended Products """
    serializer_class = ProductSerializer
    permission_classes = []

    @swagger_auto_schema(tags=['MarketPlace'])
    def list(self, request):
        try:
            recommended_products = self.get_recommended_products()
            serialized_data = ProductSerializer(recommended_products, many=True).data

            response_data = {
                'status': 200,
                'success': True,
                'message': 'Recommended products',
                'data': serialized_data,
                'page_info': {
                    'count': len(serialized_data),
                }
            }
            return response.Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return CustomErrorResponse(status.HTTP_404_NOT_FOUND, "Product not found")

    def get_recommended_products(self):
        highest_quantity_products = self.get_products_by_highest_quantity()
        highest_discount_products = self.get_products_by_highest_discount()

        return list(
            set(
                highest_quantity_products | highest_discount_products
            )
        )[:20]

    def get_products_by_highest_quantity(self):
        return Product.objects.filter(
            admin_status='approved', is_deleted=False
        ).order_by('-quantity')[:20]
    
    # def get_products_by_highest_rating(self):
    #     return Product.objects.filter(
    #         admin_status='approved', is_deleted=False
    #     ).order_by('-discount_price')[:20]

    def get_products_by_highest_discount(self):
        return Product.objects.filter(
            admin_status='approved', is_deleted=False
        ).order_by('-discount_price')[:20]

class ProductDetailView(generics.GenericAPIView):
    """ A single Product detail """
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(tags=['MarketPlace'])
    def get(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
            serializer = ProductSerializer(product)

            if request.user.is_authenticated:
                user_id = request.user.id
                # Check if an interaction already exists
                existing_interaction = UserProductInteraction.objects.filter(user=user_id, product=product_id).first()
                if existing_interaction:
                    # If interaction exists, update its updated_at field
                    existing_interaction.updated_at = datetime.now()
                    existing_interaction.save()
                else:
                    # If interaction doesn't exist, create a new one
                    interaction_data = {
                        'user': user_id,
                        'product': product_id,
                        'interaction_type': 'Viewed',
                        'created_at': datetime.now(),
                        'updated_at': datetime.now(),
                    }
                    interaction_serializer = UserProductInteractionSerializer(data=interaction_data)
                    if interaction_serializer.is_valid():
                        interaction_serializer.save()
                    else:
                        pass
            else:
                print("user not authenticated")

            response_data = {
                    "status_code": status.HTTP_200_OK,
                    "count": len(serializer.data),
                    "data": serializer.data,
                    "status": "success",
                }
        
            return response.Response(response_data, status=status.HTTP_200_OK)
        except Http404:
            return CustomErrorResponse(status.HTTP_404_NOT_FOUND, "Product Not Found")
        except Exception as e:
            return CustomErrorResponse(status.HTTP_500_INTERNAL_SERVER_ERROR,
                                   f"An error occurred while retrieving Product with id-{product_id}: {str(e)}")
 
class ProductsListBaseView(generics.ListAPIView):
    """ List All Products """
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = PaginatorGenerator()(_page_size=8)

    def get_shop(self, shop_id=None):
        try:
            return Shop.objects.get(id=shop_id)
        except Shop.DoesNotExist:
            return None

    def get_current_category(self, category_id=None):
        try:
            return ProductCategory.objects.get(id=category_id)
        except ProductCategory.DoesNotExist:
            return None
        
    def get_current_subcategory(self, category_id=None, sub_category_id=None):
        parent_category = self.get_current_category(category_id)
        try:
            query = ProductSubCategory.objects.get(parent_category=parent_category, id=sub_category_id)
            return query
        except ProductSubCategory.DoesNotExist:
            return None        

    def get_products(self, request, filters, message):
        try:
            queryset = Product.objects.filter(**filters).order_by('-updated_at')
            page = self.paginate_queryset(queryset)
            print(page)
            
            if page is not None:
                serializer = self.serializer_class(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.serializer_class(queryset, many=True)
            # No pagination, return all data
            response_data = {
                "status_code": status.HTTP_200_OK,
                "message": message,
                "data": serializer.data,
                "status": "success",
                "page_info": {
                    "count": len(serializer.data),
                }
            }
            return response.Response(response_data, status=status.HTTP_200_OK)
        
        except Http404:
            return CustomErrorResponse(status.HTTP_404_NOT_FOUND, "Product Not Found")
        except Exception as e:
            return CustomErrorResponse(status.HTTP_500_INTERNAL_SERVER_ERROR,
                                f"An error occurred while retrieving {message}: {str(e)}")

class ProductListView(ProductsListBaseView):
    """ List All Products """

    @swagger_auto_schema(tags=['MarketPlace'])
    def list(self, request):
        products = self.get_products(request, {}, "All Products")
        if products:
            return products
        else:
            return CustomErrorResponse(status.HTTP_404_NOT_FOUND, "Product not found") 

class CategoryProductListView(ProductsListBaseView):
    """ List Products in the same category """

    @swagger_auto_schema(tags=['MarketPlace'])
    def list(self, request, category_id):
        current_category = self.get_current_category(category_id)
        if current_category:
            return self.get_products(
                request,
                {
                    'category': current_category,
                },
                f"{current_category} Category Products",
            )
        else:
            return CustomErrorResponse(status.HTTP_404_NOT_FOUND, "Product not found")

class SubCategoryProductListView(ProductsListBaseView):
    """ List Products in the same category """

    @swagger_auto_schema(tags=['MarketPlace'])
    def list(self, request, category_id, subcategory_id):
        current_category = self.get_current_category(category_id)
        current_sub_category = self.get_current_subcategory(category_id, subcategory_id)
        if current_category:
            return self.get_products(
                request,
                {
                    'category': current_category,
                    'sub_category': current_sub_category,
                },
                f"{current_sub_category} Sub-Category Products",
            )
        else:
            return CustomErrorResponse(status.HTTP_404_NOT_FOUND, "Product not found")

class ShopProductListView(ProductsListBaseView):
    """ List Products in the a shop """

    @swagger_auto_schema(tags=['MarketPlace'])
    def list(self, request, shop_id):
        current_shop = self.get_shop(shop_id)
        if current_shop:
            return self.get_products(
                request,
                {
                    'shop': current_shop,
                },
                f"{current_shop} Shop Products",
            )
        else:
            return CustomErrorResponse(status.HTTP_404_NOT_FOUND, "Product not found")  

class ShopDetailView(generics.GenericAPIView):
    """ A Shop detail """
    serializer_class = ShopSerializer
    permission_classes = []

    @swagger_auto_schema(tags=['MarketPlace'])
    def get(self, request, shop_id):
        try:
            current_shop = Shop.objects.get(id=shop_id)
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
        
class SimilarProductBaseView(generics.ListAPIView):
    """ Base class for listing similar products """
    serializer_class = ProductSerializer
    permission_classes = []

    def get_current_product(self, product_id):
        try:
            return Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return None

    def get_similar_products(self, filters, product_id, message):
        try:
            queryset = Product.objects.filter(**filters).exclude(id=product_id)
            similar_products = queryset[:4]
            serializer = ProductSerializer(similar_products, many=True)

            response_data = {
                "status_code": status.HTTP_200_OK,
                "page_info": {
                    "count": len(serializer.data),
                },
                "message": message,
                "data": serializer.data,
                "status": "success",
            }

            return response.Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return CustomErrorResponse(status.HTTP_500_INTERNAL_SERVER_ERROR,
                                   f"An error occurred while retrieving {message}: {str(e)}")        

class SimilarProductListView(SimilarProductBaseView):
    """ List Similar Products with the currently viewed product """

    @swagger_auto_schema(tags=['MarketPlace'])
    def list(self, request, product_id):      
        current_product = self.get_current_product(product_id)
        if current_product:
            return self.get_similar_products(
                {
                    'category': current_product.category,
                    'sub_category': current_product.sub_category
                },
                product_id,
                "Similar products",
            )
        else:
            return CustomErrorResponse(status.HTTP_404_NOT_FOUND, "Product not found")
      
class LimitedOfferListView(generics.ListAPIView):
    """ List Limited Offer Products """
    serializer_class = ProductSerializer
    permission_classes = []
    

    @swagger_auto_schema(tags=['MarketPlace'])
    def list(self, request):
        try:
            queryset = Product.objects.filter(has_discount=True).exclude(discount_price=None).order_by('discount_price')

            serializer = self.get_serializer(queryset, many=True)
            req_response = {
                'success': True,
                'status': 200,
                'error': None,
                'message': 'Successfully Fetched Limited Offer Products',
                'data': serializer.data,
                'page_info': {
                    'count': len(serializer.data),
                }
            }

            return response.Response(req_response, status=status.HTTP_200_OK)
        except Http404:
            return CustomErrorResponse(status.HTTP_404_NOT_FOUND, "Not Found")
        except Exception as e:
            return CustomErrorResponse(status.HTTP_400_BAD_REQUEST, str(e))
        
class RecentlyViewedView(generics.ListAPIView, generics.DestroyAPIView):
    """
    Retrieve and delete recently viewed products for a specific user.
    """
    serializer_class = UserProductInteractionSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = UserProductInteraction.objects.filter(interaction_type='Viewed').order_by('updated_at')

    def list(self, request):
        """
        List recently viewed products for the authenticated user.
        """
        queryset = self.get_queryset().filter(user=request.user).select_related('product').order_by('updated_at')
        serializer = self.serializer_class(queryset, many=True)

        interaction_data = serializer.data
        # Extract product IDs from the interactions
        product_ids = [interaction['product'] for interaction in interaction_data]

        # Fetch product objects based on the IDs
        products = Product.objects.filter(id__in=product_ids)
        product_serializer = ProductSerializer(products, many=True)

        return response.Response({
                'success': True,
                'status': 200,
                'error': None,
                'message': "Recently viewed products.",
                'data': product_serializer.data,
                'interaction_data': serializer.data,
                'page_info': {
                    'count': len(serializer.data),
                }
            }, status=status.HTTP_200_OK)         

    def destroy(self, request):
        """
        Delete recently viewed products for a specific user.
        """
        deleted_count, _ = self.get_queryset().filter(user=request.user).delete()
        if deleted_count > 0:
            return response.Response({
                'success': True,
                'status': 200,
                'error': None,
                'message': "Recently viewed products deleted successfully",
                'data': {'deleted_count': deleted_count},
            }, status=status.HTTP_200_OK)
        else:
            return CustomErrorResponse(status.HTTP_404_NOT_FOUND, "No recently viewed products to delete")
        
class CategoryNameView(generics.ListAPIView):
    """
    List Category Names
    """
    serializer_class = ProductCategorySerializer
    permission_classes = []

    @swagger_auto_schema(tags=['MarketPlace'])
    def list(self, request):
        try:
            queryset = ProductCategory.objects.all()
            serializer = ProductCategorySerializer(queryset, many=True)

            response_data = {
                'status': status.HTTP_200_OK,
                'success': True,
                'message': 'Category names returned successfully',
                'data': serializer.data
            }

            return response.Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return CustomErrorResponse(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))
        
class SubCategoryNameView(generics.ListAPIView):
    """
    List Category Names
    """
    serializer_class = ProductSubCategorySerializer
    permission_classes = []

    @swagger_auto_schema(tags=['MarketPlace'])
    def list(self, request, category_id):
        try:
            category = ProductCategory.objects.filter(id=category_id)
            queryset = ProductSubCategory.objects.filter(parent_category=category[:1])
            serializer = ProductSubCategorySerializer(queryset, many=True)

            response_data = {
                'status': status.HTTP_200_OK,
                'success': True,
                'message': 'SubCategory names returned successfully',
                'data': serializer.data
            }

            return response.Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return CustomErrorResponse(status.HTTP_500_INTERNAL_SERVER_ERROR, f'An unexpected error occurred')  

class CartView(viewsets.GenericViewSet):

    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PaginatorGenerator()(_page_size=15)

    def get_serializer_class(self):
        if self.action in ['get_user_cart', 'update_cart_info']:
            return CartSerializer
        elif self.action in ['get_user_cart_items', 'add_cart_item', 'update_cart_item_quantity']:
            return CartItemSerializer

    @swagger_auto_schema(tags=['MarketPlace'])
    def get_user_cart(self, request, *args, **kwargs):
        "API Viewset to get the currently authenticated user's cart"
        cart, created = Cart.objects.get_or_create(owner=request.user)
        serializer = self.get_serializer(cart, many=False)
        data = {**serializer.data, **{'new_cart':created}}
        return response.Response(data, status=status.HTTP_200_OK)

    @swagger_auto_schema(tags=['MarketPlace'])
    def update_cart_info(self, request, *args, **kwargs):
        "API Viewset to update the currently authenticated user's delivery address"
        cart = Cart.objects.get(owner=request.user)
        serializer = self.get_serializer(cart, data=request.data, partial=True, many=False)
        if serializer.is_valid():
            serializer.save()
            return response.Response({
                'message': 'Delivery Address successfully updated.',
                'data': serializer.data,
            }, status=status.HTTP_200_OK)
        else:
            return CustomErrorResponse(status.HTTP_400_BAD_REQUEST, serializer.errors)

    @swagger_auto_schema(tags=['MarketPlace'])
    def add_cart_item(self, request, product_id, *args, **kwargs):
        "API Viewset to add an item to the currently authenticated user's cart"
        cart, created = Cart.objects.get_or_create(owner=request.user)
        product = Product.objects.get(id=product_id)
        already_in_cart = CartItem.objects.filter(cart=cart, product=product)
        if not already_in_cart:
            item_data = {}
            item_data['cart'] = cart.id
            item_data['product'] = product_id

            serializer = self.get_serializer(data=item_data)
            if serializer.is_valid():
                serializer.save()
                return response.Response(serializer.data, status=status.HTTP_201_CREATED)
            print(serializer.errors)
            return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return response.Response({'message': 'Item is already in Cart'}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(tags=['MarketPlace'])
    def remove_cart_item(self, request, product_id, *args, **kwargs):
        "API Viewset to remove an item from the currently authenticated user's cart"
        try:
            cart = Cart.objects.get(owner=request.user)
            product = Product.objects.get(id=product_id)
            queryset = CartItem.objects.filter(cart=cart, product=product)
            print("queryset: ", queryset, "product: ", product, "cart: ", cart)
            if queryset.exists():
                queryset.delete()
                return response.Response({"data": "item removed"}, status=status.HTTP_204_NO_CONTENT)
            else:
                return response.Response({"message": "Item not found"}, status=status.HTTP_404_NOT_FOUND)       
        except Cart.DoesNotExist:
            raise Http404("Cart not found")
        except Product.DoesNotExist:
            return response.Response({"message": "Product does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return response.Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(tags=['MarketPlace'])
    def get_user_cart_items(self, request, *args, **kwargs):
        "API Viewset to get the currently authenticated user's cart items"
        cart = Cart.objects.get(owner=request.user)
        queryset = CartItem.objects.filter(cart=cart)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return response.Response(serializer.data)

    @swagger_auto_schema(tags=['MarketPlace'])
    def delete_user_cart_items(self, request, *args, **kwargs):
        "API Viewset to delete the currently authenticated user's cart items"
        cart = Cart.objects.get(owner=request.user)
        queryset = CartItem.objects.filter(cart=cart)
        for cartitem in queryset:
            cartitem.delete()
        return response.Response({
            "message":"Cart successfully cleared."
        }, status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(tags=['MarketPlace'])
    def update_cart_item_quantity(self, request, product_id=None):
        """
        API Viewset to update the quantity of an item in the user's cart.
        """
        cart = Cart.objects.get(owner=request.user)
        try:
            cart_item = CartItem.objects.get(cart=cart, product=product_id)
        except CartItem.DoesNotExist:
            return response.Response({
                "message": "Cart item not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Parse the quantity adjustment from the request data
        quantity_adjustment = request.data.get('quantity')
        
        # Validate the quantity adjustment and update the cart item quantity
        if quantity_adjustment is not None:
            try:
                new_quantity = int(quantity_adjustment)
                # Ensure new quantity is greater than 0
                if new_quantity > 0:
                    cart_item.quantity = new_quantity
                    cart_item.save()
                    serializer = self.get_serializer(cart_item)
                    return response.Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return response.Response({
                        "message": "Invalid quantity adjustment. Quantity must be greater than 0."
                    }, status=status.HTTP_400_BAD_REQUEST)
            except ValueError:
                return response.Response({
                    "message": "Invalid quantity adjustment. Must be an integer."
                }, status=status.HTTP_400_BAD_REQUEST)      
        return response.Response({
            "message": "Quantity adjustment is required"
        }, status=status.HTTP_400_BAD_REQUEST)
    
class OrderView(viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PaginatorGenerator()(_page_size=15)

    def get_serializer_class(self):
        if self.action in ['get_user_order']:
            return OrderSerializer
        elif self.action in ['get_user_order_items', 'add_order_item']:
            return OrderItemSerializer

    @swagger_auto_schema(tags=['MarketPlace'])
    def get_user_order(self, request, *args, **kwargs):
        "API Viewset to get the currently authenticated user's order history"
        order, created = Order.objects.get_or_create(customer=request.user)
        serializer = self.get_serializer(order, many=False)
        data = {**serializer.data, **{'new_order_history':created}}
        return response.Response(data, status=status.HTTP_200_OK)

    @swagger_auto_schema(tags=['MarketPlace'])
    def add_order_item(self, request, product_id, *args, **kwargs):
        "API Viewset to add an item to the currently authenticated user's order history"
        try:
            order, created = Order.objects.get_or_create(customer=request.user)
            product = Product.objects.get(id=product_id)
        except Order.DoesNotExist:
            return response.Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)
        except Product.DoesNotExist:
            return response.Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        item_data = {}
        item_data['order'] = order.id
        item_data['product'] = product_id
        item_data['customer'] = request.user.id
        item_data['merchant_company'] = product.company.id
        item_data['order_price'] = product.price
        item_data['order_tax'] = product.tax
        item_data['order_discount'] = product.discount_price if product.discount_price else 0
        # item_data['promo'] = product.company

        serializer = self.get_serializer(data=item_data)
        if serializer.is_valid():
            serializer.save()
            return response.Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(tags=['MarketPlace'])
    def remove_order_item(self, request, product_id, *args, **kwargs):
        "API Viewset to remove an item from the currently authenticated user's order history"
        try:
            order = Order.objects.get(customer=request.user)
            product = Product.objects.get(id=product_id)
            queryset = OrderItem.objects.filter(order=order, product=product)
            print("queryset: ", queryset, "product: ", product, "order: ", order)
            if queryset.exists():
                queryset.delete()
                return response.Response({"data": "item removed"}, status=status.HTTP_204_NO_CONTENT)
            else:
                return response.Response({"message": "Item not found"}, status=status.HTTP_404_NOT_FOUND)       
        except Order.DoesNotExist:
            raise Http404("Order not found")
        except Product.DoesNotExist:
            return response.Response({"message": "Product does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return response.Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(tags=['MarketPlace'])
    def get_user_order_items(self, request, *args, **kwargs):
        "API Viewset to get the currently authenticated user's order items"
        order = Order.objects.get(customer=request.user)
        queryset = OrderItem.objects.filter(order=order)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return response.Response(serializer.data)

    @swagger_auto_schema(tags=['MarketPlace'])
    def delete_user_order_items(self, request, *args, **kwargs):
        "API Viewset to delete the currently authenticated user's all order items"
        order = Order.objects.get(customer=request.user)
        queryset = OrderItem.objects.filter(order=order)
        for orderItem in queryset:
            orderItem.delete()
        return response.Response({
            "message":"Order History successfully cleared."
        }, status=status.HTTP_204_NO_CONTENT)

class WishListView(viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PaginatorGenerator()(_page_size=15)

    def get_serializer_class(self):
        if self.action=='get_user_wishlist':
            return WishListSerializer
        elif self.action in ['get_user_wishlist_items', 'add_wishlist_item']:
            return WishListItemSerializer

    @swagger_auto_schema(tags=['MarketPlace'])
    def get_user_wishlist(self, request, *args, **kwargs):
        "API Viewset to get the currently authenticated user's wishlist"
        wishlist, created = Wishlist.objects.get_or_create(owner=request.user)
        serializer = self.get_serializer(wishlist, many=False)
        data = {**serializer.data, **{'new_wishlist': created, 'items_count': len(serializer.data)}}
        return response.Response(data, status=status.HTTP_200_OK)

    @swagger_auto_schema(tags=['MarketPlace'])
    def get_user_wishlist_items(self, request, *args, **kwargs):
        "API Viewset to get the currently authenticated user's wishlist items"
        wishlist = Wishlist.objects.get(owner=request.user)
        queryset = WishlistItem.objects.filter(wishlist=wishlist)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return response.Response(serializer.data)

    @swagger_auto_schema(tags=['MarketPlace'])
    def add_wishlist_item(self, request, product_id, *args, **kwargs):
        "API Viewset to add an item to the currently authenticated user's wishlist"
        wishlist, created = Wishlist.objects.get_or_create(owner=request.user)
        product = Product.objects.get(id=product_id)
        already_in_wishlist = WishlistItem.objects.filter(wishlist=wishlist, product=product)
        if not already_in_wishlist:
            item_data = {}
            item_data['wishlist'] = wishlist.id
            item_data['product'] = product_id

            serializer = self.get_serializer(data=item_data)
            if serializer.is_valid():
                serializer.save()
                return response.Response(serializer.data, status=status.HTTP_201_CREATED)
            print(serializer.errors)
            return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)      
        else:
            return response.Response({'message': 'Item is already in Wish List'}, status=status.HTTP_400_BAD_REQUEST)


    @swagger_auto_schema(tags=['MarketPlace'])
    def remove_wishlist_item(self, request, product_id, *args, **kwargs):
        "API Viewset to remove an item from the currently authenticated user's wishlist"
        try:
            wishlist = Wishlist.objects.get(owner=request.user)
            product = Product.objects.get(id=product_id)
            queryset = WishlistItem.objects.filter(wishlist=wishlist, product=product)
            print("queryset: ", queryset, "product: ", product, "wishlist: ", wishlist)
            if queryset.exists():
                queryset.delete()
                return response.Response({"data": "item removed"}, status=status.HTTP_204_NO_CONTENT)
            else:
                return response.Response({"message": "Item not found"}, status=status.HTTP_404_NOT_FOUND)       
        except Wishlist.DoesNotExist:
            raise Http404("Wishlist not found")
        except Product.DoesNotExist:
            return response.Response({"message": "Product does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return response.Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(tags=['MarketPlace'])
    def delete_user_wishlist_items(self, request, *args, **kwargs):
        "API Viewset to delete the currently authenticated user's wishlist items"
        wishlist = Wishlist.objects.get(owner=request.user)
        queryset = WishlistItem.objects.filter(wishlist=wishlist)
        for wishListItem in queryset:
            wishListItem.delete()
        return response.Response({
            "message": "WishList successfully cleared."
        }, status=status.HTTP_204_NO_CONTENT)
    
class FilterProductView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = Product.objects.filter(is_deleted=False)  # Fetch non-deleted products
    serializer_class = ProductSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ProductFilter
    pagination_class = PaginatorGenerator()(_page_size=8)

    def list(self, request, *args, **kwargs):
        # Add extra handling for custom responses
        responseResult = super().list(request, *args, **kwargs)
        response_data = {
            "success": True,
            "status": 200,
            "error": None,
            "message": "Filtered Products retrieved successfully.",
            "data": responseResult.data,
            "page_info": {
                "count": self.paginator.page.paginator.count,
                "next": self.paginator.get_next_link(),
                "previous": self.paginator.get_previous_link(),
            }
        }
        return response.Response(response_data, status=200)

    def handle_exception(self, exc):
        # Customize error responses
        if isinstance(exc, Exception):
            return CustomErrorResponse(status.HTTP_400_BAD_REQUEST, str(exc))
        return super().handle_exception(exc)

class SearchProductView(generics.ListAPIView):
    permission_classes = []
    queryset = Product.objects.filter(is_deleted=False)  # Fetch non-deleted products
    serializer_class = ProductSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ProductSearch
    pagination_class = PaginatorGenerator()(_page_size=8)

    def list(self, request, *args, **kwargs):
        # Add extra handling for custom responses
        responseResult = super().list(request, *args, **kwargs)
        response_data = {
            "success": True,
            "status": 200,
            "error": None,
            "message": "Searched Products retrieved successfully.",
            "data": responseResult.data,
            "page_info": {
                "count": self.paginator.page.paginator.count,
                "next": self.paginator.get_next_link(),
                "previous": self.paginator.get_previous_link(),
            }
        }
        return response.Response(response_data, status=200)

    def handle_exception(self, exc):
        # Customize error responses
        if isinstance(exc, Exception):
            return CustomErrorResponse(status.HTTP_400_BAD_REQUEST, str(exc))
        return super().handle_exception(exc)        