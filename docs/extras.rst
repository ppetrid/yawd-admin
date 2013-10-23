Additional functionality
========================

.. _side-navigation:

Side navigation for change forms
++++++++++++++++++++++++++++++++

.. image:: yawd-admin-affix.png
	:align: center

You can optionally enable a left menu navigation for your change form pages
on any model. This will automatically list and track all fieldsets and
inlines set in the ModelAdmin:

.. code-block:: python

	class MyModelAdmin(admin.ModelAdmin):
		..other stuff..
		fieldsets = (...)
		inlines = (...)
		affix=True

.. _reorder-changelist:

Sortable changelists
++++++++++++++++++++

.. image:: sortable-changelists.png
	:align: center

You can enable a "sorting mode" in the changelist view for
orderable objects by subklassing ``yawdadmin.admin.SortableModelAdmin``
instead of ``admin.ModelAdmin``:

.. code-block:: python

	#Model admin class
	class CategoryAdmin(SortableModelAdmin):
		...
		...
	
	admin_site.register(Category, CategoryAdmin)

By default yawdadmin expects the ordering model field to be named "order"
(it must be an `IntegerField`). If the name is different you need to set
the  `"sorting_order_field"` attribute:

.. code-block:: python

	#model definition
	class Category(models.Model):
		...
		weird_order_field_name = models.IntegerField(default=0)

	#Model admin class
	class CategoryAdmin(SortableModelAdmin):
		sortable_order_field = 'weird_order_field_name'
		...

If you use `django-mptt <https://github.com/django-mptt/django-mptt>`_ for
nested categories, you can enable nested ordering like so (see screenshot
above):

.. code-block:: python

	#Model admin class
	class CategoryAdmin(SortableModelAdmin):
		sortable_mptt = True
		...

The sorting mechanism assumes items are orderd by the ordering field
in the default queryset. If that's not true, you should
override the `"sortables_ordered"` method to provide a proper default
ordering:

.. code-block:: python

	#Model admin class
	class CategoryAdmin(SortableModelAdmin):
		def sortables_ordered(self, queryset):
			return queryset.order_by("order")

.. _message-translations:

Javascript message translations
+++++++++++++++++++++++++++++++

If you use :ref:`custom templates <overriding-templates>` and want to add
multilingual javascript messages as described in `the django documentation 
<https://docs.djangoproject.com/en/dev/topics/i18n/translation/#module-django.views.i18n>`_,
you can use the `ADMIN_JS_CATALOG` setting:

.. code-block:: python

	ADMIN_JS_CATALOG = ['your.app.package', 'your.app.package.2']

Make sure you have compiled the translated javascript messages (`djangojs`
namespace) for all listed applications, so they're included in the admin
catalog view.

Model icons
+++++++++++

You can set an accompanying icon class for each of your models in the
``ModelAdmin`` class.

.. code-block:: python

	class MyModelAdmin(admin.ModelAdmin):
		....
		title_icon = 'icon-group'

yawd-admin will display this icon in various places (e.g drop-down menus,
change list pages, change form pages) in an effort to make your UI more
eye-appealing.

The icon classes you can choose from are listed
`here <http://fortawesome.github.com/Font-Awesome/>`_. yawd-admin uses the
font-awesome bootstrap icons instead of the original ones. Therefore
you can apply any CSS rule to customize the look & feel of your icons.
