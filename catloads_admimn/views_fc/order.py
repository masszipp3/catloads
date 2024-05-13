from django.shortcuts import render,get_object_or_404,redirect
from django.urls import reverse_lazy
from django.views import View
from catloads_web.models import Order
from catloads_admimn.froms import PromoCodeForm
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView
from django.db.models import Count, Q
from django.views.generic import DetailView

class OrderListView(ListView):
    model = Order
    template_name = 'catloads_admin/orders.html'
    context_object_name = 'orders'
    paginate_by = 10
    queryset = Order.objects.filter(is_deleted=False).order_by('-id').annotate( items_count=Count('items'))

class OrderDetailView(DetailView):
    model = Order
    template_name = 'catloads_admin/order-detail.html'
    context_object_name = 'order'    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = context['order']
        total = sum(item.quantity * item.price for item in order.items.all())
        context['total'] = total
        return context


class OrderSoftDeleteView(View):
    success_url = reverse_lazy('catloadsadmin:orderlist')

    def get(self, request,id):
        
        try:
            instance = get_object_or_404(Order, id=id)
            instance.is_deleted = True
            instance.save()
        except Exception as e:
            print('Order Delete Error', e)
        return redirect(self.success_url)
