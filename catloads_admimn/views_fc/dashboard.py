from django.shortcuts import render
from django.views import View

class DashboardView(View):
    template_name = 'catloads_admin/index.html'
    def get(self,request):
        try:
            return render(request,self.template_name)
        except Exception as e:
            print("Error in dashboard view : ",e)