#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup

setup(
    name = "django-gcharts",
    version = "1.0-alpha-1",
    description = "Provides a QuerySet, Manager and other tools for easy integration with the Google charts API",
    long_description = open("README.md").read(),
    keywords = "django google charts graph plot",
    license = open("LICENSE.md").read(),
    author = "Rolf Håvard Blindheim",
    author_email = "rhblind@gmail.com",
    url = "http://github.com/rhblind/django-gcharts",
    install_requires = ["Django>=1.0"],
    zip_safe = False,
    packages = [
        "gcharts",
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
        "License :: OSI Approved :: Apache License",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)