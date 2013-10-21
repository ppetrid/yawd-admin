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