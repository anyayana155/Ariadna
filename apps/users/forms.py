from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import Profile

User = get_user_model()


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(label='Email')
    first_name = forms.CharField(label='Имя', max_length=150)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'password1', 'password2')

    def clean_email(self):
        email = (self.cleaned_data.get('email') or '').strip().lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже существует.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        email = self.cleaned_data['email']
        user.email = email
        user.first_name = self.cleaned_data['first_name'].strip()

        base_username = email.split('@')[0][:140] or 'user'
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exclude(pk=user.pk).exists():
            username = f'{base_username[:130]}_{counter}'
            counter += 1

        user.username = username

        if commit:
            user.save()
        return user


class UserLoginForm(AuthenticationForm):
    username = forms.EmailField(label='Email')
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['display_name', 'avatar']
        labels = {
            'display_name': 'Как к вам обращаться',
            'avatar': 'Аватар',
        }
