from django.urls import path, re_path
from . import views

urlpatterns = [
    # external shop endpoints
    path('shops/', views.ShopListView.as_view(), name='All Shops list'),
    path('shops/shop/<int:shop_id>/', views.ShopDetailView.as_view(), name='All Shops Detail'),

    # internal shop endpoints
    path('shops/company/<int:company_id>/', views.CompanyShopListCreateView.as_view(), name='company-shop-list-create'),
    path('shops/company/<int:company_id>/shop/<int:shop_id>/', views.CompanyShopManageView.as_view(
        {
            'patch':'partial_update', 
            'delete':'destroy',
            'get':'shop_detail',
        }
        ), name='company-shop-patch-delete-detail'),
    # path('shops/company/<int:company_id>/shop/<int:shop_id>/products/', views.ShopProductListView.as_view(), name='shop-product-list'),        
    path('shops/company/<int:company_id>/shop/<int:shop_id>/products/', views.ShopProductListCreateView.as_view(), name='shop-product-list-create'),
    path('shops/company/<int:company_id>/shop/<int:shop_id>/products/<int:product_id>/', views.ShopProductManageView.as_view(
        {
            'get':'retrieve',
            'patch':'partial_update', 
            'delete':'destroy',
        }
        ), name='shop-product-patch-delete-get'),
]