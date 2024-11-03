import os
import sys
from setuptools import setup, find_packages

setup(
    name="Enigma",
    version="3.0",
    description="A Discord music recommendation bot",
    author="Group 87(Kevin Dai, Gwen Mason, Yi Zhang)",
    author_email="yzhan274@ncsu.edu",
    zip_safe=False,
    classifiers=(
        "Development Status :: Development",
        "Intended Audience :: Engineers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
    ),
    tests_require=["pytest"],
    exclude_package_data={"": [".gitignore"], "images": ["*.xcf", "*.blend"]},
)
