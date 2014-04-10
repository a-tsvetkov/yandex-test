#!/usr/bin/env python
from setuptools import setup, find_packages
from setuptools.extension import Extension
from Cython.Distutils import build_ext


setup(
    name='Logalyzer',
    version='0.1',
    description='Log analyzer for yandex job interview',
    install_requires=['cython'],
    author='Alex Tsvetkov',
    author_email='sickuenser@gmail.com',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    entry_points={
        'console_scripts': [
            'logalyzer = logalyzer.run:main'
        ]
    },
    cmdclass={'build_ext': build_ext},
    ext_modules=[
        Extension('logalyzer.analyzer', ["src/logalyzer/analyzer.pyx"]),
        Extension('logalyzer.requests', ["src/logalyzer/requests.pyx"]),
        Extension('logalyzer.stats', ["src/logalyzer/stats.pyx"]),
        Extension('logalyzer.utils', ["src/logalyzer/utils.pyx"])
    ]
)
