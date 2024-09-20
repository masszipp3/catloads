from django.shortcuts import render,get_object_or_404,redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.urls import reverse_lazy
from django.views import View
from catloads_web.models import Cart,CartItem,CustomUser,Order,OrderItem,ProductSale,ProductSaleItems,Product,Country
from catloads_web.forms import RegisterForm,EditUserForm
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView
from django.db.models import Count, Q
from django.http import HttpResponse, JsonResponse   
from django.core.mail import EmailMultiAlternatives
import json
from django.views.generic import DetailView,TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator 
from urllib.parse import unquote
from django.db import transaction
from django.db.models import F
import base64
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.models import SocialApp
from django.contrib import messages
from catloads_web.decorator import custom_login_required
from django.http import HttpResponseRedirect
from django.views.decorators.clickjacking import xframe_options_exempt
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from catloads_web.utils import *
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from catloads import settings

def encode_id_to_base64(id):
    # Convert integer ID to bytes
    id_bytes = str(id).encode('utf-8')
    # Encode these bytes to Base64
    base64_bytes = base64.b64encode(id_bytes)
    # Convert Base64 bytes to a string for easy use in URLs
    return base64_bytes.decode('utf-8')

def decode_base64_to_id(encoded_id):
    # Convert Base64 string back to bytes
    base64_bytes = encoded_id.encode('utf-8')
    # Decode Base64 bytes to original bytes
    id_bytes = base64.b64decode(base64_bytes)
    # Convert bytes back to string and then to integer
    return int(id_bytes.decode('utf-8'))

def handle_cart_data(user, cart_data_json,request):
    country_id = request.session.get('country_data', {}).get('country_id') or Country.get_default_country().id or None
    cart_data = json.loads(cart_data_json)
    print(cart_data)
    cart, _ = Cart.objects.get_or_create(user=user,country_id=country_id)
    cart.cart_total=cart_data['cart_total']
    cart.save()
    for item in cart_data.get('items', []):
        CartItem.objects.update_or_create(
            cart=cart,
            product_id=item['product'],
            defaults={
                'quantity': item['quantity'],
                'price': item['price'],
            }
        )
        request.session['cartstatus'] = True

def updateto_Order(request=None,user=None):
    try:
        with transaction.atomic():
            users = user if user else request.user
            country_id =None
            if request:
                country_id = request.session.get('country_data', {}).get('country_id') or Country.get_default_country().id or None
            cart,_ = Cart.objects.get_or_create(user=users,country_id=country_id)
            order = Order.objects.create(user=users,country_id=country_id)  # Properly unpack the tuple

            cartitems = cart.items.all()
            if cartitems.exists():  # Check if there are items in the cart
                for item in cartitems:
                    # Update or create order items
                    OrderItem.objects.update_or_create(
                        order=order,
                        product=item.product,
                        defaults={
                            'quantity': item.quantity , # Update quantity if exists
                            'price': item.price
                        }
                    )
                cart.delete()  
                return encode_id_to_base64(order.id)
    except Exception as e:
        print(e)

@method_decorator(custom_login_required(login_url='catloads_web:login'), name='dispatch')
class CustomerDahsboard(TemplateView):
    template_name = 'catloads_web/account-dashboard.html'

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)
    


@method_decorator(custom_login_required(login_url='catloads_web:login'), name='dispatch')
@method_decorator(xframe_options_exempt, name='dispatch')
class DropboxDownloadView(View):
    def get(self, request, *args, **kwargs):
        product_id = request.GET.get('pid')
        product = Product.objects.get(id=product_id)
        file_url = product.download_link
        response = HttpResponseRedirect(file_url)
        response['Content-Disposition'] = 'attachment; filename="desired_filename.ext"'
        return response  
    
# @method_decorator(custom_login_required(login_url='catloads_web:login'), name='dispatch')
class CustomerPrivacyPolicy(TemplateView):
    template_name = 'catloads_web/privacy_policy.html'

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)

# @method_decorator(custom_login_required(login_url='catloads_web:login'), name='dispatch')
class CustomerContact(TemplateView):
    template_name = 'catloads_web/contact.html'

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)


class CustomerTerms(TemplateView):
    template_name = 'catloads_web/terms_and_codition.html'

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)

class CustomerAbout(TemplateView):
    template_name = 'catloads_web/aboutus.html'

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)        
# @method_decorator(custom_login_required(login_url='/login/'), name='dispatch')
# class CustomerDowloads(TemplateView):
#     template_name = 'catloads_web/account-downloads.html'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         order_items = OrderItem.objects.filter(order__user=self.request.user)
#         product_sales = ProductSale.objects.filter(id__in=order_items.values_list('product_id', flat=True))
#         products = ProductSaleItems.objects.filter(sale_master__in=product_sales).distinct()
#         context['products'] = products
#         return context
@method_decorator(custom_login_required(login_url='/login/'), name='dispatch')   
class CustomerOrders(TemplateView):
    template_name = 'catloads_web/account-orders.html'

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)  
        country_id = self.request.session.get('country_data', {}).get('country_id') or Country.get_default_country().id or None
        order = Order.objects.filter(user=self.request.user,country_id=country_id) 
        context['orders'] = order
        return context

