#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup

setup(
    name = "django-gcharts",
    version = "v1.0-alpha-1",
    description = "Provides a QuerySet, Manager and other tools for easy integration with the Google Visualization API",
    long_description = open("README.md").read(),
    keywords = "django google charts graph plot",
    license = open("LICENSE.md").read(),
    author = "Rolf Håvard Blindheim",
    author_email = "rhblind@gmail.com",
    url = "http://github.com/rhblind/django-gcharts",
    packages = [
        "gcharts",
        "gcharts.tests",
        "gcharts.templatetags"
    ],
    package_data = {
        "gcharts": [
            "templates/*"
        ]
    },
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)