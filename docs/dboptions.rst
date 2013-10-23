DB options
++++++++++

With yawd-admin you can register sets of custom options. These options are editable
through the admin interface and you can use them to let administrators fine-tune
the application.


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