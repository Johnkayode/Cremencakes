from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import CustomAuthForm

urlpatterns = [
    path('', views.home, name='home'),
    path('shop/', views.shop, name='shop'),
    path('shop/<slug:category_slug>/', views.shop, name='shop_by_category'),
    path('shop/<slug:category_slug>/<slug:slug>/', views.product_detail, name='product_detail'), 
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('cart/update-item/', views.updateItem, name='update_item'),
    path('checkout/process-order/', views.processOrder, name='process_order'),
    path('account/login', auth_views.LoginView.as_view(authentication_form=CustomAuthForm), name = 'login'),
    path('account/logout', auth_views.LogoutView.as_view(), name='logout'),
    path('order-history', views.orders, name='orders'),
    path('myadmin/shop/order/<int:order_id>/detail', views.admin_order_detail, name='admin_order_detail'),
    path('myadmin/shop/order/<int:order_id>/pdf', views.admin_order_pdf, name='admin_order_pdf'),
    path('account/register', views.register, name='register'),
    path('subscription/', views.email_subscribe, name='subscribe'),
     path('feedback/', views.feedback, name='feedback')
]


