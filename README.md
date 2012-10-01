Yet another Google Charts library for Django

- Requires installation of the gviz_api library which is freely available from Google.
- See http://code.google.com/p/google-visualization-python/ for details.

## Note ##
This library is yet in pre-alpha development mode, and only uploaded to github for the purpose of having it
for my own sake. It's still not ready for use, do _NOT_ use this for anything except experimenting.

Please feel free to fork or submit patches ;)

### Disclaimer ###
This library is heavy influenced by [mvasilkov's django-google-charts](https://github.com/mvasilkov/django-google-charts),
and some of the code (template tags and javascript code) are directly copied from him. I've done some minor adjustments to
make it work for my approach.

### About django-gcharts ###
As I find mvasilkov's approach very clever, I think it's can be done easier. My solution is to subclass the QuerySet
which we are all familiar with, and create a custom manager which can be hooked into the models you wish to draw a chart for.
This is really just a simple wrapper to Google's gviz_api module (which is a requirement for this module to work. See above.).

### Examples ###
Coming soon™