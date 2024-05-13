from django.shortcuts import render,get_object_or_404,redirect
from django.urls import reverse_lazy
from django.views import View
from catloads_web.models import PromoCode
from catloads_admimn.froms import PromoCodeForm
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView
from django.db.models import Count, Q
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

@method_decorator(login_required, name='dispatch')
class PromoCodeCreateUpdateView(View):
    template_name = 'catloads_admin/add-promocode.html'
    form_class = PromoCodeForm
    success_url = 'catloadsadmin:promocode_list' 

    def get(self,request,id=None):
        try:    
            promocode = get_object_or_404(PromoCode, id=id) if id else None
            form = self.form_class(instance=promocode)
            action = 'Add Promo Code' if id is None else 'Update Promo Code'
            return render(request, self.template_name, {"form": form,'action':action})
        except Exception as e:
            print('Promo Code Create Page Loading Error', e)
            
    def post(self,request,id=None):
        try: 
            promocode = get_object_or_404(PromoCode, id=id) if id else None
            form = self.form_class(request.POST,request.FILES, instance=promocode)
            if form.is_valid():
                form.save()
                return redirect(self.success_url)
            else:
                action = 'Add Promo Code' if id is None else 'Update Promo Code'
                return render(request, self.template_name, {"form": form,'action':action})
        except Exception as e:
            print('Promo Code Posting Error', e)

@method_decorator(login_required, name='dispatch')
class PromoCodeListView(ListView):
    model = PromoCode
    template_name = 'catloads_admin/promocodelist.html'
    context_object_name = 'promocodes'
    paginate_by = 10
    queryset = PromoCode.objects.filter(is_deleted=False).order_by('-id')            
    
class PromoCodeSoftDeleteView(View):
    success_url = reverse_lazy('catloadsadmin:promocode_list')
    def get(self, request,id):
        # Set the product as deleted instead of deleting it
        try:
            instance = get_object_or_404(PromoCode, id=id)
            instance.is_deleted = True
            instance.save()
        except Exception as e:
            print('PromoCode Delete Error', e)
        return redirect(self.success_url)            