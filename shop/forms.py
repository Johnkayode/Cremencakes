from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.forms.widgets import PasswordInput, TextInput, EmailInput

class CustomAuthForm(AuthenticationForm):
    username = forms.CharField(widget=TextInput(attrs={'class':'form-control pass', 'placeholder':'Username', 'required':'required'}))
    password = forms.CharField(widget=PasswordInput(attrs={'class':'form-control pass','placeholder':'Password', 'required':'required'}))

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control pass', 'placeholder':'Password', 'required':'required'}))
    password_ = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control pass', 'placeholder':'Confirm Password', 'required':'required'}))

    class Meta:
        model = User
        fields = {'username','first_name','last_name','email'} 
        widgets = {'username':TextInput(attrs={'class':'form-control-lg pass', 'placeholder':'Username', 'required':'required'}),
        'first_name':TextInput(attrs={'class':'form-control-lg pass', 'placeholder':'First Name', 'required':'required'}),
        'last_name':TextInput(attrs={'class':'form-control-lg pass', 'placeholder':'Last Name', 'required':'required'}),
        'email': EmailInput(attrs={'class':'form-control-lg pass', 'placeholder':'Email', 'required':'required'}),}

class EmailSubForm(forms.Form):
    email = forms.CharField(widget=forms.EmailInput(attrs={'class':'form-control','placeholder':'Enter your email', 'required':'required'}))


class FeedbackForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Your Name', 'required':'required'}))
    email = forms.CharField(widget=forms.EmailInput(attrs={'class':'form-control','placeholder':'Your Email', 'required':'required'}))
    subject = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Subject', 'required':'required'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control', 'placeholder':'Message', 'required':'required'}))