from django.shortcuts import render,get_object_or_404,redirect
from django.urls import reverse_lazy
from django.views import View
from catloads_web.models import Category,ProductSale,Product,ProductSaleItems,ProductImages,ProductVideos
from catloads_admimn.froms import ProductSaleForm
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView
from django.db.models import Count, Q
from django.http import JsonResponse   

class SaleCreateView(View):
    template_name = 'catloads_admin/salecreate.html'
    form_class = ProductSaleForm
    success_url = 'catloadsadmin:category_list' 

    def get(self,request,id=None):
        try:
            sale = get_object_or_404(ProductSale, id=id) if id else None
            form = self.form_class(instance=sale)
            action = 'Add Product' if id is None else 'Update Product'
            context =  {"form": form,'action':action}
            if sale :
               sale_items = sale.products_salemaster.all()
               context['sale_items'] = sale_items
            return render(request, self.template_name,context)
        except Exception as e:
            print('Error Occured on Loading Sale Form')
    
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
                if 'multifiles' in request.FILES :
                    files = request.FILES.getlist('multifiles')
                    for file in files:
                        if file.content_type.startswith('image'):
                            ProductImages.objects.create(image=file, product=instance)
                        elif file.content_type.startswith('video'):
                            ProductVideos.objects.create(video=file, product=instance)
                return redirect(self.success_url)
            else:
                action = 'Add ProductSale' if id is None else 'Update ProductSale'
                return render(request, self.template_name, {"form": form,'action':action})
        except Exception as e:
            print('Error Occured on Posting ProductSale Form', e)    

class SaleProductsList(ListView):
    model = Product
    template_name = 'catloads_admin/salelist.html'
    context_object_name = 'sales'
    paginate_by = 10

    def get_queryset(self):
        queryset = ProductSale.objects.filter(is_deleted=False).annotate(
            download_count=Count('order_items', filter=Q(order_items__order__paid=True))).filter(is_deleted=False).order_by('-id')
        return queryset             

class ProductSaleSoftDeleteView(View):
    success_url = reverse_lazy('catloadsadmin:sale_list')

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

            