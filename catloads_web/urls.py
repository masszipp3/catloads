from django.urls import path
from .catloads_views import (homepage,products,customer,order)

app_name= "catloads_web"


urlpatterns=[

    #------------------------- Dashboard ------------------------------------------------

    path('',homepage.DashboardView.as_view(),name='dashboard'),
    path('product/<slug:slug>',products.ProductDetailView.as_view(),name='product_detail'),
    path('customer/dashboard',customer.CustomerDahsboard.as_view(),name='product_dashboard'),
    path('customer/register',customer.CustomerRegistrationUpdateView.as_view(),name='registration'),
    path('customer/login',customer.LoginView.as_view(),name='login'),
    path('customer/cart',order.CartView.as_view(),name='carts'),
    path('customer/order/<str:encoded_id>',order.OrderCreate.as_view(),name='order_create'),
    path('customer/order',order.OrderCreate.as_view(),name='order_creates'),
    path('promocode/check',order.PromocodeCheck.as_view(),name='promocode_check'),
    path('order/confirm',order.OrderConfirmView.as_view(),name='order_confirm'),
    path('customer/logout',homepage.LogoutView.as_view(),name='logout'),
    path('customer/cartdata',customer.CartDataView.as_view(),name='cartdata'),
    path('customer/downloads',customer.CustomerDowloads.as_view(),name='downloads'),
    path('customer/orders',customer.CustomerOrders.as_view(),name='orders'),
    path('customer/edit',customer.AccountUpdateView.as_view(),name='edit_account'),
    path('customer/search',customer.ProductListView.as_view(),name='productsearch'),
    path('privacy_policy',customer.CustomerPrivacyPolicy.as_view(),name='privacy_policy'),
    path('terms_and_condition',customer.CustomerTerms.as_view(),name='terms_and_condition'),
    path('contact',customer.CustomerContact.as_view(),name='customer_contact'),
    path('login/redirect',customer.direct_google_login,name='login_redirect'),



















]