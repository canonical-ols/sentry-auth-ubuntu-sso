from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase

from sentry_auth_ubuntu_sso.models import UserGroup


User = get_user_model()


class UserGroupTestCase(TestCase):

    def test_repr(self):
        user = User(username='foo')
        group = Group(name='bar')
        user_group = UserGroup(user=user, group=group)
        self.assertEqual(repr(user_group), '<UserGroup: user=foo, group=bar>')
