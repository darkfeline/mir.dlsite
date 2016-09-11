#!/usr/bin/env python3

from setuptools import setup

setup(
    name='mir.dlsite',
    version='0.1.0',
    description='API for DLSite',
    long_description='',
    keywords='',
    url='https://github.com/darkfeline/mir.dlsite',
    author='Allen Li',
    author_email='darkfeline@felesatra.moe',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.5',
    ],
    install_requires=[
        'beautifulsoup4',
        'lxml',
    ],

    packages=['mir'],
)
