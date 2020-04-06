next to the inner yourapplication folder with the following contents:

from setuptools import setup

setup(
    name='PM_uT',
    packages=['Application'],
    include_package_data=True,
    install_requires=[
        'flask',
    ],
)