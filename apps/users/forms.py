from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Profile


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    username = forms.CharField(max_length=150)
    first_name = forms.CharField(max_length=150, required=False)

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'password1', 'password2')


class UserLoginForm(AuthenticationForm):
    username = forms.EmailField(label='Email')


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('display_name', 'avatar')