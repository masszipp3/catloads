from django.contrib.auth import authenticate, login
from catloads_web.models import CustomUser
from django.views import View
from django.urls import reverse_lazy

from django.shortcuts import render,redirect



class LoginView(View):
    template_name = 'catloads_admin/login.html'
    success_url = reverse_lazy('catloadsadmin:dashboard')

    def get(self,request):
        try:
            return render(request,self.template_name)
        except Exception as e:
            print("Error in Login view : ",e)

    def post(self,request):
        try:
            username = request.POST.get('email')
            password = request.POST.get('password')
            user = authenticate(request,username=username, password=password)
            if  user is not None and user.usertype==1:
                login(request,user)
                return redirect(self.success_url)
            else:
                message = 'Un Authorized Access'
        except Exception as e:
            message = f'Error Occured,{e}'
        return render(request,self.template_name,{"message":message})
            
