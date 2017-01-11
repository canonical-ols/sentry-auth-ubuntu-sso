#!/usr/bin/env python
"""
sentry-auth-ubuntu-sso
==================

:copyright: (c) 2017 Canonical
"""
from setuptools import setup, find_packages


install_requires = [
    'sentry>=7.0.0',
    'django-openid-auth==0.7',
]

setup(
    name='sentry-auth-ubuntu-sso',
    version='0.1.0',
    author='Ricardo Kirkner',
    author_email='online-services@lists.canonical.com',
    url='http://www.canonical.com',
    description='Ubuntu SSO authentication provider for Sentry',
    long_description=__doc__,
    license='Apache 2.0',
    packages=find_packages(),
    zip_safe=False,
    install_requires=install_requires,
    include_package_data=True,
    entry_points={
        'sentry.apps': [
            'auth_ubuntu_sso = sentry_auth_ubuntu_sso',
        ],
    },
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ],
)
