from django.shortcuts import render
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


@method_decorator(login_required, name='dispatch')
class DashboardView(View):
    template_name = 'catloads_admin/index.html'
    def get(self,request):
        try:
            return render(request,self.template_name)
        except Exception as e:
            print("Error in dashboard view : ",e)