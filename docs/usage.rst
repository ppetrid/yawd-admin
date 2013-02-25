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
	
.. register-urls:

Register the yawd-admin urls
++++++++++++++++++++++++++++
    
To register the admin site views, use the following (inside your `urls.py`):

.. code-block:: python

	from yawdadmin import admin_site
	
	patterns = (''
		url(r'^admin', include(admin_site.urls)),
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
	
.. _top-bar:
	
Top-bar navigation
++++++++++++++++++

yawd-admin provides a top navigation bar. If you wish, you can register
an application's admin models along with an accompanying image to the 
top-bar as follows:

.. code-block:: python

	from yawdadmin import admin_site
	admin_site.register_top_menu_item('sites', icon_class="icon-th")

The ``icon_class`` argument can be any icon from the ones that ship
with bootstrap, found `here <http://twitter.github.com/bootstrap/base-css.html#icons>`_.

The above snippet will register the `django.contrib.admin.sites` application to
the top bar. Note however that if the application you try to register
is not yet registered with the admin website, an Exception will be raised.
Therefore, a safe place to put this code is in your `urls.py module`, right
after the :ref:`auto-discovery <auto-discover>` code. If you want to register the current 
application, you could use the `admin.py` module and place the code right 
after the `ModelAdmin` registrations (as in the :ref:`demo project <demo-project>`).

.. image:: admin-top-bar.png

A screenshot of the top-bar navigation from the demo project. Note that the
order in which `ModelAdmin` classes are presented in the drop-down box
is not alphabetical and that there is also a separator line between 
the `Expenses` and `Invoices` items. yawd-admin provides two custom 
`ModelAdmin` attributes to achieve this behavior: 
``order`` and ``separator``. You can use them like this:

.. code-block:: python

	class MyCategoryAdmin(admin.ModelAdmin)
		... #bla bla..
		order = 2

	class MyPageAdmin(admin.ModelAdmin)
		... #bla bla..
		order = 1
		
	class MyThirdAdmin(admin.ModelAdmin)
		... #bla bla..
		order = 3
		separator = True

The above will place `MyPageAdmin` before `MyCategoryAdmin` and 
`MyThirdAdmin` will come last. A separator line will also be drawed
**before** the `MyThirdAdmin` item.

If you do not set a custom `ModelAdmin` order, yawd-admin will use the
standard alphabetical order for your models.

You can exclude a certain model from the top-bar navigation. To do so
set the ``exclude_from_top_menu`` attribute to True:

.. code-block:: python

	class MyExcludedAdmin(admin.ModelAdmin)
		... #bla bla..
		exclude_from_top_menu = True

Admin db options
++++++++++++++++

You can register sets of custom options that editable from the admin
interface. 

.. image:: admin-options.png

Each set of options is defined by extending the 
:class:`yawdadmin.admin_options.OptionSetAdmin` class:

.. code-block:: python
	
	class CustomOptions(OptionSetAdmin):
		optionset_label = 'custom-options'
		verbose_name = 'Custom Options'
    
		option_1 = SiteOption(field=forms.CharField(
			widget=forms.Textarea(
				attrs = {'class' : 'textarea-medium'}
			),
			required=False,
			help_text='A fancy custom text area option.',
		))
    
		option_2 = SiteOption(field=forms.CharField(
			help_text='The second awesome option. This one is required!',
		))
    
The ``optionset_label`` attribute is the equivalent of the ``app_label``
for models. By defining a ``verbose_name`` you can explicitly set how
you want this option-set label to be displayed.

Each option is implemented as a member of the ``OptionSetAdmin`` sub-class,
exactly like you would do in a database model. The options must be of
the :class:`yawdadmin.admin_options.SiteOption` type. The ``field`` 
argument of the `SiteOption` constructor can refer to any standard django
form field class instance. In the above example, `option_1` will be a 
text area and `option_2` a text input.

.. note:: 

	a `SiteOption` initialization can accept a ``lang_dependant`` boolean
	keyword argument as well. Set this to ``True`` if you use yawd-admin
	along with `yawd-translations <http://yawd.eu/open-source-projects/yawd-translations/>`_
	and you need multilingual options:
	
	.. image:: multilingual-options.png
	
After defining your custom ``OptionSetAdmin`` class you must register it 
with the yawd-admin website:

.. code-block:: python

	#register the OptionSetAdmin to the admin site
	#almost like we would do for a ModelAdmin
	admin_site.register_options(CustomOptions)

Retrieving option values
------------------------

To retrieve a single option you can use the ``get_option()`` method:

.. code-block:: python

	from yawdadmin.utils import get_option
	option = get_option('custom-options', 'option_1')
	
	if option == 'whatever value':
		#do your stuff..
	
... where the first argument of the method is the `optionset_label` 
and the second is the option name.

If you want to retrieve all options of a single option-set at once
use the ``get_options()`` method (if you need access to more than one 
options this is preferred since it will hit the database only once):

.. code-block:: python

	from yawdadmin.utils import get_options
	options = get_options('custom-options')
	
	if options['option_1'] == 'whatever value':
		#do your stuff
	
...or in the template:
 
.. code-block:: django
 
 	<p><span>Option 1 value:</span> {{options.option_1}}</p>
 	
.. _google-analytics:

Integration with Google Analytics
+++++++++++++++++++++++++++++++++
 
To access your google analytics reports through the yawd-admin
index page you need to first create a new google API application 
by performing the following steps:

* Visit the Google APIs Console (https://code.google.com/apis/console)
* Sign-in and create a project or use an existing project.
* In the Services pane (https://code.google.com/apis/console#:services) activate Analytics API for your project. If prompted, read and accept the terms of service.
* Go to the API Access pane (https://code.google.com/apis/console/#:access):
* Click Create an OAuth 2.0 client ID:

	* Fill out the Branding Information fields and click Next.
	* In Client ID Settings, set Application type to 'Web application'.
	* In the **Your site or hostname** section click 'more options'. 
		
		* The **Authorized redirect URIs** field must be set to ``http://localhost:8000/admin/oauth2callback``. Replace `localhost:8000` with a domain if you are on a production system. The '/admin/' part of the URL refers to the :ref:`prefix <register-urls>` you used to register the admin site with.
		* The **Authorized JavaScript Origins** field must be set to ``http://localhost:8000/`` (or the domain root if you are on a production system).
		
	* Click Create client ID

Keep a node of the generated `Client ID` and `Client secret` as we will
use them later on. 

Go into your project source files and create a new file named 
`client_secrets.json`. The file contents should look like this::

	{
	  "web": {
	    "client_id": "[[INSERT CLIENT ID HERE]]",
	    "client_secret": "[[INSERT CLIENT SECRET HERE]]",
	    "redirect_uris": [],
	    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
	    "token_uri": "https://accounts.google.com/o/oauth2/token" 
	  }
	}
	
Replace ``[[INSERT CLIENT ID HERE]]`` and ``[[INSERT CLIENT SECRET HERE]]``
with the actual `Client ID` and `Client secret` you created in the previous
step.

Now all we need to do is enable the google analytics in the project
settings module (`settings.py`):

.. code-block:: python

	ADMIN_GOOGLE_ANALYTICS = {
		'client_secrets' : '/absolute/path/to/client_secrets.json',
		'token_file_name' : '/absolute/path/to/analytics.dat'),
		'profile_id' : '12345678',
		'admin_root_url' : 'http://localhost:8000/admin/'
	}
	
The ``client_secrets`` key must hold the absolute path to the
the `client_secrets.json` file we created.

The ``token_file_name`` key must point to the absolute path of a file
where yawd-admin will store session keys and information returned from
the google API. You do not need to manually create this file, just make sure
the web server has write access to that path.

``profile_id`` refers to the ID of the google analytics account you want to
connect with yawd-admin. To find this ID login to your google analytics
account, click the 'Admin' link from the horizontal menu and select
the account you wish to connect.

.. image:: analytics-id.png

A screenshot of an analytics account showing the Profile ID.

The last setting, ``admin_root_url`` must be set to the root url of the
admin website.

Now restart the web server and visit the admin interface 
(e.g. http://localhost:8000/admin). 

.. image:: configure-google-analytics.png

Visit the 'Configure Google Analytics' page (image above) and click 
'Authenticate new account' to grant the application access to your 
google analytics data. Make sure the google account you link has access 
to the specified ``profile_id``.

Now yawd-admin has stored your data and you don't need
to go through the confirmation process again.

.. _admin-inlines:

Admin inlines
+++++++++++++

Collapsing inlines
------------------

With yawd-admin you can collapse your inlines, like you do with
your fieldsets. Collapsing an admin inline is easy and works for
both stacked and tabular inlines:

.. code-block:: python
	
	class MyStackedInline(admin.StackedInline):
		#bla bla
		collapse = True
		
	class MyTabularInline(admin.TabularInline):
		#bla bla
		collapse = True
		
Modal inlines
-------------

Another nice & new option is the inline modal functionality. It can
be really useful when you have a lot of fields in your inline model. Add
``modal=True`` to the ``StackedInline`` class and your inline form will
open in a popup-style modal window:

.. code-block:: python

	class MyStackedInline(admin.StackedInline):
		#bla bla
		modal = True 

This does not work with tabular inlines

Inline description
------------------

When setting a model's fieldsets you can provide a ``description`` key to
specify a text that will be displayed under the fieldset header. Now you can
achieve the same effect with your inlines using the ``description`` member
in your Inline class:

.. code-block:: python

	class MyStackedInline(admin.StackedInline):
		#bla bla
		description = 'My inline description text'

.. _other-templates:

Templates for popular django applications
+++++++++++++++++++++++++++++++++++++++++

yawd-admin comes with templates for the following popular django
applications (thanks `pahaz <https://github.com/pahaz>`_)::

* django-reversion
* django-mptt

Just remember to place yawd-admin above these applications in your
``settings.py`` file.
