from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.utils.crypto import constant_time_compare
from datetime import datetime
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
from django.core.mail import EmailMultiAlternatives
from twilio.rest import Client
from . models import Order,AuthToken
import base64
import json
from django.contrib.auth import login
import secrets
from django.utils import timezone

def login_user_without_password(request, user):
    if user :
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)

def generate_unique_token(user):
    token = secrets.token_hex(20) 
    
    # Ensure the token is unique
    while AuthToken.objects.filter(token=token).exists():
        token = secrets.token_hex(20)  # Regenerate token if not unique
    auth_token, created = AuthToken.objects.update_or_create(user=user, defaults={'token': token,'created_on': timezone.now() })
    return auth_token.token

def encode_id_to_base64(id):
    id_bytes = str(id).encode('utf-8')
    base64_bytes = base64.b64encode(id_bytes)
    return base64_bytes.decode('utf-8')


def send_failedwhatsapp_notification(order,template='HX5d900d34c3f6d587c6b81e959587d9c1'):
        account_sid = settings.TWILIO_ACCOUNT_SID
        auth_token = settings.TWILIO_AUTH_TOKEN
        client = Client(account_sid, auth_token)
        order_id = encode_id_to_base64(order.id)
        token = generate_unique_token(order.user)
        url = f'customer/order/{order_id}?acctoken={token}'
        phone_number = order.user.phone.strip().replace(" ", "")
        if not phone_number.startswith("+91"):
            phone_number = "+91" + phone_number
        if phone_number:    
            message = client.messages.create(
                    content_sid=template,
                    content_variables=json.dumps({
                        "1": str(order.order_id), 
                        "2": url ,
                        "3":order.user.name
                    }),
                    from_=f'whatsapp:{settings.TWILIO_PHONE_NUMBER}',
                    to=f'whatsapp:{phone_number}')

def send_successwhatsapp_notification(order,template='HXbf9e4e5db502ba92a047c86123202218'):
        account_sid = settings.TWILIO_ACCOUNT_SID
        auth_token = settings.TWILIO_AUTH_TOKEN
        client = Client(account_sid, auth_token)
        token = generate_unique_token(order.user)
        url = f'customer/downloads?acctoken={token}&order_id={order.id}'
        phone_number = order.user.phone.strip().replace(" ", "")
        if not phone_number.startswith("+91"):
            phone_number = "+91" + phone_number
        if phone_number:    
            message = client.messages.create(
                    content_sid=template,
                    content_variables=json.dumps({
                        "1": "Worksheets", 
                        "2": url ,
                        "3":order.user.name
                    }),
                    from_=f'whatsapp:{settings.TWILIO_PHONE_NUMBER}',
                    to=f'whatsapp:{phone_number}')


def send_confirm_email( user,request):
        orders_link = request.build_absolute_uri(
                    reverse('catloads_web:orders'))
        context = {
            'name': user.name,
            'email': user.email,
            'orders_link': orders_link,     
        }
        html_content = render_to_string('catloads_web/order_confirmation_email.html', context)
        text_content = strip_tags(html_content) 
        email = EmailMultiAlternatives(
        subject='Catloads Order Confirmation',
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email]
         )
        email.attach_alternative(html_content, "text/html")
        email.send()  

# class CustomPasswordResetTokenGenerator(PasswordResetTokenGenerator):
#     def _today(self):
#         # Return today's date as a datetime object
#         return datetime.now()

#     def _make_hash_value(self, user, timestamp):
#         # Ensure the timestamp is in a consistent format (e.g., timestamp is the datetime the token was generated)
#         login_timestamp = '' if user.last_login is None else user.last_login.replace(microsecond=0, tzinfo=None)
#         return f"{user.pk}{user.password}{timestamp.strftime('%Y-%m-%d %H:%M:%S')}{login_timestamp}"

#     def make_token(self, user):
#         timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#         ts_encoded = urlsafe_base64_encode(force_bytes(timestamp))
#         return f"{ts_encoded}-{self._make_hash_value(user, timestamp)}"

#     def _secret_value(self, user):
#         """
#         Generate a secret value that changes upon password or other critical user details change.
#         """
#         # This is a placeholder. You might want to include actual user details that impact token security.
#         return user.password + str(user.pk)
    
#     def check_token(self, user, token):
#         """
#         Check that a password reset token is correct for a given user.
#         """
#         # Split the token
#         try:
#             ts_b64, hash = token.split("-")
#             ts = force_str(urlsafe_base64_decode(ts_b64))
#             ts = datetime.strptime(ts, '%Y-%m-%d %H:%M:%S')
#         except (ValueError, IndexError, OverflowError):
#             return False

#         # Check the timestamp is within limit (e.g., within 48 hours)
#         if (self._today() - ts).total_seconds() > 48 * 3600:
#             return False

#         hash_value = self._make_hash_value(user, ts)
#         return constant_time_compare(hash_value, hash)


