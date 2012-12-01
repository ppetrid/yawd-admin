#!/usr/bin/env python
from setuptools import setup, find_packages
import translations

setup(
      name='yawd-admin',
      url='http://yawd.eu/open-source-projects/yawd-admin/',
      version = yawdadmin.__version__,
      description='An administration website for Django',
      author='yawd',
      author_email='info@yawd.eu',
      packages=find_packages(),
      license='BSD',
      classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries'
        ],
      include_package_data = True,
      install_requires = [
        "django >= 1.4",
        "oauth2client"
        ],
)