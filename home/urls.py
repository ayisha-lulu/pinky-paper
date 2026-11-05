from django.urls import path
from . import views

urlpatterns = [
    path('', views.store_home, name='home'),
    path('product/<int:product_id>/',views.product_detail,name='product_detail'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('edit-profile/',views.edit_profile,name='edit_profile'),
    path('register/', views.register, name='register'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view,name='cart'),
    path('remove-from-cart/<int:product_id>/',views.remove_from_cart,name='remove_from_cart'),
    path('update-cart/<int:product_id>/',views.update_cart,name='update_cart'),
    path('place-order/',views.place_order,name='place_order'),
    path('checkout/',views.checkout,name='checkout'),
    path('add-to-wishlist/<int:product_id>/',views.add_to_wishlist,name='add_to_wishlist'),
    path('wishlist/',views.wishlist_view,name='wishlist'),
    path('remove-from-wishlist/<int:item_id>/',views.remove_from_wishlist,name='remove_from_wishlist'),
    path('orders/',views.order_history,name='order_history'),
    path('orders/<int:order_id>/',views.order_detail,name='order_detail'),
    
]