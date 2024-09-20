from django.shortcuts import render,get_object_or_404,redirect
from django.urls import reverse_lazy
from django.views import View
from catloads_web.models import Category,ProductSale,Product,ProductSaleItems,ProductImages,ProductVideos,Country,CountryPrice
from catloads_admimn.forms import ProductSaleForm
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView
from django.db.models import Count, Q
from django.http import JsonResponse   
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
from catloads_admimn.context_processors import get_countries
import json

class SaleCreateView(UserPassesTestMixin,View):
    template_name = 'catloads_admin/salecreate.html'
    form_class = ProductSaleForm
    success_url = 'catloadsadmin:sale_list' 
    def test_func(self):
        return self.request.user.is_superuser   
    
    def handle_no_permission(self):
        return HttpResponseRedirect(reverse('catloadsadmin:login'))
    def get(self,request,id=None):
        try:
            sale = get_object_or_404(ProductSale, id=id) if id else None
            form = self.form_class(instance=sale)
            action = 'Add Product' if id is None else 'Update Product'
            context =  {"form": form,'action':action}
            if sale :
               sale_items = sale.products_salemaster.all()
               context['sale_items'] = sale_items
               context['description'] = sale.description
            return render(request, self.template_name,context)
        except Exception as e:
            print('Error Occured on Loading Sale Form',e)
    
    def post(self,request,id=None):
        try:
            sale = get_object_or_404(ProductSale, id=id) if id else None
            form = self.form_class(request.POST,request.FILES, instance=sale)
            if form.is_valid():
                instance = form.save()
                if request.POST.getlist('options[]'):
                    productids= request.POST.getlist('options[]')
                    print(productids)
                    instance.products_salemaster.all().delete()
                    # Create new ProductSaleItems for each product ID selected
                    for product_id in productids:
                        product = get_object_or_404(Product, pk=product_id)
                        ProductSaleItems.objects.create(
                            product=product,
                            sale_master=instance
                        )
                if 'multifiles' in request.FILES:
                    self._extracted_from_images(request, instance)
                return redirect(self.success_url)
            else:
                action = 'Add ProductSale' if id is None else 'Update ProductSale'
                return render(request, self.template_name, {"form": form,'action':action})
        except Exception as e:
            print('Error Occured on Posting ProductSale Form', e)    

    def _extracted_from_images(self, request, instance):
        files = request.FILES.getlist('multifiles')
        products_images = ProductImages.objects.filter(
                    product=instance, 
                )
        products_videos = ProductVideos.objects.filter(
                    product=instance, 
                )
        files_sorted_by_name = sorted(files, key=lambda x: x.name)
        if products_images.exists() or products_videos.exists():
            products_images.delete()
            products_videos.delete()
        for file in files_sorted_by_name:
            if file.content_type.startswith('image'):
                ProductImages.objects.create(
                    image=file, 
                    product=instance, 
                )
            elif file.content_type.startswith('video'):
                ProductVideos.objects.create(
                    video=file, 
                    product=instance, 
                )    

class SaleProductsList(UserPassesTestMixin,ListView):
    model = Product
    template_name = 'catloads_admin/salelist.html'
    context_object_name = 'sales'
    paginate_by = 10
    def test_func(self):
        return self.request.user.is_superuser   
    
    def handle_no_permission(self):
        return HttpResponseRedirect(reverse('catloadsadmin:login'))
    def get_queryset(self):
        queryset = ProductSale.objects.filter(is_deleted=False).annotate(
            download_count=Count('order_items', filter=Q(order_items__order__paid=True))).filter(is_deleted=False).order_by('-id')
        return queryset             

class ProductSaleSoftDeleteView(UserPassesTestMixin,View):
    success_url = reverse_lazy('catloadsadmin:sale_list')
    def test_func(self):
        return self.request.user.is_superuser   
    
    def handle_no_permission(self):
        return HttpResponseRedirect(reverse('catloadsadmin:login'))
    def get(self, request,id):
        # Set the product as deleted instead of deleting it
        try:
            instance = get_object_or_404(ProductSale, id=id)
            instance.is_deleted = True
            instance.save()
            instance.products_salemaster.filter().update(is_deleted=True)
            instance.productssale_videos.filter().update(is_deleted=True)
            instance.products_images.filter().update(is_deleted=True)

        except Exception as e:
            print('Product Sale Delete Error', e)
        return redirect(self.success_url)

class ProductPricingList(UserPassesTestMixin,View):
    success_url = reverse_lazy('catloadsadmin:sale_list')
    def test_func(self):
        return self.request.user.is_superuser   
    
    def handle_no_permission(self):
        return HttpResponseRedirect(reverse('catloadsadmin:login'))
    def get(self, request,id):
        try:
            instance = get_object_or_404(ProductSale, id=id)
            country_prices = instance.country_sale_prices.all()
            price_list =[{
                'id':country_price.id,
                'price': country_price.price,
                'country': country_price.country.id,
                'discount':country_price.discount
            }for country_price in country_prices]
            countries = Country.objects.values('id', 'code', 'name', 'symbol')
            countries = list(countries)
            return JsonResponse({'price_list':price_list,'countries':countries},status=200)

        except Exception as e:
            print('Product Sale Delete Error', e)
        return JsonResponse({'error': str(e)}, status=404)       
    
class ProductPricingPOST(UserPassesTestMixin,View):
    success_url = reverse_lazy('catloadsadmin:sale_list')
    def test_func(self):
        return self.request.user.is_superuser   
    
    def handle_no_permission(self):
        return HttpResponseRedirect(reverse('catloadsadmin:login'))
    def post(self, request,id):
        try:
            instance = get_object_or_404(ProductSale, id=id)
            data = json.loads(request.body)
            items = data.get('items', [])
            print(items)
            updated_country_ids = [item.get('country_id') for item in items if item.get('country_id')]
            existing_country_prices = CountryPrice.objects.filter(product_sale=instance)
            for item in items:
                price = item.get('price')
                discount = item.get('discount')
                country_id = item.get('country_id')
                country = get_object_or_404(Country, id=country_id)
                CountryPrice.objects.update_or_create(
                    product_sale=instance,
                    country=country,
                    defaults={
                        'price': price,
                        'discount': discount
                    }
                )
                existing_country_prices.exclude(country__id__in=updated_country_ids).delete()
            return JsonResponse({'status': 'success', 'message': 'Pricing updated successfully'},status=200)
        except Exception as e:
            print('Product Sale Delete Error', e)
            return JsonResponse({'error': str(e)}, status=404)   
