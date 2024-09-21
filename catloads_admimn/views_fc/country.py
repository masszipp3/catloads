from django.shortcuts import render,get_object_or_404,redirect
from django.urls import reverse_lazy
from django.views import View
from catloads_web.models import Category,Product,Country
from catloads_admimn.forms import CountryForm,ProductForm
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView
from django.db.models import Count, Q
from django.http import JsonResponse   
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator 
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponseRedirect
from django.urls import reverse

@method_decorator(login_required, name='dispatch')
class CountryCreateView(UserPassesTestMixin,View):
    template_name = 'catloads_admin/country_create.html'
    form_class = CountryForm
    success_url = 'catloadsadmin:country_list' 

    def test_func(self):
        return self.request.user.is_superuser   
    
    def handle_no_permission(self):
        return HttpResponseRedirect(reverse('catloadsadmin:login'))
    
    def get(self,request,id=None):
        try:
            country = get_object_or_404(Country, id=id) if id else None
            form = self.form_class(instance=country)
            action = 'Add Country' if id is None else 'Update Country'
            return render(request, self.template_name, {"form": form,'action':action})
        except Exception as e:
            print('Error Occured on Loading Category Form')
    
    def post(self,request,id=None):
        try:
            country = get_object_or_404(Country, id=id) if id else None
            form = self.form_class(request.POST,request.FILES, instance=country)
            if form.is_valid():
                form.save()
                return redirect(self.success_url)
            else:
                print(form.errors)
                action = 'Add Country' if id is None else 'Update Country'
                return render(request, self.template_name, {"form": form,'action':action})
        except Exception as e:
            print('Error Occured on Posting Country Form')  

@method_decorator(login_required, name='dispatch')
class CountryListView(ListView):
    model = Country
    template_name = 'catloads_admin/country_list.html'
    context_object_name = 'countries'
    paginate_by = 50
    queryset = Country.objects.filter(is_deleted=False).order_by('-id') 

    def get(self, request, *args, **kwargs):
        if 'search' in self.request.GET:
            keyword=  self.request.GET.get('search','')
            queryset = self.get_queryset().filter(
                Q(name__icontains=keyword) | 
                Q(code__icontains=keyword)
            ) 
            contrieslist = [{
            'id': country.id,
            'name': country.name,
            'code':  country.code,
            'symbol': country.symbol,
            'edit_link': reverse("catloadsadmin:country_edit" , kwargs={'id': country.id}),
            'delete_link': reverse("catloadsadmin:country_delete" , kwargs={'id': country.id}),  
            'status': "Active" if country.active else "Inactive"
        } for country in queryset] 
            return JsonResponse({'contries': contrieslist}, safe=False)
        return super().get(request, *args, **kwargs) 

    



@method_decorator(login_required, name='dispatch')
class CountryDeleteView(View):
    success_url = reverse_lazy('catloadsadmin:country_list')

    def get(self, request,id):
        try:
            instance = get_object_or_404(Country, id=id)
            instance.delete()
        except Exception as e:
            print('User Delete Error', e)
        return redirect(self.success_url)               