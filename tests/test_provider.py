
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import RequestFactory
from mock import patch

from sentry.auth.exceptions import IdentityNotValid
from sentry.auth.helper import AuthHelper
from sentry.models import Organization, OrganizationMember

from sentry_auth_ubuntu_sso.provider import (
    ROLE_MANAGER,
    BindUser,
    UbuntuSSOProvider,
    UpdateRole,
)


User = get_user_model()


class BindUserTestCase(TestCase):

    def setUp(self):
        super(BindUserTestCase, self).setUp()
        self.user = User.objects.create_user(
            'username', 'user@domain.tld', 'password')
        self.client.login(username='username', password='password')
        self.request = RequestFactory().get('')
        self.request.user = self.user
        self.request.session = self.client.session
        self.org = Organization.objects.create(slug='org')
        self.helper = AuthHelper(
            self.request, self.org, AuthHelper.FLOW_LOGIN,
            provider_key='ubuntu-sso')
        self.helper.state.regenerate({'data': {}, 'step_index': 0})

    def test_dispatch(self):
        view = BindUser()
        with patch.object(self.helper, 'next_step'):
            view.dispatch(self.request, self.helper)

        user_id = self.helper.fetch_state('user_id')
        self.assertEqual(user_id, self.user.id)


class UpdateRoleTestCase(TestCase):

    def setUp(self):
        super(UpdateRoleTestCase, self).setUp()
        self.user = User.objects.create_user(
            'username', 'user@domain.tld', 'password')
        self.client.login(username='username', password='password')
        self.request = RequestFactory().get('')
        self.request.user = self.user
        self.request.session = self.client.session
        self.org = Organization.objects.create(slug='org')
        self.helper = AuthHelper(
            self.request, self.org, AuthHelper.FLOW_LOGIN,
            provider_key='ubuntu-sso')
        self.helper.state.regenerate(
            {'data': {'user_id': self.user.id}, 'step_index': 1})

    def test_do_nothing_if_not_staff(self):
        view = UpdateRole()
        with patch.object(self.helper, 'next_step'):
            view.dispatch(self.request, self.helper)

        user = User.objects.get(id=self.user.id)
        memberships = OrganizationMember.objects.filter(
            user=self.user, role=ROLE_MANAGER)
        self.assertEqual(memberships.count(), 0)

    def test_update_role_if_staff(self):
        self.user.is_staff = True
        self.user.save()
        # make sure user has at least one membership
        OrganizationMember.objects.create(
            user=self.user, organization=self.org, role='user')
        # and make sure none of them has a manager role
        memberships = OrganizationMember.objects.filter(
            user=self.user, role=ROLE_MANAGER)
        self.assertEqual(memberships.count(), 0)

        view = UpdateRole()
        with patch.object(self.helper, 'next_step'):
            view.dispatch(self.request, self.helper)

        user = User.objects.get(id=self.user.id)
        memberships = OrganizationMember.objects.filter(
            user=self.user, role=ROLE_MANAGER)
        self.assertEqual(memberships.count(), 1)

    def test_fail_if_invalid_user_id(self):
        self.helper.state.regenerate(
            {'data': {'user_id': 99}, 'step_index': 2,
             'flow': AuthHelper.FLOW_LOGIN})

        view = UpdateRole()
        with patch('sentry.auth.helper.messages'):
            response = view.dispatch(self.request, self.helper)

        url = reverse('sentry-auth-organization', args=[self.org.slug])
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], url)


class UbuntuSSOProviderTestCase(TestCase):

    def setUp(self):
        super(UbuntuSSOProviderTestCase, self).setUp()
        self.user = User.objects.create_user(
            'username', 'user@domain.tld', 'password')
        self.client.login(username='username', password='password')
        self.request = RequestFactory().get('')
        self.request.user = self.user
        self.request.session = self.client.session
        self.org = Organization.objects.create(slug='org')
        self.helper = AuthHelper(
            self.request, self.org, AuthHelper.FLOW_LOGIN,
            provider_key='ubuntu-sso')
        self.helper.state.regenerate(
            {'data': {'user_id': self.user.id}, 'step_index': 2})

    def test_build_identity(self):
        provider = UbuntuSSOProvider('ubuntu-sso')
        identity = provider.build_identity(self.helper.fetch_state())
        self.assertEqual(identity, {
            'name': self.user.get_full_name(),
            'id': self.user.id,
            'email': self.user.email,
        })

    def test_build_identity_for_invalid_user(self):
        self.helper.state.regenerate(
            {'data': {'user_id': 99}, 'step_index': 2})

        provider = UbuntuSSOProvider('ubuntu-sso')
        self.assertRaises(
            IdentityNotValid,
            provider.build_identity, self.helper.fetch_state())
