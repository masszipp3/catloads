from django.db.models.query import QuerySet
from django.shortcuts import render,get_object_or_404,redirect
from django.urls import reverse_lazy
from django.views import View
from catloads_web.models import Order,OrderItem
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
from django.http import HttpResponse
import xlwt
from django.http import JsonResponse   
from catloads_web.utils import send_confirm_email




@method_decorator(login_required, name='dispatch')
class OrderListView(UserPassesTestMixin,ListView):
    model = Order
    template_name = 'catloads_admin/orders.html'
    context_object_name = 'orders'
    paginate_by = 10
    queryset = Order.objects.filter(is_deleted=False).order_by('-id').annotate( items_count=Count('items'))

    def get(self, request, *args, **kwargs):
        if 'search' in self.request.GET:
            keyword=  self.request.GET.get('search','')
            queryset = self.get_queryset().filter(
                Q(order_id__icontains=keyword) | 
                Q(user__email__icontains=keyword) |
                Q(user__phone__icontains=keyword) 
            ) 
            order_list = [{
            'id': order.id,
            'order_id': order.order_id,
            'amount':  order.total_price,
            'count': order.items_count,
            'edit_link': reverse("catloadsadmin:order_detail" , kwargs={'pk': order.id}),
            'delete_link': reverse("catloadsadmin:order_delete" , kwargs={'id': order.id}),  
            'date': order.created_on,
            'status': order.get_order_status_display()
        } for order in queryset] 
            return JsonResponse({'orders': order_list}, safe=False)
        return super().get(request, *args, **kwargs)     
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
class OrderUpdateView(UserPassesTestMixin,View):  
    def test_func(self):
        return self.request.user.is_superuser   
    
    def handle_no_permission(self):
        return HttpResponseRedirect(reverse('catloadsadmin:login'))
    def get(self,request ,id):
        try:
            status = request.GET.get('status')
            order = Order.objects.get(id=id)
            if status:
                order.order_status = status
                order.save()
                if status == '2':
                    send_confirm_email(user=order.user,request=request)    

            return redirect(reverse('catloadsadmin:order_detail', kwargs={'pk': id}) )    
        except Order.DoesNotExist:
            return redirect('catloadsadmin:orderlist')

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


@method_decorator(login_required, name='dispatch')
class OrderViewList(UserPassesTestMixin,ListView):
    model = Order
    template_name = 'catloads_admin/order_data.html'
    context_object_name = 'orders'
    paginate_by = 60
    queryset = OrderItem.objects.filter(is_deleted=False).order_by('-id')

    def get_queryset(self) :
        queryset = super().get_queryset()
        start_date = self.request.GET.get('start',None)
        end_date = self.request.GET.get('end',None)
        if start_date and end_date:
            queryset = queryset.filter(order__created_on__date__range=(start_date,end_date))
        return queryset
        
    def test_func(self):
        return self.request.user.is_superuser   

    def handle_no_permission(self):
        return HttpResponseRedirect(reverse('catloadsadmin:login'))