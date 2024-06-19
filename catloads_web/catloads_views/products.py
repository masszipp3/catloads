from django.shortcuts import render,get_object_or_404,redirect
from django.urls import reverse_lazy
from django.views import View
from catloads_web.models import Category,Product,ProductSale,Banner,ProductImages,ProductSaleItems
from catloads_admimn.forms import CategoryForm,ProductForm
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView
from django.db.models import Count, Q
from django.http import JsonResponse   
from django.views.generic import DetailView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator 

class ProductDetailView(DetailView):
    model = ProductSale
    template_name = 'catloads_web/product-default.html'
    context_object_name = 'products'    
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = context['products']
        banners = Banner.objects.filter(is_deleted=False)
        product_images = product.products_images.filter(is_deleted=False).order_by('id')
        product_videos = product.productssale_videos.filter(is_deleted=False).order_by('id')
        categories = product.get_all_categories()
        context['banners'] = banners
        context['products_images'] = product_images
        context['product_discount'] = product.get_discount_percentage()
        context['product_videos'] = product_videos
        context['categories'] = categories
        context['max_price'] = product.get_maxprice()

        
        print(categories)

        return context
