from django.shortcuts import render,get_object_or_404,redirect
from django.urls import reverse_lazy
from django.views import View
from catloads_web.models import Category,Product,ProductSale,Banner,CustomUser,Country,CountryPrice,Order
from catloads_admimn.forms import CategoryForm,ProductForm
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView
from django.db.models import Count, Q
from django.http import JsonResponse   
from django.contrib.auth import authenticate, login,logout
from django.urls import reverse
from django.db.models import Subquery,OuterRef,ExpressionWrapper,FloatField,F
from catloads_web.utils import send_failed_email

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator 

from django.core.mail import EmailMessage

def send_my_email():
    email = EmailMessage(
        'Hello',  # subject
        'Body goes here',  # message
        'support@catloads.com',  # from email
        ['rishanrash143@gmail.com'],  # to email list
        reply_to=['another@example.com'],  # reply address
        headers={'Message-ID': 'foo'},
    )
    email.send()

class DashboardView(View):
    template_name = 'catloads_web/index.html'
    def get(self,request):
        # send_my_email()
        order = Order.objects.get(id=21)
        send_failed_email(order=order)
        try:
            default_country = Country.get_default_country()
            country_id = self.request.session.get('country_data', {}).get('country_id') or default_country.id

            products_sale = ProductSale.objects.filter(
                country_sale_prices__country_id=country_id, 
                is_deleted=False
            )

            if not products_sale.exists():
                products_sale = ProductSale.objects.filter(
                    country_sale_prices__country_id=default_country.id, 
                    is_deleted=False
                )
                country_id = default_country.id

            products_sale = products_sale.annotate(
                price_for_country=Subquery(
                    CountryPrice.objects.filter(
                        product_sale=OuterRef('pk'),
                        country_id=country_id
                    ).values('price')[:1]
                ),
                symbol=Subquery(
                    CountryPrice.objects.filter(
                        product_sale=OuterRef('pk'),
                        country_id=country_id
                    ).values('country__symbol')[:1]
                ),
                discount_for_country=Subquery(
                    CountryPrice.objects.filter(
                        product_sale=OuterRef('pk'),
                        country_id=country_id
                    ).values('discount')[:1]
                ),
                discount_percentage=ExpressionWrapper(
                    100 * F('discount_for_country') / (F('discount_for_country') + F('price_for_country')),
                    output_field=FloatField()
                ),
                order_count=Count('order_items')
            ).order_by('-order_count')
            banners = Banner.objects.filter(is_deleted= False)
            context = {'products_sale':products_sale,'banners':banners}
            return render(request,self.template_name,context=context)
        except Exception as e:
            print("Error in dashboard view : ",e)   

class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect(reverse('catloads_web:login'))            