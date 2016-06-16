"""
``pyspool`` is a reference implementation of the Secure Public Online Ownership
Ledger `SPOOL <https://github.com/ascribe/spool>`_ and part of the development
stack of `ascribe.io <https://www.ascribe.io/>`_.

"""
import io
import os
import re

from setuptools import setup


def read(*names, **kwargs):
    with io.open(
        os.path.join(os.path.dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8')
    ) as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(
        r'^__version__ = [\'"]([^\'"]*)[\'"]', version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')


install_requires = [
    'pybitcointools==1.1.15',
    'pycoin>=0.70',
    'requests>=2.7.0',
    'transactions>=0.1.0',
]

dependency_links = [
    'git+https://github.com/sbellem/python-bitcoinrpc.git@setup#egg=python_bitcoinrpc-0.3.1',
]

tests_require = [
    'coverage',
    'pep8',
    'pyflakes',
    'pylint',
    'pytest',
    'pytest-cov',
    'python-bitcoinrpc>=0.3.1',
    'pytz',
]

dev_require = [
    'ipdb',
    'ipython',
]

docs_require = [
    'Sphinx>=1.3.5',
    'sphinx-autobuild',
    'sphinxcontrib-napoleon>=0.4.4',
    'sphinx_rtd_theme',
]


setup(
    name='pyspool',
    version=find_version('spool', '__init__.py'),
    url='https://github.com/ascribe/pyspool',
    license='Apache Software License',
    author='pyspool contributors',
    author_email='devel@ascribe.io',
    packages=['spool'],
    description='pyspool: Reference implementation of the SPOOL protocol',
    long_description=__doc__,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2 :: Only'
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development',
    ],
    install_requires=install_requires,
    dependency_links=dependency_links,
    setup_requires=['pytest-runner'],
    tests_require=tests_require,
    extras_require={
        'test': tests_require,
        'dev':  dev_require + tests_require + docs_require,
        'docs':  docs_require,
    },
)
