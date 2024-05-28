from django.shortcuts import render
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponseRedirect
from django.urls import reverse

@method_decorator(login_required, name='dispatch')
class DashboardView(UserPassesTestMixin,View):
    template_name = 'catloads_admin/index.html'
    def test_func(self):
        return self.request.user.is_superuser   
    
    def handle_no_permission(self):
        return HttpResponseRedirect(reverse('catloadsadmin:login'))    
    def get(self,request):
        try:
            return render(request,self.template_name)
        except Exception as e:
            print("Error in dashboard view : ",e)