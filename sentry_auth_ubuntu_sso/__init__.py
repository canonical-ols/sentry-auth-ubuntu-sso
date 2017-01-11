from __future__ import absolute_import

from sentry.auth import register

from sentry_auth_ubuntu_sso.provider import UbuntuSSOProvider


register('ubuntu-sso', UbuntuSSOProvider)
