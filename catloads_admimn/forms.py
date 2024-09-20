from django import forms
from catloads_web.models import Category,Product,PromoCode,Banner,ProductSale,CountryPrice,Country
from django_ckeditor_5.widgets import CKEditor5Widget
from django.core.exceptions import ObjectDoesNotExist



class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name','icon']
        
        widgets = {
            'name': forms.TextInput(attrs={'class': 'flex-grow', 'placeholder': 'Category name', 'required': True}),
            # 'slug': forms.TextInput(attrs={'class': 'flex-grow','placeholder': 'Slug'}),
            'icon': forms.FileInput(attrs={'id':"myFile" ,'name':"filename"}),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category','name','price','product_size','download_link','product_unit']
        
        widgets = {
            'name': forms.TextInput(attrs={'class': 'mb-10', 'placeholder': 'Enter product name', 'required': True,'tabindex':"0",'aria-required':"true"}),
            'category' : forms.Select(attrs={'required':True}),
            'price': forms.NumberInput(attrs={'class': 'mb-10', 'placeholder': 'Enter product Price', 'required': True,'tabindex':"0",'aria-required':"true"}),
            'product_unit' : forms.Select(attrs={'required':True}),
            'product_size' : forms.TextInput(attrs={'class': 'mb-10', 'placeholder': 'Enter Size', 'required': True,'tabindex':"0",'aria-required':"true"}),
            'download_link':forms.TextInput(attrs={'class': 'mb-10', 'placeholder': 'Enter Download Link', 'required': True,'tabindex':"0",'aria-required':"true"}),
        }

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        # Filter the category queryset to include only categories where is_deleted is False
        self.fields['category'].queryset = self.fields['category'].queryset.filter(is_deleted=False)    

class PromoCodeForm(forms.ModelForm):
    class Meta:
        model = PromoCode
        fields = ['code','discount_value','valid_from','valid_to','minimum_order_value','usage_limit']
        
        widgets = {
            'code': forms.TextInput(attrs={'class': 'flex-grow', 'placeholder': 'Promo Code', 'required': True,'tabindex':"0",'aria-required':"true"}),
            'discount_value' : forms.NumberInput(attrs={'class': 'flex-grow', 'placeholder': 'Discount', 'required': True,'tabindex':"0",'aria-required':"true"}),
            'valid_from': forms.DateTimeInput(attrs={'class': 'flex-grow', 'type': 'datetime-local', 'required': True,'tabindex':"0",'aria-required':"true"}),
            'valid_to' : forms.DateTimeInput(attrs={'class': 'flex-grow','type': 'datetime-local', 'required': True,'tabindex':"0",'aria-required':"true"}),
            'minimum_order_value' : forms.NumberInput(attrs={'class': 'flex-grow','placeholder': 'Min Order Value', 'required': True,'tabindex':"0",'aria-required':"true"}),
            'usage_limit':forms.NumberInput(attrs={'class': 'flex-grow', 'placeholder': 'Usage Limit', 'required': True,'tabindex':"0",'aria-required':"true"}),
        }

class BannerForm(forms.ModelForm):
    class Meta:
        model = Banner
        fields = ['banner_head','image',]
        
        widgets = {
            'banner_head': forms.TextInput(attrs={'class': 'flex-grow', 'placeholder': 'Banner name', 'required': True}),
            'image': forms.FileInput(attrs={'id':"myFile" ,'name':"filename"}),
        }

class ProductSaleForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditor5Widget())
    class Meta:
        model = ProductSale
        fields = ['name','description','caption','price','discount','thumbnail','rating','sale_tag','sale_tag_color']
        
        widgets = {
            'name': forms.TextInput(attrs={'class': 'mb-10', 'placeholder': 'Enter Sale name', 'required': True,'tabindex':"0",'aria-required':"true"}),
            'sale_tag': forms.TextInput(attrs={'class': 'mb-10', 'placeholder': 'Enter Sale Tag','tabindex':"0",'aria-required':"true"}),
            'sale_tag_color': forms.TextInput(attrs={'class': 'mb-10', 'placeholder': 'Enter Sale Tag','tabindex':"0",'aria-required':"true"}),
            'caption' : forms.Textarea(attrs={'class': 'mb-10', 'placeholder': 'Enter Caption', 'required': True,'tabindex':"0",'aria-required':"true"}),
            'price': forms.NumberInput(attrs={'class': 'mb-10', 'placeholder': 'Enter product Price', 'required': True,'tabindex':"0",'aria-required':"true"}),
            'rating': forms.NumberInput(attrs={'class': 'mb-10', 'placeholder': 'Enter Rating Here', 'required': True,'tabindex':"0",'aria-required':"true"}),
            'discount' : forms.NumberInput(attrs={'class': 'mb-10', 'placeholder': 'Enter Discount', 'required': True,'tabindex':"0",'aria-required':"true"}),
            'thumbnail' : forms.FileInput(attrs={'id':"myFile" }),
            # 'description':forms.Textarea(attrs={'class': 'mb-10', 'placeholder': 'Enter Discription', 'required': True,'tabindex':"0",'aria-required':"true"}),
        }  

    def save(self, commit=True):
        product_sale = super().save(commit=False)
        price = self.cleaned_data.get('price')
        if commit:
            product_sale.save()
        try:
            default_country = Country.objects.get(default=True)
        except ObjectDoesNotExist:
            default_country = Country.objects.get(name='United States', code='US')

        CountryPrice.objects.create(
            product_sale=product_sale,
            country=default_country,
            price=price,
            discount=self.cleaned_data.get('discount', 0.00) 
        )
        return product_sale      