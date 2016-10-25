from django.conf.urls import url
from accounts import views

urlpatterns = [
    # Because these URLs are in the same namespace as usernames, we cannot
    # have a user with one of these names
    url(r'^login/?', views.login, name="accounts-login"),
    url(r'^register/?', views.registration, name="accounts-register"),
]
