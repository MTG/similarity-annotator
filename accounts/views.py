from django.shortcuts import redirect
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
