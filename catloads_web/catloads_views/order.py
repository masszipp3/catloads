import contextlib
from django.shortcuts import render,get_object_or_404,redirect
from django.urls import reverse_lazy,reverse
from django.views import View
from catloads_web.models import Order,OrderItem,PromoCode,CustomUser,Payment
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
import razorpay
import json
from catloads.settings import RAZOR_PAY_KEY, RAZOR_PAY_SECRET,RAZO_PAY_WEBHOOK
from django.http import HttpResponse
import xlwt
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
import json
import hmac
import hashlib
from catloads_web.utils import send_confirm_email

class CartView(TemplateView):
    template_name = 'catloads_web/shop-cart.html'

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)
    
class OrderCreate(View):
    template_name = 'catloads_web/shop-checkout.html'
    success_url = 'catloadsadmin:product_list' 

    def get(self,request,encoded_id=None):
        try:
            razorpay_client = razorpay.Client(auth=(RAZOR_PAY_KEY, RAZOR_PAY_SECRET))
            if not request.user.is_authenticated:
                login_url = f"{reverse('catloads_web:login')}?redirect=order"
                return HttpResponseRedirect(login_url)
            if encoded_id is None:
                order_id = updateto_Order(request)
                return HttpResponseRedirect(reverse('catloads_web:order_create', kwargs={'encoded_id': order_id}))
            print(request.user.pk)
            order_id = decode_base64_to_id(encoded_id)
            order = Order.objects.get(user=request.user,is_deleted =False,id=order_id,order_status__in=[1,3])
            orderitems  = order.items.all()
            total_amount = order.get_order_total()*100

            if not order.razorpay_id:
                # Create Razorpay order
                razorpay_order = razorpay_client.order.create({
                    "amount": float(total_amount),
                    "currency": "INR",
                    "receipt": f"order_rcptid_{order.id}",
                    "payment_capture": '1'
                })
                # Save the Razorpay order ID to the order instance
                order.razorpay_id = razorpay_order['id']
                order.total_price = order.get_order_total()  # Save the initial amount
                order.save()
            context = {
                'orderitems':orderitems,
                'order':order,
                'razorpay_order_id': order.razorpay_id,
                'razorpay_key_id': RAZOR_PAY_KEY,  # Add your Razorpay Key ID
                'amount': float(order.total_price),
                'currency': "INR",
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
            orders = Order.objects.filter(user=request.user,is_deleted =False,promocode=promocode)
            if orders.exists() or float(promocode.minimum_order_value) > float(order_value):
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
            payment_id = request.POST.get('razorpay_payment_id')
            print(payment_id)
            payment_order_id = request.POST.get('razorpay_order_id')
            payment_signature_id = request.POST.get('razorpay_signature',None)
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
            if payment_id:
                Payment.objects.create(order=order,transaction_id=payment_id,signature=payment_signature_id,amount=order.total_price,status=2)
            send_confirm_email(user=order.user,request=request)    
            redirect_url = reverse('catloads_web:downloads') 
            return JsonResponse({'Message':'Success','redirect_url':redirect_url})
        except (Exception, Exception) as e:
            return  JsonResponse({'Message':'Failed','Reason':str(e)})
        

class VerifyPaymentView(View):
    def get(self,request):
        payment_id = request.GET.get('payment_id',None)
        orderid = request.GET.get('order_id',None)
        signature = request.GET.get('signature',None)
        if payment_id:
            with contextlib.suppress(Exception):
                return self._extracted_from_get_(orderid, payment_id)
        return redirect('catloads_web:orders')

    def _extracted_from_get_(self, orderid, payment_id):
        instance = get_object_or_404(Order, pk=orderid)
        client = razorpay.Client(auth=(RAZOR_PAY_KEY,RAZOR_PAY_SECRET))
        paymemnt = client.payment.fetch(payment_id)
        payment_instance = Payment.objects.create(order=instance
                                                ,amount=paymemnt.get('amount')/100 if paymemnt.get('amount') else 0,
                                                transaction_id=payment_id,reason = paymemnt.get('error_reason',None))
        payment_instance.status = 2 if paymemnt.get('status') == 'captured' else 3
        payment_instance.save()
        instance.order_status = 2 if paymemnt.get('status') == 'captured' else 3
        instance.save()
        return redirect('catloads_web:downloads') if paymemnt.get('status') == 'captured' else redirect('catloads_web:orders')


class Update_paymentView(View):
    @csrf_exempt
    def post(self,request):
        securyt_key = RAZO_PAY_WEBHOOK

        webhook_payload = request.body
        received_signature = request.headers.get('X-Razorpay-Signature')
        generated_signature = hmac.new(securyt_key.encode(), webhook_payload, hashlib.sha256).hexdigest()
        if hmac.compare_digest(received_signature, generated_signature):
            webhook_payload = json.loads(webhook_payload)

            # Handle the event - e.g., check if it's a payment captured event
            if webhook_payload['event'] == 'payment.captured':
                # Get the relevant information from the payload
                payment_id = webhook_payload['payload']['payment']['entity']['id']
                order_id = webhook_payload['payload']['payment']['entity']['order_id']
                amount = webhook_payload['payload']['payment']['entity']['amount']
                if order := Order.objects.filter(razorpay_id=order_id).first():
                    order.order_status= 2
                    order.save()
                    payment,_ = Payment.objects.get_or_create(order=order, transaction_id=payment_id)
                    payment.amount = amount
                    payment.save()
                    return HttpResponse(status=200)
        return HttpResponse(status=400)    













                
            


