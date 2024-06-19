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
from django.http import HttpResponse
import xlwt


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


@method_decorator(login_required, name='dispatch')
class ExportOrderExcel(View):
    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="orders.xls"'

        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Orders')

        row_num = 0
        font_style = xlwt.XFStyle()
        font_style.font.bold = True

        # Updated columns list to include 'Order Date'
        columns = ['Order ID', 'Customer', 'Payment Method', 'Order Status', 'Tax', 'Discount', 'Total Price', 'Order Date', 'Product', 'Quantity', 'Price', 'Subtotal']

        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style)

        font_style = xlwt.XFStyle()
        orders = Order.objects.prefetch_related('items').all()

        for order in orders:
            items = order.items.all()
            order_details = [
                order.id,
                order.user.username if order.user else "",
                order.get_payment_method_display(),
                order.get_status_display(),
                str(order.tax),
                str(order.discount),
                str(order.total_price),
                order.created_on.strftime('%Y-%m-%d') if order.created_on else "",  # Assuming 'order_date' is the field name and it is not None
            ]
            
            if not items:
                row_num += 1
                for i, detail in enumerate(order_details):
                    ws.write(row_num, i, detail, font_style)
            for item in items:
                row_num += 1
                for i, detail in enumerate(order_details):
                    ws.write(row_num, i, detail, font_style)
                ws.write(row_num, 8, item.product.name, font_style)
                ws.write(row_num, 9, item.quantity, font_style)
                ws.write(row_num, 10, str(item.price), font_style)
                ws.write(row_num, 11, str(item.get_subtotal()), font_style)

        wb.save(response)
        return response  