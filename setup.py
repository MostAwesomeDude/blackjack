#!/usr/bin/env python

from setuptools import setup

setup(
    name="blackjack",
    setup_requires=["vcversioner"],
    vcversioner={},
    py_modules=["blackjack"],
    author="Corbin Simpson",
    author_email="cds@corbinsimpson.com",
    description="Red-black trees",
    long_description=open("README.rst").read(),
    license="MIT/X11",
    url="http://github.com/MostAwesomeDude/blackjack",
)
