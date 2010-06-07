#!/usr/bin/env python

import sys
from util import text

def import_template_module(template_name):
    try:
        return sys.modules[template_name]
    except KeyError:
        __import__(template_name, globals(), locals(), [])
        return sys.modules[template_name]

def import_template_class(template_name):
    template_module = import_template_module(template_name)
    classname = template_name.split('.')[-1]
    return getattr(template_module, classname)

def render_template(name, display):
    template_name = 'events.compiled_templates.%s' % name
    template_class = import_template_class(template_name)
    template = template_class(search_list=[display], default_filter=text.html_escape)
    return template.main().strip()

