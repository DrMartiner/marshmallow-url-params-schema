#!/usr/bin/env python
import sys
from distutils.core import setup

if sys.version_info < (3, 6, 0):
    raise RuntimeError("it doesn't support Python < 3.6")

setup(
    name='marshmallow-url-params-schema',
    version='0.9.0',
    install_requires=[
        'marshmallow==3.0.0rc4',
    ],
    extras_require={
        'testing': [
            'tox',
            'isort',
            'flake8',
            'pytest',
            'twine',
        ]
    },
    url='https://github.com/DrMartiner/marshmallow-url-params-schema',
    license='MIT',
    author='Aleksei Kuzmin',
    author_email='DrMartiner@GMail.Com',
    description='Marshmallow JSON schema for URL params'
)
