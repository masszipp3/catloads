from django.shortcuts import render,get_object_or_404,redirect
from django.urls import reverse_lazy
from django.views import View
from catloads_web.models import Category,Product
from catloads_admimn.forms import CategoryForm,ProductForm
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView
from django.db.models import Count, Q
from django.http import JsonResponse   
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator 
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponseRedirect
from django.urls import reverse

#-----------------------------------Category Create / Update/ List/ Delete ----------------------------------------


@method_decorator(login_required, name='dispatch')
class CategoryCreateView(UserPassesTestMixin,View):
    template_name = 'catloads_admin/new-category.html'
    form_class = CategoryForm
    success_url = 'catloadsadmin:category_list' 

    def test_func(self):
        return self.request.user.is_superuser   
    
    def handle_no_permission(self):
        return HttpResponseRedirect(reverse('catloadsadmin:login'))
    
    def get(self,request,id=None):
        try:
            category = get_object_or_404(Category, id=id) if id else None
            form = self.form_class(instance=category)
            action = 'Add Category' if id is None else 'Update Category'
            return render(request, self.template_name, {"form": form,'action':action})
        except Exception as e:
            print('Error Occured on Loading Category Form')
    
    def post(self,request,id=None):
        try:
            category = get_object_or_404(Category, id=id) if id else None
            form = self.form_class(request.POST,request.FILES, instance=category)
            if form.is_valid():
                form.save()
                return redirect(self.success_url)
            else:
                action = 'Add Category' if id is None else 'Update Category'
                return render(request, self.template_name, {"form": form,'action':action})
        except Exception as e:
            print('Error Occured on Posting Category Form')    

@method_decorator(login_required, name='dispatch')
class CategoryListView(UserPassesTestMixin,ListView):
    model = Category
    template_name = 'catloads_admin/category-list.html'
    context_object_name = 'categories'
    paginate_by = 10

    def test_func(self):
        return self.request.user.is_superuser   
    
    def handle_no_permission(self):
        return HttpResponseRedirect(reverse('catloadsadmin:login'))

    def get_queryset(self):
        queryset = Category.objects.filter(is_deleted=False).annotate(
            product_count=Count('products_category', filter=Q(products_category__is_deleted=False))
        )
        queryset = queryset.annotate(
            download_count=Count('products_category__products_sale__order_items', filter=Q(products_category__products_sale__order_items__order__paid=True))).filter(is_deleted=False).order_by('-id')   
        return queryset
@method_decorator(login_required, name='dispatch')
class CategorySoftDeleteView(UserPassesTestMixin,View):
    success_url = reverse_lazy('catloadsadmin:category_list')

    def test_func(self):
        return self.request.user.is_superuser   
    
    def handle_no_permission(self):
        return HttpResponseRedirect(reverse('catloadsadmin:login'))
    def get(self, request,id):
        # Set the product as deleted instead of deleting it
        try:
            instance = get_object_or_404(Category, id=id)
            instance.is_deleted = True
            instance.save()
        except Exception as e:
            print('Category Delete Error', e)
        return redirect(self.success_url)


#-----------------------------------Product Create / Update/ List/Delete ----------------------------------------
@method_decorator(login_required, name='dispatch')
class ProductCreateUpdateView(UserPassesTestMixin,View):
    template_name = 'catloads_admin/add-product.html'
    form_class = ProductForm
    success_url = 'catloadsadmin:product_list' 

    def test_func(self):
        return self.request.user.is_superuser   
    
    def handle_no_permission(self):
        return HttpResponseRedirect(reverse('catloadsadmin:login'))
    
    def get(self,request,id=None):
        try:    
            product = get_object_or_404(Product, id=id) if id else None
            form = self.form_class(instance=product)
            action = 'Add Product' if id is None else 'Update Product'
            return render(request, self.template_name, {"form": form,'action':action})
        except Exception as e:
            print('Product Create Page Loading Error', e)
            
    def post(self,request,id=None):
        try: 
            product = get_object_or_404(Product, id=id) if id else None
            form = self.form_class(request.POST,request.FILES, instance=product)
            if form.is_valid():
                form.save()
                return redirect(self.success_url)
            else:
                action = 'Add Product' if id is None else 'Update Product'
                return render(request, self.template_name, {"form": form,'action':action})
        except Exception as e:
            print('Product Posting Error', e)
@method_decorator(login_required, name='dispatch')
class ProductListView(UserPassesTestMixin,ListView):
    model = Product
    template_name = 'catloads_admin/product-list.html'
    context_object_name = 'products'
    paginate_by = 10
    queryset = Product.objects.filter(is_deleted=False)

    def test_func(self):
        return self.request.user.is_superuser   
    
    def handle_no_permission(self):
        return HttpResponseRedirect(reverse('catloadsadmin:login'))

    def get(self, request, *args, **kwargs):
        if 'search' in self.request.GET:
            keyword=  self.request.GET.get('search','')
            queryset = self.get_queryset().filter(
                Q(name__icontains=keyword) | 
                Q(product_code__icontains=keyword)
            ) 
            products_list = [{
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'download_count': product.download_count,
            'product_code': product.product_code,
            'product_size': product.product_size,
            'product_unit': product.get_unit_display()  # using the model method to get the human-readable unit
        } for product in queryset] 
            return JsonResponse({'products': products_list}, safe=False)
        return super().get(request, *args, **kwargs) 
    def get_queryset(self):
        queryset = Product.objects.filter(is_deleted=False).annotate(
            download_count=Count('products_sale__order_items', filter=Q(products_sale__order_items__order__paid=True))).filter(is_deleted=False).order_by('-id')
        return queryset   
                 
@method_decorator(login_required, name='dispatch')  
class ProductSoftDeleteView(UserPassesTestMixin,View):
    success_url = reverse_lazy('catloadsadmin:product_list')
    def test_func(self):
        return self.request.user.is_superuser   
    
    def handle_no_permission(self):
        return HttpResponseRedirect(reverse('catloadsadmin:login'))
    def get(self, request,id):
        # Set the product as deleted instead of deleting it
        try:
            instance = get_object_or_404(Product, id=id)
            instance.is_deleted = True
            instance.save()
        except Exception as e:
            print('Product Delete Error', e)
        return redirect(self.success_url)