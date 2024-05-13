from django.shortcuts import render,get_object_or_404,redirect
from django.urls import reverse_lazy
from django.views import View
from catloads_web.models import Banner
from catloads_admimn.froms import PromoCodeForm,BannerForm
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView
from django.db.models import Count, Q

class BannerCreateUpdateView(View):
    template_name = 'catloads_admin/add_banner.html'
    form_class = BannerForm
    success_url = 'catloadsadmin:promocode_list' 

    def get(self,request,id=None):
        try:    
            banner = get_object_or_404(Banner, id=id) if id else None
            form = self.form_class(instance=banner)
            action = 'Add Banner' if id is None else 'Update Banner'
            return render(request, self.template_name, {"form": form,'action':action})
        except Exception as e:
            print('Banner Create Page Loading Error', e)
            
    def post(self,request,id=None):
        try: 
            banner = get_object_or_404(Banner, id=id) if id else None
            form = self.form_class(request.POST,request.FILES, instance=banner)
            if form.is_valid():
                form.save()
                return redirect(self.success_url)
            else:
                action = 'Add Banner' if id is None else 'Update Banner'
                return render(request, self.template_name, {"form": form,'action':action})
        except Exception as e:
            print('Banner Posting Error', e)

class BannerListView(ListView):
    model = Banner
    template_name = 'catloads_admin/bannerlists.html'
    context_object_name = 'banners'
    paginate_by = 10
    queryset = Banner.objects.filter(is_deleted=False).order_by('-id')   

class BannerSoftDeleteView(View):
    success_url = reverse_lazy('catloadsadmin:banner_list')

    def get(self, request,id):
        # Set the product as deleted instead of deleting it
        try:
            instance = get_object_or_404(Banner, id=id)
            instance.is_deleted = True
            instance.save()
        except Exception as e:
            print('Banner Delete Error', e)
        return redirect(self.success_url)    