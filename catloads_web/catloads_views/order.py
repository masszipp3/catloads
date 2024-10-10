import contextlib
from django.shortcuts import render,get_object_or_404,redirect
from django.urls import reverse_lazy,reverse
from django.views import View
from catloads_web.models import Order,OrderItem,PromoCode,CustomUser,Payment,AuthToken
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
import logging
from catloads_web.utils import send_confirm_email,login_user_without_password,generate_unique_token,send_failedwhatsapp_notification,send_successwhatsapp_notification,send_meta_apiconversion

class CartView(TemplateView):
    template_name = 'catloads_web/shop-cart.html'

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)
    
class OrderCreate(View):
    template_name = 'catloads_web/shop-checkout.html'
    success_url = 'catloadsadmin:product_list' 

    def get(self,request,encoded_id=None):
        try:
            token = request.GET.get('acctoken')
            if token:
                user = AuthToken.objects.get(token=token).user
                login_user_without_password(request=request,user=user)
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
            order.client_ip_address = request.META.get('HTTP_X_FORWARDED_FOR', None)  or request.META.get('REMOTE_ADDR')
            order.client_user_agent = request.META.get('HTTP_USER_AGENT', None)  
            if 'fbc' in request.session:
                order.fcb_id = request.session['fbc']
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
            send_meta_apiconversion(order)   
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
        send_meta_apiconversion(instance)   
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

# Configure logging
logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class UpdatePaymentView(View):
    def post(self, request):
        try:
            # Log request details for debugging
            logger.info("Received Razorpay webhook:")
            logger.info(f"Headers: {request.headers}")
            logger.info(f"Body: {request.body}")

            # Razorpay secret key for generating signature
            security_key = RAZO_PAY_WEBHOOK

            # Verify the webhook signature
            webhook_payload = request.body
            received_signature = request.headers.get('X-Razorpay-Signature')
            generated_signature = hmac.new(security_key.encode(), webhook_payload, hashlib.sha256).hexdigest()

            if not hmac.compare_digest(received_signature, generated_signature):
                logger.error("Signature mismatch: Verification failed.")
                return HttpResponse("Signature mismatch: Verification failed.", status=400)

            # Parse the webhook payload
            webhook_payload = json.loads(webhook_payload)
            logger.info(f"Parsed Webhook Payload: {webhook_payload}")
            print(webhook_payload,'hhhhkkk')
            # Extract necessary details
            event = webhook_payload.get('event')
            payment_entity = webhook_payload.get('payload', {}).get('payment', {}).get('entity', {})
            payment_id = payment_entity.get('id')
            order_id = payment_entity.get('order_id')
            amount = payment_entity.get('amount')
            phone = payment_entity.get('contact')

            status = payment_entity.get('status')

            # Validate extracted data
            if not payment_id or not order_id or amount is None:
                logger.error("Invalid payment information extracted from webhook.")
                return HttpResponse("Invalid payment information", status=400)

            # Process order and payment based on the event type
            order = Order.objects.filter(razorpay_id=order_id).first()
            if not order:
                logger.error(f"Order not found for order_id: {order_id}")
                return HttpResponse(f"Order not found: {order_id}", status=404)
            send_meta_apiconversion(order)
            if event == 'payment.captured':
                # Update order and payment for captured payment
                order.order_status = 2  # Assume 2 is the status for "Captured"
                order.save()
                payment, _ = Payment.objects.get_or_create(order=order, transaction_id=payment_id)
                payment.amount = amount
                payment.status = 2
                order.user.phone = phone
                order.user.save()
                payment.save()
                send_successwhatsapp_notification(order=order)
                logger.info(f"Payment captured for order_id: {order_id}, payment_id: {payment_id}")

                return HttpResponse("Payment captured and processed successfully.", status=200)
            
            elif event == 'payment.failed':
                # Update order and payment for failed payment
                order.order_status = 3  # Assume 3 is the status for "Failed"
                order.save()
                payment, _ = Payment.objects.get_or_create(order=order, transaction_id=payment_id)
                payment.amount = amount
                payment.status = 0
                order.user.phone = phone
                order.user.save()
                payment.save()
                send_failedwhatsapp_notification(order=order)
                logger.info(f"Payment failed for order_id: {order_id}, payment_id: {payment_id}")
                return HttpResponse("Payment failed and processed successfully.", status=200)

            elif event == 'payment.pending':
                # Update order and payment for pending payment
                order.order_status = 1  #1 is the status for "Pending"
                order.save()
                payment, _ = Payment.objects.get_or_create(order=order, transaction_id=payment_id)
                payment.amount = amount
                payment.status = 1
                order.user.phone = phone
                order.user.save()
                payment.save()
                logger.info(f"Payment pending for order_id: {order_id}, payment_id: {payment_id}")
                return HttpResponse("Payment pending and processed successfully.", status=200)
            
            else:
                logger.error(f"Unhandled event type: {event}")
                return HttpResponse(f"Unhandled event type: {event}", status=400)
                
        except Exception as e:
            logger.exception(f"Exception occurred while processing the webhook: {e}")
            return HttpResponse(f"Exception occurred: {e}", status=400)










                
            


