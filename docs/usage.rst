Using yawd-admin
================

.. _setup:

Set up
++++++

To use the yawd-admin website you first need to include yawdadmin in
your ``INSTALLED_APPS`` setting. You also not need to include
`django.contrib.admin` in ``INSTALLED_APPS`` and place
it **after** `yawdadmin` for yawd-admin to work properly. In `settings.py`:

.. code-block:: python

	INSTALLED_APPS = (
		...
		'yawdadmin',
		'django.contrib.admin',
		...
	)

yawd-admin uses the :class:`yawdadmin.middleware.PopupMiddleware` middleware
to replace the  standard django admin popups with fancybox. Make sure the
middleware is enabled in your ``MIDDLEWARE_CLASSES`` setting. In `settings.py`:

.. code-block:: python

	MIDDLEWARE_CLASSES = (
		...
		'yawdadmin.middleware.PopupMiddleware',
		...
	)

Finally, the `django.core.context_processors.request` context
processor must also be enabled:

.. code-block:: python

	TEMPLATE_CONTEXT_PROCESSORS = (
		...
		"django.core.context_processors.request",
		...
	)

.. _register-urls:

Registering the yawd-admin urls
+++++++++++++++++++++++++++++++

To register the admin site views, use the following (inside your `urls.py`):

.. code-block:: python

	from yawdadmin import admin_site

	patterns = (''
		url(r'^admin/', include(admin_site.urls)),
		...
	)

You **do not** need to register the django admin urls as well, the
yawd ``admin_site`` extends the original admin class.
	
.. _auto-discover:

ModelAdmin registration and auto-discovery
++++++++++++++++++++++++++++++++++++++++++

Normally, to register your normal ModelAdmin class with yawd-admin you
should use ``yawdadmin.admin_site`` instead of the original
``django.contrib.admin.site`` instance (in `admin.py`):

.. code-block:: python

	from django.contrib import admin
	from models import MyModel

	class MyModelAdmin(admin.ModelAdmin):
		pass

	from yawdadmin import admin_site
	#you can use this instead of admin.site.register():
	admin_site.register(MyModel, MyModelAdmin)

However, many applications might have registered their `ModelAdmin`
classes with the default django admin site. As you can see from the
above snippet yawd-admin uses the `ModelAdmin` class as well, therefore
you can easily add all standard registrations to the yawd-admin website.
To do so, use the standard `admin.autodiscover()` method and then update
the yawd-admin registry as follows (in `urls.py`):

.. code-block:: python

	from django.contrib import admin
	from yawdadmin import admin_site

	admin.autodiscover()
	admin_site._registry.update(admin.site._registry)

.. _custom-user-models:

Integration with Custom User Models
+++++++++++++++++++++++++++++++++++

yawdadmin comes with a new admin view to allow staff users edit their own
account information (username,  first name, last name and email). This view
uses a ModelForm of the standard ``django.contrib.auth.models.User`` model.

If your projects makes use of the
`new django 1.5 custom user functionality <https://docs.djangoproject.com/en/dev/topics/auth/customizing/#auth-custom-user>`_
you can set the ``ADMIN_USER_MODELFORM`` yawd-admin setting to override the
ModelForm used by the view (in settings.py):

.. code-block:: python

	ADMIN_USER_MODELFORM = 'myapp.module.MyModelForm'

Note that the setting value can be a string or Class. A string is normally
preferred to avoid import errors during environment initialization.


.. settings:

Settings
++++++++

ADMIN_DISABLE_APP_INDEX
***********************

With yawd-admin you can optionaly disable the app index view (the one that lists an application's 
models). Doing so will raise "Page Not Found" (404) errors when accessing the application urls and
will also hide all corresponding links from breadcrumbs.

.. code-block:: python

	ADMIN_DISABLE_APP_INDEX = True 


ADMIN_GOOGLE_ANALYTICS
**********************

A dictionary holding configuration of the connected google analytics account. Please see
:ref:`google-analytics`.


ADMIN_SITE_NAME / ADMIN_SITE_DESCRIPTION
****************************************

You can change the admin site name and add a description to the login page
by adding a couple attributes to your settings:

.. code-block:: python
	
	ADMIN_SITE_NAME = 'My Admin Site'
	ADMIN_SITE_DESCRIPTION = 'This is a private site.  Please don\'t hack me'


If you don't want a description at all just null the attribute:

.. code-block:: python

	ADMIN_SITE_DESCRIPTION = None


ADMIN_SITE_LOGO_HTML
********************

To set a logo that will show up in the right side of the header:

.. code-block:: python

	ADMIN_SITE_LOGO_HTML = '<div id="myproject-logo hidden-phone">Logo</div>'


ADMIN_JS_CATALOG
****************

Additional javascript translation messages for use in the admin interface. Please see
:ref:`message-translations`.


ADMIN_USER_MODELFORM
********************

If you implement a custom user model (django 1.5 and above) you can override the ModelForm that
yawd-admin uses to allow staff users edit their account data. For more info please see
:ref:`custom-user-models`.

.. code-block:: python

	ADMIN_USER_MODELFORM = 'myapp.module.MyModelForm'
