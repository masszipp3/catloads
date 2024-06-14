from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from .models import CustomUser
from django.shortcuts import render,get_object_or_404,redirect
from django.urls import reverse

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        user.username = user.email
        user.name = user.first_name
        return user

    def pre_social_login(self, request, sociallogin):
        user = CustomUser.objects.filter(email=sociallogin.user.email).first()
        if user and not sociallogin.is_existing:
            sociallogin.connect(request, user) 

    def get_login_redirect_url(self, request):
         return reverse('catloads_web:login_redirect')