def direct_google_login(request):
    if cart := request.GET.get('cart'):
        cart_data = unquote(cart)
        user = request.user
        handle_cart_data(user, cart_data,request)
        order_id = updateto_Order(user=user)
        return redirect(reverse('catloads_web:order_create', kwargs={'encoded_id': order_id}))
    return render(request,'catloads_web/redirect.html')

class CustomerRegistrationUpdateView(View):
    template_name = 'catloads_web/shop-registration.html'
    form_class = RegisterForm
    success_url = 'catloads_web:login' 

    def get(self,request,id=None):
        try:    
            customer = get_object_or_404(CustomUser, id=id) if id else None
            form = self.form_class(instance=customer)
            action = 'Sign Up' if id is None else 'Update Profile'
            return render(request, self.template_name, {"form": form,'action':action})
        except Exception as e:
            print('Customer Create Page Loading Error', e)

    def post(self,request,id=None):
        # try:
            customer = get_object_or_404(CustomUser, id=id) if id else None
            form = self.form_class(request.POST,request.FILES, instance=customer)
            if form.is_valid():
                user = form.save()
                if cartdata := request.POST.get('cartData'):
                    user.backend = 'django.contrib.auth.backends.ModelBackend'
                    handle_cart_data(user, cartdata,request)  
                    if request.GET.get('redirect'):
                        order_id = updateto_Order(user=user)
                        login(request,user)
                        return redirect(reverse('catloads_web:order_create', kwargs={'encoded_id': order_id}))
                return redirect(self.success_url)
            else:
                print(form.errors)
                action = '' if id is None else 'Update Profile'
                return render(request, self.template_name, {"form": form,'action':action})
        # except Exception as e:
        #     print('Register Failed', e)        

class LoginView(View):
    template_name = 'catloads_web/shop-my-account.html'
    success_url = reverse_lazy('catloads_web:dashboard')

    def get(self,request):
        try:
            if request.user.is_authenticated:
                return redirect(self.success_url)
            return render(request,self.template_name)
        except Exception as e:
            print("Error in Login view : ",e)

    def post(self,request):
        try:
            username = request.POST.get('email')
            password = request.POST.get('password')
            user = authenticate(request,username=username, password=password)
            if  user is not None and user.usertype==2:
                user.backend = 'django.contrib.auth.backends.ModelBackend'

                if cartdata := request.POST.get('cartData'):
                    handle_cart_data(user, cartdata,request)  
                    if request.GET.get('redirect'):
                        order_id = updateto_Order(user=user,request=request)
                        self.success_url = reverse('catloads_web:order_create', kwargs={'encoded_id': order_id})
                login(request,user)
                if request.GET.get('next'):
                    return redirect(request.GET.get('next'))
                return redirect(self.success_url)
            else:
                message = 'Un Authorized Access'
        except Exception as e:
            message = f'Error Occured,{e}'
        return render(request,self.template_name,{"msg":message})

class CartView(View):
    def post(self, request):
        # Example payload: {'action': 'add', 'product_id': '1', 'quantity': 1}
        action = request.POST.get('action')
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))

        cart = Cart.objects.get_or_create(user=request.user)
        if action == 'add':
            if not cart.items.filter(product_id=product_id).exists():
               CartItem.objects.create(cart=cart,product_id=product_id)
            else:
                cartitem = CartItem.objects.get(cart=cart,product_id=product_id)
                cartitem.quantity += 1
                cartitem.save()
            messages.success(request, "Product added to cart!")
        elif action == 'remove':
            if not cart.items.filter(product_id=product_id).exists():
               messages.error(request, "Product not in cart!")
            else:
                cartitem = CartItem.objects.get(cart=cart,product_id=product_id)
                cartitem.quantity -= 1
                if cartitem.quantity <= 0:
                    cartitem.delete()
                else:    
                    cartitem.save()
            messages.success(request, "Product minus from cart!")
        elif action == 'delete':
            if not cart.items.filter(product_id=product_id).exists():
               messages.error(request, "Product not in cart!")
            else:
                cartitem = CartItem.objects.get(cart=cart,product_id=product_id)
                cartitem.delete()
        return JsonResponse({'cart': cart})

    def get(self, request):
        # Return the contents of the shopping cart
        cart = request.session.get('cart', {})
        return JsonResponse({'cart': cart})
    
