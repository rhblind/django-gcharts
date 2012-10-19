.. django-gcharts documentation master file, created by
   sphinx-quickstart on Mon Oct 15 14:17:29 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

##########################################
Welcome to django-gcharts's documentation!
##########################################

This library is an implementation of (parts of) the Google Visualization API.
It is written as a `Django <https://www.djangoproject.com/>`_ reusable app, and contains
a custom QuerySet and a manager which acts as a bridge between the Django QuerySet and
the `gviz_api <http://code.google.com/p/google-visualization-python/>`_ python library from
Google.

Installation
============

First, install the requirements.

* `gviz_api library from Google <http://code.google.com/p/google-visualization-python/>`_

From Python Package Index
-------------------------
django-gcharts exists in the python package index, and can be installed by executing either
of the following commands::

   $ pip install django-gcharts
   $ easy_install django-gcharts
   
From source
-----------
If you prefer to download the source code and build it yourself, this can be done by following
these steps::

   $ git clone https://github.com/rhblind/django-gcharts.git
   $ cd django-gcharts
   $ python setup.py install

The source code also includes a demo site which is not available in the pypi package. This is
just a simple page displaying a couple of charts for demonstration purposes, as well as some source
examples on how you can use this library for extracting chartable data from your models.

To fire up the demo site, execute the following commands inside the django-gcharts directory
you just cloned::

   $ python manage.py syncdb
   $ python manage.py initdata
   $ python manage.py runserver
   
Then point your browser at `http://localhost:8000 <http://localhost:8000>`_
and you should see some charts displayed.

External resources
==================
* `django-gcharts source code <https://github.com/rhblind/django-gcharts/>`_
* `gviz_api source code <http://code.google.com/p/google-visualization-python/>`_
* `Google Visualization API documentation <https://developers.google.com/chart/interactive/docs/reference>`_

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

