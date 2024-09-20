from django.urls import path
from catloads_admimn.views_fc import (dashboard,product,promocode,banner,order,users,sale,login)

app_name= "catloadsadmin"

urlpatterns=[
    #------------------------- Dashboard ------------------------------------------------

    path('',dashboard.DashboardView.as_view(),name='dashboard'),

    #------------------------- Login ------------------------------------------------

    path('login',login.LoginView.as_view(),name='login'),


    #------------------------- Product Category Management----------------------------------

    path('category/create',product.CategoryCreateView.as_view(),name='category_create'),
    path('category/<int:id>/edit',product.CategoryCreateView.as_view(),name='category_edit'),
    path('category/list',product.CategoryListView.as_view(),name='category_list'),
    path('category/<int:id>/delete',product.CategorySoftDeleteView.as_view(),name='category_delete'),

    #------------------------- Product Management-------------------------------------------

    path('product/create',product.ProductCreateUpdateView.as_view(),name='product_create'),
    path('product/<int:id>/edit',product.ProductCreateUpdateView.as_view(),name='product_edit'),
    path('product/list',product.ProductListView.as_view(),name='product_list'),
    path('product/<int:id>/delete',product.ProductSoftDeleteView.as_view(),name='product_delete'),

    #------------------------- PromoCode Management-----------------------------------------

    path('promocode/create',promocode.PromoCodeCreateUpdateView.as_view(),name='promocode_create'),
    path('promocode/<int:id>/edit',promocode.PromoCodeCreateUpdateView.as_view(),name='promocode_edit'),
    path('promocode/list',promocode.PromoCodeListView.as_view(),name='promocode_list'),
    path('promocode/<int:id>/delete',promocode.PromoCodeSoftDeleteView.as_view(),name='promocode_delete'),

    #------------------------- Banner Management---------------------------------------------

    path('banner/create',banner.BannerCreateUpdateView.as_view(),name='banner_create'),
    path('banner/<int:id>/update',banner.BannerCreateUpdateView.as_view(),name='banner_edit'),
    path('banner/<int:id>/delete',banner.BannerSoftDeleteView.as_view(),name='banner_delete'),
    path('banner/list',banner.BannerListView.as_view(),name='bannerlist'),

    #------------------------- Order Management----------------------------------------------

    path('order/list',order.OrderListView.as_view(),name='orderlist'),
    path('order/<int:pk>/detail',order.OrderDetailView.as_view(),name='order_detail'),
    path('order/<int:id>/update',order.OrderUpdateView.as_view(),name='order_update'),
    path('order/<int:id>/delete',order.OrderSoftDeleteView.as_view(),name='order_delete'),
    path('order/data/excel',order.ExportOrderExcel.as_view(),name='order_excel'),


    #------------------------- User Management----------------------------------------------

    path('user/list',users.UsersListView.as_view(),name='userlist'),
    path('user/<int:id>/delete',users.UserSoftDeleteView.as_view(),name='user_delete'),
    path('user/export/download',users.ExportUserExcel.as_view(),name='export_user'),

    
    #------------------------- Sale Management----------------------------------------------

    path('sale/create',sale.SaleCreateView.as_view(),name='sale_create'),
    path('sale/<int:id>/edit',sale.SaleCreateView.as_view(),name='sale_edit'),
    path('sale/<int:id>/delete',sale.ProductSaleSoftDeleteView.as_view(),name='sale_delete'),
    path('sale/list',sale.SaleProductsList.as_view(),name='sale_list'),
    path('sale/prices/<int:id>',sale.ProductPricingList.as_view(),name='pricinglist'),
    path('salesprice/update/<int:id>',sale.ProductPricingPOST.as_view(),name='pricingupdate'),






















    





]