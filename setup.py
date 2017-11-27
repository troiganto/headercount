#!/usr/bin/env python3

from setuptools import setup, find_packages


setup(
    name='headercount',
    version='0.1',
    python_requires='>=3.4',
    packages=['headercount'],
    entry_points={
        'console_scripts': [
            'headercount = headercount.__main__:main',
            ]
        },
    zip_safe=True,
    author='Nico Madysa',
    author_email='uebertreiber@gmx.de',
    description='Count directly and indirectly included headers in a C/C++ project',
    license='',
    keywords='',
    url='https://github.com/troiganto/headercount',
)
