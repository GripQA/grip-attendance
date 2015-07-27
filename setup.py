#!/usr/bin/env python
# coding=utf8

import os
from distutils.core import setup
import sys


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name = 'grip-attendance',
    py_modules = ['grip-attendance'],
    version = '0.01',
    description = 'Program to generate an attendance report for an event',
    long_description=read('README.rst'),
    author = 'Dean Stevens, GripQA',
    author_email = 'support@grip.qa',
    url = 'https://github.com/GripQA/grip-attendance', # URL to the github repo
    download_url = 'https://github.com/GripQA/grip-attendance/tarball/0.01',
    keywords = ['attendance',
                'webinar',
                'meetings',
                'registration',
                'attendee'
    ],
    classifiers = ['Programming Language :: Python',
                   'Programming Language :: Python :: 3.4',
                   'Operating System :: OS Independent',
                   'Development Status :: 3 - Alpha',
                   'Intended Audience :: End Users/Desktop',
                   'License :: OSI Approved :: Apache Software License',
                   'Natural Language :: English',
                   'Topic :: Office/Business',
                   'Topic :: Utilities',
                   
    ],
)
