from setuptools import setup

setup(
    name='backoffice',
    packages=['backoffice'],
    include_package_data=True,
    install_requires=[
        'flask',
    ],
)