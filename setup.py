# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

long_desc = '''
This package contains the sphinxcontrib-erlangdomain Sphinx extension.

This extension adds Erlang Domain to Sphinx.
It needs Sphinx 1.0 or newer.

Detail document: https://sphinxcontrib-erlangdomain.readthedocs.io/en/latest/
'''

requires = ['Sphinx>=1.0']

setup(
    name='sphinxcontrib-erlangdomain',
    version='0.2.1',
    url='https://github.com/hio/sphinx-erlangdomain',
    download_url='https://pypi.org/project/sphinxcontrib-erlangdomain/',
    project_urls={
        'Documentation': 'https://sphinxcontrib-erlangdomain.readthedocs.io/en/latest/',
        'Source': 'https://github.com/hio/sphinx-erlangdomain',
    },
    license='BSD',
    author='SHIBUKAWA Yoshiki',
    author_email='yoshiki@shibu.jp',
    maintainer='YAMASHINA Hio',
    maintainer_email='hio@hio.jp',
    description='Sphinx extension sphinxcontrib-erlangdomain',
    long_description=long_desc,
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Erlang',
        'Topic :: Documentation',
        'Topic :: Utilities',
    ],
    platforms='any',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requires,
    namespace_packages=['sphinxcontrib'],
)
