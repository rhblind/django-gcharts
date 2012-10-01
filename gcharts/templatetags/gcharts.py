# -*- coding: utf-8 -*-
#
# This code is copied from mvasilkov's django-google-charts on github
# (https://github.com/mvasilkov/django-google-charts) and licensed under 
# the MIT License
#

from django.conf import settings
from django import template
from django.template.loader import render_to_string

register = template.Library()

_api = getattr(settings, "GOOGLECHARTS_API", "1.1")
_packages = getattr(settings, "GOOGLECHARTS_PACKAGES", ["corechart", "table"])

def _remove_quotes(s):
    if s[0] in ('"', "'") and s[-1] == s[0]:
        return s[1:-1]
    return s

# {% gcharts %} ... {% endgcharts %}

class GChartsNode(template.Node):
    def __init__(self, nodelist):
        self._nodelist = nodelist
        
    def render_template(self, template, **kwargs):
        return render_to_string(template, kwargs)
    
    def render(self, context):
        js = self._nodelist.render(context)
        return self.render_template("gcharts/gcharts.html", googlecharts_js=js,
                                    api=_api, packages=_packages)

@register.tag
def gcharts(parser, token):
    nodelist = parser.parse(["endgcharts"])
    parser.delete_first_token()
    return GChartsNode(nodelist)


# {% options "name" %}...{% endoptions %}

class OptionsNode(template.Node):
    def __init__(self, nodelist, name):
        self._nodelist = nodelist
        self._name = name

    def render(self, context):
        '''
        var googlecharts_options_%(name)s = {
            %(data)s
        };
        '''
        return self.render.__doc__ % {'name': self._name, 'data': self._nodelist.render(context)}

@register.tag
def options(parser, token):
    try:
        _, name = token.split_contents()
        name = _remove_quotes(name)
    except ValueError:
        name = 'default'
    nodelist = parser.parse(['endoptions'])
    parser.delete_first_token()
    return OptionsNode(nodelist, name=name)


# {% render "container_id" "data" "options" %}

class RenderNode(template.Node):
    def __init__(self, container, data, options):
        self.container = container
        self.data = template.Variable(data)
        self.options = options
    
    def render(self, context):
        """
        opt = _clone(googlecharts_options_%(options)s);
        opt.container = "%(container)s";
        opt.data = googlecharts_data_%(src)s =
            %(data)s
        googlecharts.push(opt);
        """
        return self.render.__doc__ % {"options": self.options, "container": self.container,
                                      "src": self.data.var, "data": self.data.resolve(context)}

@register.tag
def render(parser, token):
    args = token.split_contents()
    if len(args) < 2:
        raise template.TemplateSyntaxError('%r tag requires at least one argument' % args[0])
    while len(args) < 4:
        args.append('default')
    _, container, data, options = [_remove_quotes(s) for s in args]
    return RenderNode(container=container, data=data, options=options)