class ProductListView(ListView):
    model = Product
    template_name = 'catloads_web/product-list.html'
    context_object_name = 'products'
    paginate_by = 10

    def get(self, request, *args, **kwargs):
        if 'search' in self.request.GET:
            keyword=  self.request.GET.get('search','')
            queryset = self.get_queryset().filter(
                Q(name__icontains=keyword) | 
                Q(sale_id__icontains=keyword)
            ) 
            products_list = list(queryset.values( 'name', 'slug'))  
            return JsonResponse({'products': products_list}, safe=False)
        return super().get(request, *args, **kwargs) 
    def get_queryset(self):
        queryset = ProductSale.objects.filter(is_deleted=False)
        return queryset    

class CartDataView(View):
    def post(self, request):
        # Return the contents of the shopping cart
        user= request.user
        if not user.is_authenticated:
            redirect_url = reverse('catloads_web:login')
            redirect_url=f"{redirect_url}?redirect=order"
            return JsonResponse({'Message':'user not logged in' ,'redirect_url':redirect_url})
        cart = request.POST['cart']
        # print(cart)
        handle_cart_data(user,cart,request)
        order = updateto_Order(request=request)
        redirect_url = reverse('catloads_web:order_create', kwargs={'encoded_id': order})
        return JsonResponse({'Message':'Success','order': order,'redirect_url':redirect_url})


class CustomerDowloads(TemplateView):
    template_name = 'catloads_web/account-downloads.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_id = self.request.GET.get('order_id')
        order_items = OrderItem.objects.filter(order__user=self.request.user,order__order_status=2)
        if order_id:
           order_items= order_items.filter(id=order_id)
        product_sales = ProductSale.objects.filter(id__in=order_items.values_list('product_id', flat=True))
        products = ProductSaleItems.objects.filter(sale_master__in=product_sales).distinct()
        context['products'] = products
        return context
    
@method_decorator(custom_login_required(login_url='/login/'), name='dispatch')
class AccountUpdateView(UpdateView):
    model = CustomUser
    form_class = EditUserForm
    template_name = 'catloads_web/account-edit-account.html'  # Specify your template name
    success_url = reverse_lazy('catloads_web:dashboard')  # Redirect to account view or other appropriate page

    def get_object(self):
        return self.request.user    

    def form_valid(self, form):
        print(form)
        response = super().form_valid(form)
        # After form is saved
        return response

    def form_invalid(self, form):
        print(form.errors)  # This will help identify what went wrong
        return super().form_invalid(form)
    

class ForgetpasswordView(View):
    template_name = 'catloads_web/forget_password.html'
    success_url = reverse_lazy('catloads_web:login')

    def get(self,request):
        try:
            return render(request,self.template_name)
        except Exception as e:
            print("Error in Login view : ",e)
            return redirect(self.success_url)

    def post(self,request):
        try:
            email = request.POST.get('email')
            user = CustomUser.objects.filter(email=email).first()
            if user is None:
                message = 'User not exists'
                return render(request,self.template_name,{"msg":message})    
            else:
                self.send_resetmail(user, request)
                message =''
        except Exception as e:
            message = f'Error Occured,{e}'
            return render(request,self.template_name,{"msg":message})    
        return render(request,self.template_name,{"success":True})

    def send_resetmail(self, user, request):
        token_generator = PasswordResetTokenGenerator()
        token = token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_link = request.build_absolute_uri(
                    reverse('catloads_web:change_password', kwargs={'uidb64': uid, 'token': token}))
        context = {
            'name': user.name,
            'email': user.email,
            'reset_link': reset_link,     
        }
        html_content = render_to_string('catloads_web/email.html', context)
        text_content = strip_tags(html_content) 
        email = EmailMultiAlternatives(
        subject='Password Reset',
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email]
         )
        email.attach_alternative(html_content, "text/html")
        email.send()    

class ChangepasswordView(View):
    template_name = 'catloads_web/change_password.html'
    success_url = reverse_lazy('catloads_web:login')

    def get(self,request,**kwargs):
        try:
            token = kwargs.get('token')
            uidb64 = kwargs.get('uidb64')
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            user = None
        if user is not None and PasswordResetTokenGenerator().check_token(user, token):
            return render(request,self.template_name,{'success':True})
        else:
            return HttpResponse("Token Expired")
    def post(self,request,**kwargs):
        try:
            uidb64 = kwargs.get('uidb64')
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                return redirect(self.success_url)
            else:
                render(request,self.template_name,{'msg':'Password Doesnot Match'})
        except Exception:
            return render(request,self.template_name,{'msg':'Failed to Change the Password'})


class SendEmialTempView(View):
    template_name = 'catloads_web/email.html'
    success_url = reverse_lazy('catloads_web:login')

    def get(self,request):
        try:
            return render(request,self.template_name)
        except Exception as e:
            print("Error in Login view : ",e)               