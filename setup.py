#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='yawd-admin',
    url='http://yawd.eu/open-source-projects/yawd-admin/',
    version='0.7.3',
    description='An administration website for Django',
    long_description=open('README.rst', 'rt').read(),
    author='yawd',
    author_email='info@yawd.eu',
    packages=find_packages(),
    license='BSD',
    classifiers=[
                'Development Status :: 4 - Beta',
                'Environment :: Web Environment',
                'Framework :: Django',
                'Intended Audience :: Developers',
                'License :: OSI Approved :: BSD License',
                'Operating System :: OS Independent',
                'Programming Language :: Python',
                'Topic :: Software Development :: Libraries'
    ],
    include_package_data=True,
    install_requires=[
                     "httplib2",
                     "django >=1.6, <1.9",
                     "oauth2client"
    ],
    zip_safe=False
)
