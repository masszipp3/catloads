from django import forms
from catloads_web.models import CustomUser
from django.contrib.auth.forms import UserChangeForm


class RegisterForm(forms.ModelForm):

    class Meta:
        model = CustomUser
        fields = ['name', 'email', 'city', 'phone','password']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name', 'required': True}),
            'email': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Email', 'required': True}),
            'phone': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Phone', 'required': True}),
            'password':forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password', 'required': True}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.usertype=2
        user.username=self.cleaned_data['email']
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user
    

class EditUserForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ['name', 'email', 'city', 'phone']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name', 'required': True}),
            'email': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Email', 'required': True}),
            'phone': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Phone', 'required': True}),
            'city': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Phone', 'required': False}),
            # Password field widget is defined above, separately
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.usertype = 2
        user.username = self.cleaned_data['email']

        if commit:
            user.save()
        return user    