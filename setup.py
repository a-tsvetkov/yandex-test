#!/usr/bin/env python
from setuptools import setup, find_packages


setup(
    name='Logalyzer',
    version='0.1',
    description='Log analyzer for yandex job interview',
    author='Alex Tsvetkov',
    author_email='sickuenser@gmail.com',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    entry_points={
        'console_scripts': [
            'logalyzer = logalyzer.run:main'
        ]
    }
)
