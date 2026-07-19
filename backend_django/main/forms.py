"""Forms used across auth and profile flows."""
from django import forms
from django.contrib.auth.models import User


class SignupForm(forms.Form):
    first_name = forms.CharField(max_length=64)
    last_name = forms.CharField(max_length=64, required=False)
    email = forms.EmailField()
    password = forms.CharField(min_length=6, max_length=128)

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(max_length=128)


class ProfileUpdateForm(forms.Form):
    name = forms.CharField(max_length=128, required=False)
    phone = forms.CharField(max_length=32, required=False)
    country = forms.CharField(max_length=64, required=False)


class BookingForm(forms.Form):
    consultant_id = forms.CharField(max_length=64)
    consultant_name = forms.CharField(max_length=128)
    date = forms.CharField(max_length=64)
    time = forms.CharField(max_length=32)
    name = forms.CharField(max_length=128, required=False)
    email = forms.EmailField(required=False)
    message = forms.CharField(required=False, widget=forms.Textarea)
