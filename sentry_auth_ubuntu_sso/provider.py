from __future__ import absolute_import

import logging
from uuid import uuid4

from django_openid_auth.views import login_begin, login_complete
from sentry.auth import AuthView, Provider
from sentry.web.frontend.auth_provider_login import AuthProviderLoginView


class OpenIDLoginBegin(AuthView):

    def dispatch(self, request, helper):
        if helper.fetch_state('state'):
            return helper.next_step()

        state = uuid4().hex
        helper.bind_state('state', state)
        return login_begin(request, login_complete_view='sentry-auth-sso')


class OpenIDLoginComplete(AuthView):

    def dispatch(self, request, helper):
        login_complete(request)
        return helper.next_step()


class BindUser(AuthView):

    def dispatch(self, request, helper):
        helper.bind_state('user', request.user)
        return helper.next_step()


class LoginView(AuthProviderLoginView):

    # override dispatch method to remove the csrf protection
    # as django-openid-auth will POST back to this view after login
    # is completed
    def dispatch(self, request, *args, **kwargs):
        if self.is_auth_required(request, *args, **kwargs):
            return self.handle_auth_required(request, *args, **kwargs)

        if self.is_sudo_required(request, *args, **kwargs):
            return self.handle_sudo_required(request, *args, **kwargs)

        args, kwargs = self.convert_args(request, *args, **kwargs)

        request.access = self.get_access(request, *args, **kwargs)

        if not self.has_permission(request, *args, **kwargs):
            return self.handle_permission_required(request, *args, **kwargs)

        self.request = request
        self.default_context = self.get_context_data(request, *args, **kwargs)

        return self.handle(request, *args, **kwargs)


class UbuntuSSOProvider(Provider):
    name = 'Ubuntu SSO'

    def get_auth_pipeline(self):
        return [
            OpenIDLoginBegin(),
            OpenIDLoginComplete(),
            BindUser(),
        ]

    def get_setup_pipeline(self):
        return [
            BindUser(),
        ]

    def build_identity(self, state):
        user = state.get('user')
        return {
            'name': user.get_full_name(),
            'id': user.id,
            'email': user.email,
        }

    def refresh_identity(self, auth_identity):
        pass

    def build_config(self, state):
        return {}
