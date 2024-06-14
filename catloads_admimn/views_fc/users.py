from django.shortcuts import render,get_object_or_404,redirect
from django.urls import reverse_lazy
from django.views import View
from catloads_web.models import CustomUser
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView
from django.db.models import Count, Q
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import xlwt
from django.http import HttpResponse

@method_decorator(login_required, name='dispatch')
class UsersListView(ListView):
    model = CustomUser
    template_name = 'catloads_admin/all-user.html'
    context_object_name = 'users'
    paginate_by = 10
    queryset = CustomUser.objects.filter(usertype=2,is_deleted=False).order_by('-id')  
@method_decorator(login_required, name='dispatch')
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

@method_decorator(login_required, name='dispatch')
class ExportUserExcel(View):
    def get(self, request, *args, **kwargs):
        # Create a workbook and add a worksheet.
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="users.xls"'

        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Users')

        # Sheet header, first row
        row_num = 0
        font_style = xlwt.XFStyle()
        font_style.font.bold = True

        columns = ['User ID', 'User Type', 'Name', 'Email', 'City', 'Phone']

        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style)

        # Sheet body, remaining rows
        font_style = xlwt.XFStyle()

        users = CustomUser.objects.all()
        for user in users:
            row_num += 1
            ws.write(row_num, 0, user.id, font_style)
            ws.write(row_num, 1, user.get_usertype_display(), font_style)
            ws.write(row_num, 2, user.name or "", font_style)
            ws.write(row_num, 3, user.email or "", font_style)
            ws.write(row_num, 4, user.city or "", font_style)
            ws.write(row_num, 5, user.phone or "", font_style)

        wb.save(response)
        return response