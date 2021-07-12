#!/usr/bin/env python3
"""Setup for oyinsteon module."""
from setuptools import find_packages, setup


def readme():
    """Return README file as a string."""
    with open("DESCRIPTION.rst", "r") as readme_file:
        return readme_file.read()


setup(
    name="pyinsteon",
    version="1.0.12",
    author="The pyinsteon Development Team",
    author_email="pyinsteon@harrisnj.net",
    url="https://github.com/pyinsteon/pyinsteon",
    license="MIT License",
    packages=find_packages(exclude=["tests", "tests.*", "topics", "docs", "samples"]),
    scripts=[],
    description="Python API for controlling Insteon devices",
    long_description=readme(),
    include_package_data=True,
    zip_safe=True,
    install_requires=[
        "pyserial",
        "pyserial-asyncio>=0.5",
        "aiohttp",
        "pypubsub",
        "aiofiles",
        "pyyaml",
    ],
    entry_points={"console_scripts": ["insteon_tools = pyinsteon.tools:tools"]},
)
