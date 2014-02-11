"""
Displaying data and gather feedback.
"""

from setuptools import setup

setup(
    name='tableau',
    version='1.0.0',
    long_description=__doc__,
    packages=['tableau'],
    include_package_data=True,
    zip_safe=False,
    install_requires=['Flask']
)
