from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse

from .forms import ProfileForm, UserLoginForm, UserRegisterForm
from .models import Profile


class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    authentication_form = UserLoginForm

    def get_success_url(self):
        user = self.request.user
        if user.is_staff:
            return reverse('dashboard_home')
        return reverse('cards_feed')


def register_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('dashboard_home')
        return redirect('cards_feed')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.get_or_create(
                user=user,
                defaults={'display_name': user.first_name}
            )
            login(request, user)
            return redirect('preferences')
    else:
        form = UserRegisterForm()

    return render(request, 'users/register.html', {'form': form})


@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(
        user=request.user,
        defaults={'display_name': request.user.first_name}
    )
    return render(request, 'users/profile.html', {'profile': profile})


@login_required
def profile_edit_view(request):
    profile, _ = Profile.objects.get_or_create(
        user=request.user,
        defaults={'display_name': request.user.first_name}
    )

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'users/profile_edit.html', {'form': form})
