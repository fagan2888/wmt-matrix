#!/usr/bin/env python3

"""
A setuptools based setup module.

See:
- https://packaging.python.org/en/latest/distributing.html
- https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup
import re
import os

def get_version():
    VERSION_RE = re.compile(r'''VERSION\s+=\s+['"]([0-9.]+)['"]''')
    init = open(os.path.join(os.path.dirname(__file__), 'wmt.py')).read()
    return VERSION_RE.search(init).group(1)

setup(
    name = 'wmt',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version = get_version(),

    description = '',
    long_description = '',

    # The project's main homepage.
    url = 'https://github.com/mjpost/wmt',

    author = 'Matt Post',
    author_email='post@cs.jhu.edu',

    license = 'Apache License 2.0',

    python_requires = '>=3',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Text Processing',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: Apache Software License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3 :: Only',
    ],

    # What does your project relate to?
    keywords = ['machine translation, evaluation, NLP, natural language processing, computational linguistics'],

    # Alternatively, if you want to distribute just a my_module.py, uncomment this:
    py_modules = ["wmt"],

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires = ['typing', 'bs4'],

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    extras_require = {},

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            'wmt = wmt:main',
        ],
    },
)
