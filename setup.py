#!/usr/bin/env python

PROJECT = 'astrotweet'

# Change docs/sphinx/conf.py too!
VERSION = '0.0.1'

# Bootstrap installation of Distribute
import distribute_setup
distribute_setup.use_setuptools()

from setuptools import setup, find_packages

try:
    long_description = open('README.rst', 'rt').read()
except IOError:
    long_description = ''

setup(
    name=PROJECT,
    version=VERSION,

    description='Work with the AstroBetter index of tweeting astronomers',
    long_description=long_description,

    author='Jonathan Sick',
    author_email='jonathansick@mac.com',

    url='https://github.com/jonathansick/astrotweet',

    classifiers=['Development Status :: 3 - Alpha',
                 'Programming Language :: Python',
                 'Programming Language :: Python :: 2',
                 'Programming Language :: Python :: 2.7',
                 'Intended Audience :: Developers',
                 'Environment :: Console',
                 ],

    platforms=['Any'],

    scripts=[],

    provides=[],
    install_requires=['distribute', 'cliff', 'twitter', 'requests', 'pymongo',
        'networkx'],

    namespace_packages=[],
    packages=find_packages(),
    include_package_data=True,

    entry_points={
        'console_scripts': [
            'astrotweet = astrotweet.main:main'
            ],
        'astrotweet.commands': [
            'summary = astrotweet.summary:SummaryTable',
            'build = astrotweet.mongobuild:MongoBuilder',
            ],
        },

    zip_safe=False,
    )
