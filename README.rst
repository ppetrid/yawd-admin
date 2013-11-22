yawd-admin, a django administration website
======================================================

yawd-admin now has a live demo at
`http://yawd-admin.yawd.eu/ <http://yawd-admin.yawd.eu/>`_.
Use demo / demo as username & passowrd.

.. image:: docs/yawd-admin-screenshot.png
	:align: center

`yawd-admin <http://yawd.eu/open-source-projects/yawd-admin/>`_ is an 
administration website for django. It extends the default django admin 
site and offers the following:

* A clean and beautiful bootstrap user interface
* Hand-written pure HTML5/CSS3 code with indented HTML output
* Responsive interface, optimized for mobile phones and tablets
* Register custom database settings (options) editable from the UI. You can use all **standard django form fields** for these settings
* Integration with google analytics for displaying statistics in the admin home page
* Register your applications to the top-bar navigation
* Refurbished original django admin widgets
* Mechanism for opening the original django admin popup windows with fancybox
* Seamless integration with `yawd-translations` for multilingual admin websites

.. note::

	yawd-admin v0.6.1 is the last version intended to work with
	Django 1.4. yawd-admin v.0.7.0 and on is developed under Django 1.5.x
	and does NOT work with older Django releases. For those still using
	Django 1.4, you can checkout the ``0.6.x`` branch or use the yawd-admin
	v0.6.1 pypi package. New features will not be backported to the ``0.6.x``
	branch. Since many of us run production systems tied to Django 1.4, both
	v0.6.1 and the latest documentation will be online on readthedocs.org. 

Usage and demo
==============

See the `yawd-admin documentation <http://yawd-admin.readthedocs.org/en/latest/>`_ 
for information on how to install the demo and use yawd-admin. There is also an
online version of the demo at `http://yawd-admin.yawd.eu/ <http://yawd.eu/open-source-projects/yawd-admin/>`_.
Just use *demo*/*demo* as username and password.

Screenshots
===========

Side navigation for change forms
++++++++++++++++++++++++++++++++

.. image:: docs/yawd-admin-affix.png
	:align: center

Sortable changelists
++++++++++++++++++++

.. image:: docs/sortable-changelists.png
	:align: center

Modal inlines
+++++++++++++

.. image:: docs/contacts-email-addresses.png
	:align: left
	
Admin db options
++++++++++++++++

.. image:: docs/admin-options-full.png
