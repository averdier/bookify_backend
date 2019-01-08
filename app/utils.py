# -*- coding: utf-8 -*-

import os
from jinja2 import Template


def render_email(template_name, data):
    basedir = os.path.abspath(os.path.dirname(__file__))

    with open(basedir + '/templates/' + template_name) as template_file:
        template = Template(template_file.read())

        return template.render(data)
