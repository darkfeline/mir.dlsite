#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name='dlsitelib',
    version='0.1.0',
    package_dir={'': 'src'},
    packages=find_packages('src'),

    author='Allen Li',
    author_email='darkfeline@felesatra.moe',
    description='DLSite library',
    license='GPLv3',
    url='',
)
