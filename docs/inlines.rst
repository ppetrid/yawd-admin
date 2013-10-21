.. _admin-inlines:


Inlines
=======

Admin inline customizations
+++++++++++++++++++++++++++

Collapsing inlines
------------------

With yawd-admin you can collapse your inlines, like you do with
your fieldsets. Collapsing an admin inline is easy and works for
both stacked and tabular inlines:

.. code-block:: python

	class MyStackedInline(admin.StackedInline):
		...
		collapse = True

	class MyTabularInline(admin.TabularInline):
		...
		collapse = True

Inline description
------------------

When setting a model's fieldsets you can provide a ``description`` key to
specify a text that will be displayed under the fieldset header. Now you can
achieve the same effect with your inlines using the ``description`` member
in your Inline class:

.. code-block:: python

	class MyStackedInline(admin.StackedInline):
		...
		description = 'My inline description text'



Modal inlines
-------------

.. image:: contacts-email-addresses.png
	:align: left

Another nice option is the inline modal functionality. It can
be really useful when you have a lot of fields in your inline model. Add
``modal=True`` to the ``StackedInline`` class and your inline form will
open in a popup-style modal window:

.. code-block:: python

	class MyStackedInline(admin.StackedInline):
		...
		modal = True

This does not work with tabular inlines

.. image:: contacts-email-address.png
	:align: center


New inline types
++++++++++++++++

In addition to the stacked and tabular inlines, yawd-admin implements a couple of
new inline types.


Popup/Ajax inlines
------------------

This inline loads the inline form using ajax. It comes in handy when you want
to have inline forms *inside* an inline, or you jusst want a better-looking
inline form.

Say we want to implement an image gallery where each image should have variations.
An example models.py could look like this:

.. code-block:: python

	class Gallery(models.Model):
		title = models.CharField(max_length=100, required=True)

	class GalleryImage(models.Model):
		gallery = models.ForeignKey(Gallery)
		title = models.CharField(max_length=100)
	
	class GalleryImageVariation(models.Model)
		image = models.ForeignKey(GalleryImage)
		image_file = models.ImageField(upload_to=...)


We intend to use GalleryImageVariation as an inline for GalleryImage. In admin.py:

.. code-block:: python

	class GalleryAdmin(admin.ModelAdmin):
		...

	class GalleryImageVariationInline(models.StackedInline):
		model = GalleryImageVariation
		....

	class GalleryImageAdmin(admin.ModelAdmin):
		inlines = (GalleryImageVariationInline,)
		...
	
	admin_site.register(Gallery, GalleryAdmin)
	admin_site.register(GalleryImage, GalleryImageAdmin)
		

Now what if we wanted images to be editable through the Gallery admin page?
We could use a StackedInline or a Tabular inline for the GalleryImage model
but still all ImageVariations would be editable only through the GalleryImage's own change page.
To solve this we can use the ``PopupInline``, as follows:

.. code-block:: python

	from yawdadmin.admin import PopupInline, PopupModelAdmin
 
	class GalleryImageInline(PopupInline):
		model = GalleryImage
		...

	class GalleryAdmin(admin.ModelAdmin):
		inlines = (GalleryImageInline,)
		...

	class GalleryImageVariationInline(models.StackedInline):
		model = GalleryImageVariation
		....

	#We extend PopupModelAdmin instead of the original ModelAdmin.
	#This adds a couple of extra views to the GalleryImageAdmin
	#that allow managing the GaleryImage through ajax.
	#We also need to explicitly set the linked inline class
	#that will use the ajax functionality
	class GalleryImageAdmin(PopupModelAdmin):
		inlines = (GalleryImageVariationInline,)
		linked_inline = GalleryImageInline
		...
	
	admin_site.register(Gallery, GalleryAdmin)
	admin_site.register(GalleryImage, GalleryImageAdmin)
	
The above code will allow adding/editing images directly through the
gallery change page. Each time you choose to edit/add a gallery image, a modal
form will open; this form actually is the original GalleryImageAdmin form, including
all of its fieldsets, inlines etc.

Popup inlines can also be sortable. This means you can change their order using drag & drop:

.. code-block:: python

	class GalleryImage(models.Model):
		...
		ordering_field = models.IntegerField(..)

	class GalleryImageInline(PopupInline):
		model = GalleryImage
		sortable = False
		#the default value for the following property is 'order'.
		sortable_order_field = 'ordering_field'
		...


If you want to allow editing gallery images only through the popup inline you can use
the `popup_only` attribute:

.. code-block:: python

	
	class GalleryImageAdmin(PopupModelAdmin):
		inlines = (GalleryImageVariationInline,)
		linked_inline = GalleryImageInline
		popup_only = True
		....

	admin_site.register(GalleryImage, GalleryImageAdmin)

The above will raise ``Http404`` errors when accessing the standard add/change views of
the ``GalleryImage`` model. However, it will not make the equivalent links
disappear from the admin homepage or the app index page etc. To do so you must override
the equivalent templates. For the top-bar navigation you can use the :ref:`top-bar-exclude`
functionality.

.. note::

	Ajax/Popup inlines are **only** displayed in the `change` form and not the `add` form
	of an object, since they require the parent object to be already saved in the database.  


One-to-one inlines
------------------

If you have one-to-one relations, you might want to use the ``OneToOneInline`` class to
make the add/change page look like that of a single model.

For example, say you're developing an e-shop selling books. In your admin.py:

.. code-block:: python

	from yawdadmin.admin import OneToOneInline
	
	class BookInlineAdmin(OneToOneIneline):
		model = Book
	
	class ProductAdmin(admin.ModelAdmin):
		inlines = (BookInline,)
		....

	admin_site.register(Product, ProductAdmin)

That way the ``Product`` admin pages will look like a single form is being used.

