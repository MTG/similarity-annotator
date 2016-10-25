from django import forms
from django.contrib import auth
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import MultipleObjectsReturned


class CaptchaWidget(forms.Widget):
    """
    A Widget class for captcha. Converts the recaptcha response field into a readable field for the form
    """

    # make sure that labels are not displayed either
    is_hidden = True

    recaptcha_response_field = 'g-recaptcha-response'

    def render(self, *args, **kwargs):
        return ''

    def value_from_datadict(self, data, files, name):
        return data.get(self.recaptcha_response_field, None)


class RegistrationForm(forms.Form):
    username = forms.RegexField(
        label=_("Username"), min_length=3, max_length=30, regex=r'^[\w.]*$',
        help_text=_("Required. 30 characters or fewer. Alphanumeric characters only "
                    "(letters, digits and underscores)."),
        error_messages={
            'invalid': _("This value must contain only letters, numbers and underscores.")
        })
    email = forms.EmailField(
        label=_("Email"),
        help_text=_("We will send you a confirmation/activation email, so make sure this is correct!."))
    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput, min_length=6)
    password2 = forms.CharField(label=_("Password confirmation"), widget=forms.PasswordInput, min_length=6)

    def clean_username(self):
        username = self.cleaned_data["username"]
        try:
            auth.models.User.objects.get(username__iexact=username)
            raise forms.ValidationError(_("A user with that username already exists."))
        except auth.models.User.DoesNotExist:  # @UndefinedVariable
            return username

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1", "")
        password2 = self.cleaned_data["password2"]
        if password1 != password2:
            raise forms.ValidationError(_("The two password fields didn't match."))
        return password2

    def clean_email(self):
        email = self.cleaned_data.get("email", "")
        try:
            auth.models.User.objects.get(email__iexact=email)
            raise forms.ValidationError(_("A user using that email address already exists."))
        except MultipleObjectsReturned:
            raise forms.ValidationError(_("A user using that email address already exists."))
        except auth.models.User.DoesNotExist:  # @UndefinedVariable
            pass

        return email

    def save(self):
        username = self.cleaned_data["username"]
        email = self.cleaned_data["email"]
        password = self.cleaned_data["password2"]

        user = auth.models.User(username=username, email=email, password=password, is_staff=False, is_active=True,
                                is_superuser=False)
        user.set_password(password)
        user.save()

        return user
