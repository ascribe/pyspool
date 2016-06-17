# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import sphinx_rtd_theme

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
]

templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
project = u'pyspool'
copyright = u'2016, ascribe GmbH'
author = u'ascribe GmbH'
version = u'0.1'
release = u'0.1.0'
language = None
exclude_patterns = []
pygments_style = 'sphinx'
todo_include_todos = True
html_theme = 'sphinx_rtd_theme'
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
html_static_path = ['_static']
htmlhelp_basename = 'pyspooldoc'

latex_elements = {}
latex_documents = [
    (master_doc, 'pyspool.tex', u'pyspool Documentation',
     u'ascribe GmbH', 'manual'),
]

man_pages = [
    (master_doc, 'pyspool', u'pyspool Documentation',
     [author], 1)
]

texinfo_documents = [
    (master_doc, 'pyspool', u'pyspool Documentation',
     author, 'pyspool', 'One line description of project.',
     'Miscellaneous'),
]

intersphinx_mapping = {'https://docs.python.org/': None}
