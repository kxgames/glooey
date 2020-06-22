#!/usr/bin/env python3

import os, sys
import glooey
from autoclasstoc import Section, PublicMethods, PublicDataAttrs
sys.path.insert(0, os.path.abspath('.'))  # glooey_ext

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
        'vecrec': ('https://vecrec.readthedocs.io/en/latest', None),
}
autodoc_default_flags = [ #
]
autosummary_generate = True
pygments_style = 'sphinx'
todo_include_todos = False
default_role = 'smartxref'
smartxref_overrides = {
        'Grid': 'glooey.containers.Grid',
        'HVBox': 'glooey.containers.HVBox',
        'Background': 'glooey.images.Background',
        'Frame': 'glooey.containers.Frame',
        'Label': 'glooey.text.Label',
}
smartxref_literals = {
        'args',
        'atlas',
        'batch',
        '_children',
        'drawing.Grid',
        'EVENT_HANDLED',
        'event_type',
        'EVENT_UNHANDLED',
        "'expand'",
        'expand',
        'flip_x',
        'flip_y',
        'font.load',
        'FormattedDocument',
        'get_script_home',
        'handler',
        'Hbox',
        'Location',
        'media.load',
        'media.Source',
        'Model',
        '__name__',
        'name',
        'parent',
        'path',
        'pyglet.text.formats.attributed',
        'rotate',
        'script_home',
        'self._pending_updates',
        'size',
        'size=0',
        'size=100',
        "size='expand'",
        'sizes',
        'streaming',
        'Texture',
        'UnformattedDocument',
        'w1',
        'w2',
        'w3',
}

def is_custom(name, attr):
    from inspect import isclass
    return name.startswith('custom_') or \
            (isclass(attr) and issubclass(attr, glooey.Widget)) or \
            (name[0].isupper() and attr is None)

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

