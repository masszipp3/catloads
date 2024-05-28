from django.shortcuts import render,get_object_or_404,redirect
from django.urls import reverse_lazy,reverse
from django.views import View
from catloads_web.models import Order,OrderItem,PromoCode,CustomUser
from catloads_admimn.forms import CategoryForm,ProductForm
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView
from django.db.models import Count, Q
from django.http import JsonResponse   
from django.views.generic import DetailView,TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator 
from django.http import HttpResponseRedirect
import base64
from .customer import decode_base64_to_id,handle_cart_data,updateto_Order

class CartView(TemplateView):
    template_name = 'catloads_web/shop-cart.html'

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)
    
class OrderCreate(View):
    template_name = 'catloads_web/shop-checkout.html'
    success_url = 'catloadsadmin:product_list' 

    def get(self,request,encoded_id=None):
        try:
            if not request.user.is_authenticated:
                login_url = f"{reverse('catloads_web:login')}?redirect=order"
                return HttpResponseRedirect(login_url)
            if encoded_id is None:
                order_id = updateto_Order(request.user)
                return HttpResponseRedirect(reverse('catloads_web:order_create', kwargs={'encoded_id': order_id}))
            print(request.user.pk)
            order_id = decode_base64_to_id(encoded_id)
            order = Order.objects.get(user=request.user,is_deleted =False,id=order_id,order_status=1)
            orderitems  = order.items.all()
            context = {
                'orderitems':orderitems,
                'order':order
            }
            return render(request, self.template_name,context)
        except Exception as e:
            print('Order Create Page Loading Error', e)
            return redirect('catloads_web:dashboard')


class PromocodeCheck(View):
    def get(self,request):
        try:
            order_value = request.GET.get('order_total')
            promocode = PromoCode.objects.get(code=request.GET.get('promocode'))
            if not promocode.is_valid():
                return JsonResponse({'Message':'Promocode Not Valid'})
            order = Order.objects.filter(user=request.user,is_deleted =False,promocode=promocode)
            if order.count() >= promocode.usage_limit and float(promocode.minimum_order_value) > float(order_value):
                return JsonResponse({'Message':'Failed'})
            return JsonResponse({'Message':'Success','promocode_id':promocode.id,'discount':promocode.discount_value,'total':float(order_value)-float(promocode.discount_value)})
        except Exception as e:
            return JsonResponse({'Message':'Failed','Reason':str(e)})
        

class OrderConfirmView(View):
    def post(self,request):
        try:
            city = request.POST.get('city')
            promocode = request.POST.get('promocode')
            total_price = request.POST.get('total_price')
            discount = request.POST.get('discount')
            order_id = request.POST.get('order_id')
            phone = request.POST.get('phone')
            order = Order.objects.get(id=order_id)
            if promocode is not None:
                order.promocode_id = promocode
            order.total_price = total_price
            order.discount = discount
            if city:
                order.user.city = city
            if phone and order.user.phone is None:
                order.user.phone = phone
            order.order_status = 2    
            order.save()
            order.user.save()
            redirect_url = reverse('catloads_web:orders') 
            return JsonResponse({'Message':'Success','redirect_url':redirect_url})
        except (Exception, Exception) as e:
            return  JsonResponse({'Message':'Failed','Reason':str(e)})