from __future__ import absolute_import

from django.conf.urls import *
from django.views.decorators.csrf import csrf_exempt
from sentry.conf import urls

from sentry_auth_ubuntu_sso.provider import LoginView


urlpatterns = patterns('sentry_auth_ubuntu_sso.provider',
    url(r'^openid/', include('django_openid_auth.urls')),
    # override sentry-auth-sso to replace with equivalent but csrf-exempt view
    url(r'^auth/sso/$', csrf_exempt(LoginView.as_view()),
        name='sentry-auth-sso'),
) + urls.urlpatterns
