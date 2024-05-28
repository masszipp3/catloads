from django.shortcuts import render,get_object_or_404,redirect
from django.urls import reverse_lazy
from django.views import View
from catloads_web.models import Order
from catloads_admimn.forms import PromoCodeForm
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView
from django.db.models import Count, Q
from django.views.generic import DetailView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponseRedirect
from django.urls import reverse


@method_decorator(login_required, name='dispatch')
class OrderListView(UserPassesTestMixin,ListView):
    model = Order
    template_name = 'catloads_admin/orders.html'
    context_object_name = 'orders'
    paginate_by = 10
    queryset = Order.objects.filter(is_deleted=False).order_by('-id').annotate( items_count=Count('items'))
    def test_func(self):
        return self.request.user.is_superuser   
    
    def handle_no_permission(self):
        return HttpResponseRedirect(reverse('catloadsadmin:login'))

@method_decorator(login_required, name='dispatch')
class OrderDetailView(UserPassesTestMixin,DetailView):
    model = Order
    template_name = 'catloads_admin/oder-detail.html'
    context_object_name = 'order'    
    def test_func(self):
        return self.request.user.is_superuser   
    
    def handle_no_permission(self):
        return HttpResponseRedirect(reverse('catloadsadmin:login'))
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = context['order']
        total = sum(item.quantity * item.price for item in order.items.all())
        context['total'] = total
        return context

@method_decorator(login_required, name='dispatch')
class OrderSoftDeleteView(UserPassesTestMixin,View):
    success_url = reverse_lazy('catloadsadmin:orderlist')
    def test_func(self):
        return self.request.user.is_superuser   
    
    def handle_no_permission(self):
        return HttpResponseRedirect(reverse('catloadsadmin:login'))
    def get(self, request,id):
        
        try:
            instance = get_object_or_404(Order, id=id)
            instance.is_deleted = True
            instance.save()
        except Exception as e:
            print('Order Delete Error', e)
        return redirect(self.success_url)
