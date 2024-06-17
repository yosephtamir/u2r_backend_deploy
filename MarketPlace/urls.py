from django.urls import path, re_path
from . import views

urlpatterns = [
    path('marketplace/products/', views.ProductListView.as_view(), name='Product-list'),
    path('marketplace/products/limited-offer/', views.LimitedOfferListView.as_view(), name='limited_offer'),
    path('marketplace/products/popular/', views.ProductRecommendationView.as_view(), name='recommendations'),
    path('marketplace/products/recently-viewed/', views.RecentlyViewedView.as_view(), name='recently_viewed'),
    path('marketplace/products/<int:product_id>/similar-products/', views.SimilarProductListView.as_view(), name='similar-products'), 
    path('marketplace/products/<int:product_id>/product-detail/', views.ProductDetailView.as_view(), name='product-detail'),
    path('marketplace/products/product-filter/', views.FilterProductView.as_view(), name='product-filter'),    
    path('marketplace/products/search/', views.SearchProductView.as_view(), name='product-search'),    

    path('marketplace/categories/',views.CategoryNameView.as_view(), name='category_name'),
    path('marketplace/categories/<int:category_id>/products/',views.CategoryProductListView.as_view(), name='category_products'),
    path('marketplace/categories/<int:category_id>/sub-category/',views.SubCategoryNameView.as_view(), name='sub_category_name'),
    path('marketplace/categories/<int:category_id>/sub-category/<int:subcategory_id>/products/',views.SubCategoryProductListView.as_view(), name='sub_category_products'),

    path('marketplace/shops/<int:shop_id>/',views.ShopDetailView.as_view(), name='shop-detail'),    
    path('marketplace/shops/<int:shop_id>/products',views.ShopProductListView.as_view(), name='shop-products'),

    path('marketplace/me/cart/', views.CartView.as_view({'get':'get_user_cart', 'patch':'update_cart_info'}), name='user-cart-detail'),
    # path('marketplace/me/cart/', views.CartView.as_view({'patch':'update_cart_info'}), name='update-cart-detail'),
    path('marketplace/me/cart/items/', views.CartView.as_view({'get':'get_user_cart_items'}), name='user-cart-items-list'),
    path('marketplace/me/cart/dump/', views.CartView.as_view({'delete':'delete_user_cart_items'}), name='user-cart-dump'),
    path('marketplace/me/cart/add-item/<int:product_id>/', views.CartView.as_view({'post': 'add_cart_item'}), name='add-cart-item'),
    path('marketplace/me/cart/remove-item/<int:product_id>/', views.CartView.as_view({'delete':'remove_cart_item'}), name='remove-cart-item'),
    path('marketplace/me/cart/update-quantity/<int:product_id>/', views.CartView.as_view({'patch':'update_cart_item_quantity'}), name='update_cart_item_quantity'),

    path('marketplace/me/wish-list/', views.WishListView.as_view({'get':'get_user_wishlist'}), name='user-wish-list-detail'),
    path('marketplace/me/wish-list/items/', views.WishListView.as_view({'get':'get_user_wishlist_items'}), name='user-wish-list-items-list'),
    path('marketplace/me/wish-list/dump/', views.WishListView.as_view({'delete':'delete_user_wishlist_items'}), name='user-wish-list-dump'),
    path('marketplace/me/wish-list/add-item/<int:product_id>/', views.WishListView.as_view({'post': 'add_wishlist_item'}), name='add-wish-list-item'),
    path('marketplace/me/wish-list/remove-item/<int:product_id>/', views.WishListView.as_view({'delete':'remove_wishlist_item'}), name='remove-wish-list-item'),

    path('marketplace/me/order/', views.OrderView.as_view({'get':'get_user_order'}), name='user-order-detail'),
    path('marketplace/me/order/items/', views.OrderView.as_view({'get':'get_user_order_items'}), name='user-order-items-list'),
    path('marketplace/me/order/dump/', views.OrderView.as_view({'delete':'delete_user_order_items'}), name='user-order-dump'),
    path('marketplace/me/order/add-item/<int:product_id>/', views.OrderView.as_view({'post': 'add_order_item'}), name='add-order-item'),
    path('marketplace/me/order/remove-item/<int:product_id>/', views.OrderView.as_view({'delete':'remove_order_item'}), name='remove-order-item'),
]