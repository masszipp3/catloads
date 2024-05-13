from django.shortcuts import render,get_object_or_404,redirect
from django.urls import reverse_lazy
from django.views import View
from catloads_web.models import CustomUser
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView
from django.db.models import Count, Q


class UsersListView(ListView):
    model = CustomUser
    template_name = 'catloads_admin/all-user.html'
    context_object_name = 'users'
    paginate_by = 10
    queryset = CustomUser.objects.filter(usertype=2,is_deleted=False).order_by('-id')  

class UserSoftDeleteView(View):
    success_url = reverse_lazy('catloadsadmin:userlist')

    def get(self, request,id):
        try:
            instance = get_object_or_404(CustomUser, id=id)
            instance.is_deleted = True
            instance.save()
        except Exception as e:
            print('User Delete Error', e)
        return redirect(self.success_url)    
