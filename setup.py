#!/usr/bin/env python3
"""Setup for oyinsteon module."""
from setuptools import setup, find_packages


def readme():
    """Return README file as a string."""
    with open('README.rst', 'r') as f:
        return f.read()


setup(
    name='pyinsteon',
    version='0.1.0a2',
    author='The pyinsteon Development Team',
    author_email='pyinsteon@harrisnj.net',
    url='https://github.com/pyinsteon/pyinsteon',
    license="MIT License",
    packages=find_packages(exclude=['tests', 'tests.*', 'topics',
                                    'docs', 'samples']),
    scripts=[],
    description='Python API for controlling Insteon devices',
    long_description=readme(),
    include_package_data=True,
    zip_safe=True,
    install_requires=[
        'pyserial',
        'pyserial-asyncio',
        'aiohttp',
        'pypubsub'
    ],
    entry_points={
        'console_scripts': ['insteon_monitor = pyinsteon.tools:monitor',
                            'insteon_tools = '
                            'pyinsteon.tools:tools']
    }
)
