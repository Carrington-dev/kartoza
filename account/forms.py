from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
# from cart.models import Cart, CartItem
from django.core.cache import cache
from urllib.parse import urlparse, urlunparse

from django.conf import settings
# Avoid shadowing the login() and logout() views below.
from django.contrib.auth import (
    REDIRECT_FIELD_NAME, get_user_model, login as auth_login,
    logout as auth_logout, update_session_auth_hash,
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import (
    AuthenticationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm,
)
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect, QueryDict
from django.shortcuts import resolve_url
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.http import (
    url_has_allowed_host_and_scheme, urlsafe_base64_decode,
)
from django.core.mail import get_connection, EmailMultiAlternatives

from django.contrib.auth.views import PasswordContextMixin

from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from account.models import  UserAccount
# from account.models import Profile
from typing import Final
from django.template import loader
import unicodedata

from django import forms
from django.contrib.auth import (
    authenticate, get_user_model, password_validation,
)
from django.contrib.auth.hashers import (
    UNUSABLE_PASSWORD_PREFIX, identify_hasher,
)
from django.contrib.staticfiles import finders

from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.text import capfirst
from django.utils.translation import gettext, gettext_lazy as _
from email.mime.image import MIMEImage
from typing import Dict, Final, Optional
UserModel = get_user_model()
# Constants for sending password-reset emails.
LOGO_FILE_PATH: Final[str] = "/static/images/logo.png"
LOGO_CID_NAME: Final[str] = "logo"
PASSWORD_RESET_FORM_TEMPLATE: Final[str] = "registration/password_reset_form.html"
PASSWORD_RESET_HTML_TEMPLATE: Final[str] = "registration/password_reset_email.html"
PASSWORD_RESET_TEXT_TEMPLATE: Final[str] = "registration/password_reset_email.txt"
PASSWORD_RESET_SUBJECT_TEMPLATE: Final[str] = "registration/password_reset_subject.txt"
SUPPORT_EMAIL: Final[str] = "support@oftmart.com"
FROM_EMAIL: Final[str] = f"Oftmart Support <{SUPPORT_EMAIL}>"


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required. Add a valid email address.')

    class Meta:
        model = UserAccount
        fields = ('email', 'username', 'is_subscribed', 'password1', 'password2', )
        # widgets = {
        #     'country': forms.SelectMultiple(attrs={'class': 'input-text', 'autofocus': True}),
        #     }



# class ProfileUpdateForm(forms.ModelForm):
# 	class Meta:
# 		model = Profile
# 		fields = ['image',]

class AccountAuthenticationForm(forms.ModelForm):

	password = forms.CharField(label='Password', widget=forms.PasswordInput)

	class Meta:
		model = UserAccount
		fields = ('email', 'password')
        

	def clean(self):
		if self.is_valid():
			email = self.cleaned_data['email']
			password = self.cleaned_data['password']
			if not authenticate(email=email, password=password):
				raise forms.ValidationError("Invalid login")


class AccountUpdateForm(forms.ModelForm):

	class Meta:
		model = UserAccount
		fields = ('email', 'username', 'first_name','last_name', 'location','longitude', 'latitude', 
		 'phone',)
		# fields =  '__all__' 

	def clean_email(self):
		email = self.cleaned_data['email']
		try:
			account = UserAccount.objects.exclude(pk=self.instance.pk).get(email=email)
		except UserAccount.DoesNotExist:
			return email
		raise forms.ValidationError('Email "%s" is already in use.' % account)

	def clean_username(self):
		username = self.cleaned_data['username']
		try:
			account = UserAccount.objects.exclude(pk=self.instance.pk).get(username=username)
		except UserAccount.DoesNotExist:
			return username
		raise forms.ValidationError('Username "%s" is already in use.' % username)
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['username'].widget.attrs.update({'placeholder': 'Enter your username'})
		self.fields['email'].widget.attrs.update({'placeholder': 'Email'})
		
		# self.fields['comment'].widget.attrs.update(size='40')
		for field in self.fields:
			# name = field.name
			# name = str(name)
			self.fields[field].widget.attrs.update({'class': 'form-control'})

def get_as_mime_image(image_file_path: str, cid_name: str) -> MIMEImage:
    """Fetch an image file and return it wrapped in a ``MIMEImage`` object for use 
    in emails.

    After the ``MIMEImage`` has been attached to an email, reference the image in 
    the HTML using the Content ID.

    Example:

    If the CID name is "logo", then the HTML reference would be:

    <img src="cid:logo" />

    Args:
        image_file_path: The path of the image. The path must be findable by the 
            Django staticfiles app.
        cid_name: The Content-ID name to use within the HTML email body to 
            reference the image.

    Raises:
        FileNotFoundError: If the image file cannot be found by the staticfiles app.

    Returns:
        MIMEImage: The image wrapped in a ``MIMEImage`` object and the Content ID 
        set to ``cid_name``.
    """
    paths = finders.find(image_file_path)
    if paths is None:
        raise FileNotFoundError(f"{image_file_path} not found in static files")

    if isinstance(paths, list):
        final_path = paths[0]
    else:
        final_path = paths
    with open(final_path, 'rb') as f:
        image_data = f.read()

    mime_image = MIMEImage(image_data)
    mime_image.add_header("Content-ID", f"<{cid_name}>")
    return mime_image

class CustomPasswordResetForm(PasswordResetForm):
	
	def send_mail(self, subject_template_name, email_template_name,
	# context,
	context: Dict[str, str],
	from_email, to_email, html_email_template_name=None):
		""" Sends a django.core.mail.EmailMultiAlternatives to `to_email`."""
		
		
		subject = loader.render_to_string(subject_template_name, context)
		# Email subject *must not* contain newlines
		subject = ''.join(subject.splitlines())
		body = loader.render_to_string(email_template_name, context)


		email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
		# New line introduce
		email_message.attach_alternative(body, 'text/html')

		if html_email_template_name is not None:
			html_email = loader.render_to_string(html_email_template_name, context)
			email_message.attach_alternative(html_email, 'text/html')
			mime_image = get_as_mime_image(image_file_path=LOGO_FILE_PATH, cid_name=LOGO_CID_NAME)
			email_message.attach(mime_image) 

		email_message.send()


# class PasswordResetForm(forms.Form):
#     email = forms.EmailField(
#         label=_("Email"),
#         max_length=254,
#         widget=forms.EmailInput(attrs={'autocomplete': 'email'})
#     )

#     def send_mail(self, subject_template_name, email_template_name,
#                   context, from_email, to_email, html_email_template_name=None):
#         """
#         Send a django.core.mail.EmailMultiAlternatives to `to_email`.
#         """
#         subject = loader.render_to_string(subject_template_name, context)
#         # Email subject *must not* contain newlines
#         subject = ''.join(subject.splitlines())
#         body = loader.render_to_string(email_template_name, context)

#         email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
#         if html_email_template_name is not None:
#             html_email = loader.render_to_string(html_email_template_name, context)
#             email_message.attach_alternative(html_email, 'text/html')

#         email_message.send()

#     def get_users(self, email):
#         """Given an email, return matching user(s) who should receive a reset.

#         This allows subclasses to more easily customize the default policies
#         that prevent inactive users and users with unusable passwords from
#         resetting their password.
#         """
#         email_field_name = Account.get_email_field_name()
#         active_users = Account._default_manager.filter(**{
#             '%s__iexact' % email_field_name: email,
#             'is_active': True,
#         })
#         return (
#             u for u in active_users
#             if u.has_usable_password() and _unicode_ci_compare(email, getattr(u, email_field_name))
#         )

#     def save(self, domain_override=None,
#              subject_template_name='registration/password_reset_subject.txt',
#              email_template_name='registration/password_reset_email.html',
#              use_https=False, token_generator=default_token_generator,
#              from_email=None, request=None, html_email_template_name=None,
#              extra_email_context=None):
#         """
#         Generate a one-use only link for resetting password and send it to the
#         user.
#         """
#         email = self.cleaned_data["email"]
#         if not domain_override:
#             current_site = get_current_site(request)
#             site_name = current_site.name
#             domain = current_site.domain
#         else:
#             site_name = domain = domain_override
#         email_field_name = Account.get_email_field_name()
#         for user in self.get_users(email):
#             user_email = getattr(user, email_field_name)
#             context = {
#                 'email': user_email,
#                 'domain': domain,
#                 'site_name': site_name,
#                 'uid': urlsafe_base64_encode(force_bytes(user.pk)),
#                 'user': user,
#                 'token': token_generator.make_token(user),
#                 'protocol': 'https' if use_https else 'http',
#                 **(extra_email_context or {}),
#             }
#             self.send_mail(
#                 subject_template_name, email_template_name, context, from_email,
#                 user_email, html_email_template_name=html_email_template_name,
#             )
