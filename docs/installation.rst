Installing yawd-admin
=====================

.. _prerequisites:

Prerequisites
+++++++++++++

yawd-admin requires that the `oauth2client` and `httplib2` libraries
are installed in your python environment::
	
	$ pip install oauth2client
	$ pip install httplib2

If you plan to use the yawd-admin google analytics functionality, 
the `google-api-python-client` must also be installed::

	$ pip install google-api-python-client
	
To see which Django versions work with yawd-admin please see
:ref:`django-versions`.

.. _installation:

Application installation
++++++++++++++++++++++++

Install yawd-admin either from `pypi <http://pypi.python.org/pypi/yawd-admin/>`_
or the `github repository <https://github.com/yawd/yawd-admin/>`_::

	$ pip install yawd-admin
   
...or::

	$ git clone https://github.com/yawd/yawd-admin
	$ cd yawd-admin
	$ python setup.py install
	
Either ways all :ref:`prerequisites` (**except** from `google-api-python-client`)
will be automatically installed.

.. note::

	Since yawd-admin is actively being developed the github version is
	generally preferred (especially if you use the latest django); the
	``master`` branch always contains all latest updates & fixes and is
	generally considered stable.
	
.. _demo-project:

Install the demo project
++++++++++++++++++++++++

In the demo project you will find a full example of yawd-admin (only the
google analytics functionality is not demonstrated).

Create a new environment named *yawdadmin* and activate it::

   $ virtualenv /www/yawdadmin
   $ source /www/yawdadmin/bin/activate
   
Download and install yawd-admin::

   $ git clone https://github.com/yawd/yawd-admin
   $ cd yawd-admin
   $ python setup.py install
   
At this point, yawd-admin will be in your ``PYTHONPATH``. Now initialize 
the example project::
   
   $ cd example_project
   $ python manage.py syncdb
   
When promted, create an admin account. Finally, start the web server::

   $ python manage.py runserver
   
...and visit *http://localhost:8000/*
to see the admin interface and experiment with its features.

.. note::
	The demo admin URLs are registered in the root url and no
	prefix (e.g. '/admin/') is needed.
	
Explore the demo project source code and read the comments, to better
understand how to use yawd-admin.

Once you are done, you can deactivate the virtual environment::

   $ deactivate yawdadmin


Live demo
+++++++++

Alternatively, you can visit the live demo at 
`http://yawd-admin.yawd.eu/ <http://yawd.eu/open-source-projects/yawd-admin/>`_.
Use demo / demo as username & passowrd.

.. note::

	The live demo uses yawd-admin v0.7.0.
