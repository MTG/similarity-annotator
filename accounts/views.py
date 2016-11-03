from django.shortcuts import redirect, render
from django.contrib import auth
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from accounts import forms
from django.conf import settings
from django.contrib.auth import views as authviews


def login(request):
    redirect_url = request.GET.get('next', settings.LOGIN_REDIRECT_URL)
    if request.user.is_authenticated():
        return redirect(redirect_url)
    return authviews.login(request,
                           template_name="accounts/login.html",
                           redirect_field_name='next',
                           extra_context={'redirect_url': redirect_url})


def logout(request):
    auth.logout(request)
    return redirect('/')


def registration(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse("accounts-user", args=[request.user.username]))

    if request.method == "POST":
        form = forms.RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'accounts/registration_done.html')
    else:
        form = forms.RegistrationForm()

    return render(request, 'accounts/registration.html', {'form': form})
