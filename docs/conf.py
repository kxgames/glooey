#!/usr/bin/env python3

import os, sys; sys.path.insert(0, os.path.abspath('.'))
import glooey
from autoclasstoc import Section, PublicMethods, PublicDataAttrs

## General configuration

project = 'Glooey'
copyright = '2014, Kale Kundert'
author = 'Kale Kundert'
version = glooey.__version__
release = glooey.__version__

master_doc = 'index'
source_suffix = '.rst'
templates_path = ['.templates']
exclude_patterns = ['.build', 'Thumbs.db', '.DS_Store']
html_static_path = ['.static']
needs_sphinx = '3.1'

## Extension configuration

extensions = [ #
    'glooey_ext',
    'autoclasstoc',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.coverage',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
]
intersphinx_mapping = { #
        'pyglet': ('http://pyglet.readthedocs.io/en/latest', None),
}
autodoc_default_flags = [ #
]
autosummary_generate = True
autosummary_generate_overwrite = True
pygments_style = 'sphinx'
todo_include_todos = False
default_role = 'any'

def is_custom(name, attr):
    from inspect import isclass
    return name.startswith('custom_') or \
            (isclass(attr) and issubclass(attr, glooey.Widget))

def is_virtual(name):
    return name.startswith('do_')

class CustomAttrs(Section):
    key = 'custom-props'
    title = "Custom attributes:"

    def predicate(self, name, attr, meta):
        return is_custom(name, attr)

class CustomMethods(Section):
    key = 'custom-methods'
    title = "Customizable methods:"

    def predicate(self, name, attr, meta):
        return is_virtual(name)

class OtherPublicMethods(PublicMethods):

    def predicate(self, name, attr, meta):
        return super().predicate(name, attr, meta) and not \
                is_custom(name, attr) and not \
                is_virtual(name)

class OtherPublicDataAttrs(PublicDataAttrs):

    def predicate(self, name, attr, meta):
        return super().predicate(name, attr, meta) and not \
                is_custom(name, attr) and not \
                is_virtual(name)

autoclasstoc_sections = [
        'custom-props',
        'custom-methods',
        'public-attrs',
        'public-methods',
        'private-attrs',
        'private-methods',
]

## Options for HTML output

from sphinx_rtd_theme import get_html_theme_path
html_theme = "sphinx_rtd_theme"
html_theme_path = [get_html_theme_path()]
html_favicon = 'favicon.ico'

