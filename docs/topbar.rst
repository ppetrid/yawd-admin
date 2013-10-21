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

.. _top-bar-exclude:

Model exclusion
***************

You can exclude a certain model from the top-bar navigation. To do so
set the ``exclude_from_top_menu`` attribute to True:

.. code-block:: python

	class MyExcludedAdmin(admin.ModelAdmin)
		... #bla bla..
		exclude_from_top_menu = True

Custom top-bar menus
--------------------

In addition to the app/model-driven top bar menus, you can also create
custom menus. To do that you should use the ``register_top_menu_item``
method, specifying child menu items like this:

.. code-block:: python

	from yawdadmin import admin_site
	admin_site.register_top_menu_item('Custom menu', icon_class="icon-th",
		children=[{'name': 'Custom view 1', 'admin_url': reverse_lazy('custom-url-view'), 'order': 1, 'title_icon': 'icon-hand-left' },
		          {'name': 'Custom view 2', 'admin_url': reverse_lazy('custom-url-view-2'), 'order': 2, separator: True, 'title_icon': 'icon-hand-right' }],
	perms=perms_func)


The ``children`` keyword argument must be a list holding the actual sub-menu items.
Each item in this list must be a dictionary with the following keys:

* *name*: The menu item name. **Required**
* *admin_url*: The menu item URL. **Required**
* *title_icon*: The class of the leading icon. Optional.
* *order*: The item's order among its siblings. Optional.
* *separator*: If a separator should be placed *before* this item (just like with model-driven menus). Optional.

The ``perms`` keyword argument is **optional**. If you wish to control the
permissions on each menu item, you can specify a function that accepts
both the current request and a menu item as arguments and returns either True -when the user is allowed
to view the item-, or False. Example implementation:

.. code-block:: python

	def perms_func(request, item):
		if not request.user.is_superuser and item['admin_url'].startswith('/private'):
			return False
		return True