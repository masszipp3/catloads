from decimal import Decimal
from django.shortcuts import render
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponseRedirect,HttpResponse
from django.urls import reverse
from django.utils import timezone
from django.db.models import Sum,Count
from datetime import timedelta,date
from catloads_web.models import Order,ProductSale

@method_decorator(login_required, name='dispatch')
class DashboardView(UserPassesTestMixin, View):
    template_name = 'catloads_admin/index.html'

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        return HttpResponseRedirect(reverse('catloadsadmin:login'))

    def get(self, request):
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        first_day_current_month = today.replace(day=1)
        first_day_last_month = (first_day_current_month - timedelta(days=1)).replace(day=1)
        last_day_last_month = first_day_current_month - timedelta(days=1)
        year_start = today.replace(month=1, day=1)
        months_data = []
        most_ordered_products = ProductSale.objects.annotate(
            order_count=Count('order_items')).order_by('-order_count')[:10]
        
        recent_orders=Order.objects.filter(is_deleted=False).order_by('-id').annotate( items_count=Count('items'))

        try:
            def get_sales_data(start_date, end_date):
                sales = Order.objects.filter(created_on__date__gte=start_date, created_on__date__lte=end_date, order_status=2)
                income = sales.aggregate(total_income=Sum('total_price'))['total_income'] or Decimal(0.00)
                return sales.count(), income
            for month in range(1, today.month + 1):  # Loop through each month up to the current month
                first_day = date(today.year, month, 1)
                last_day = first_day.replace(day=28) + timedelta(days=4)  # this will always give the last day of the month
                last_day = last_day - timedelta(days=last_day.day - 1)
                _, monthly_income = get_sales_data(first_day, last_day)
                months_data.append((first_day.strftime('%B'), monthly_income))
                
            todays_count, todays_income = get_sales_data(today, today)
            month_count, month_income = get_sales_data(first_day_last_month, last_day_last_month)
            yesterdays_count, yesterdays_income = get_sales_data(yesterday, yesterday)
            current_month_count, current_month_income = get_sales_data(first_day_current_month, today)
            last_month_count, last_month_income = get_sales_data(first_day_last_month, last_day_last_month)

            def calculate_percentage(current, previous):
                return round(abs(((current - previous) / previous * 100))) if previous else 0

            def status_indicator(current, previous):
                if current > previous:
                    return 1  # Positive change
                elif current < previous:
                    return 3  # Negative change
                return 2  # No change

            context = {
                'todays_income': todays_income,
                'todays_sale': todays_count,
                'month_sale':month_count,
                'month_income':month_income,
                'today_income_percentage': calculate_percentage(todays_income, yesterdays_income),
                'month_income_percentage': calculate_percentage(current_month_income, last_month_income),
                'today_sale_percentage': calculate_percentage(todays_count, yesterdays_count),
                'month_sale_percentage': calculate_percentage(current_month_count, last_month_count),
                'diff_status_sale_today': status_indicator(todays_count, yesterdays_count),
                'diff_status_sale_month': status_indicator(current_month_count, last_month_count),
                'diff_status_income_month': status_indicator(current_month_income, last_month_income),
                'diff_status_income_today': status_indicator(todays_income, yesterdays_income),
                'months_data':months_data   ,
                'most_ordered_products':most_ordered_products,
                'recent_orders':recent_orders[:10],


            }

            return render(request, self.template_name, context=context)
        except Exception as e:
            print("Error in dashboard view: ", e)
            return HttpResponse(e)
