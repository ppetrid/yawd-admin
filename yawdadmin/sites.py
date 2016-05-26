import httplib2
from functools import update_wrapper
from oauth2client.file import Storage
from django import VERSION as DJANGO_VERSION
from django.conf.urls import patterns, url
from django.conf import settings
from django.contrib.admin.sites import AdminSite
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse, NoReverseMatch
from django.http import Http404
from django.template.response import TemplateResponse
from django.utils import six
from django.utils.encoding import force_text
from django.utils.text import capfirst
from django.utils.translation import ugettext as _, get_language
from django.views.decorators.cache import never_cache
from conf import settings as ls
from models import AppOption
from views import AppOptionView, AnalyticsAuthView, AnalyticsConfigView, \
    AnalyticsConnectView, MyAccountView


_optionset_labels = {}


class YawdAdminDashboard(object):
    exclude = []

    def __init__(self, app_labels, admin_name):
        self.name = admin_name
        self.app_labels = {}
        for i in app_labels:
            if i not in self.exclude:
                self.app_labels[i] = app_labels[i].copy()

    def _app_dict_sets(self):
        for app_label in self.app_dict:
            if not 'linksets' in self.app_dict[app_label]:
                #sort models alphabetically
                if not 'models' in self.app_dict[app_label]:
                    self.app_dict[app_label]['models'] = []

                self.app_dict[app_label]['models'].sort(key=lambda x: x['name'])
                if not 'extras' in self.app_dict[app_label]:
                    self.app_dict[app_label]['sets'] = (('', self.\
                                    app_dict[app_label]['models']),)
                else:
                    self.app_dict[app_label]['sets'] = (('', self.\
                                    app_dict[app_label]['models'] + \
                                    self.app_dict[app_label]['extras']),)
            else:
                self.app_dict[app_label]['sets'] = []
                for set in self.app_dict[app_label]['linksets']:
                    models = []
                    for label in set[1]:
                        model = self._find_model(label, app_label)
                        if model:
                            models.append(model)
                    self.app_dict[app_label]['sets'].append((set[0], models))

            self.app_dict[app_label]['show'] = self._get_has_any_perms(self.app_dict[app_label])
    
    def _get_has_any_perms(self, data):
        for set in data['sets']:
            for m in set[1]:
                if ('perms' in m and m['perms']['change']) or \
                        ('url' in m and m['url']):
                    return True

    def _check_app_dict(self, app_label, has_module_perms):
        if not app_label in self.app_dict:
            self.app_dict[app_label] = {}
        if not 'has_module_perms' in self.app_dict[app_label]:
            self.app_dict[app_label]['has_module_perms'] = has_module_perms
        if not 'name' in self.app_dict[app_label]:
            self.app_dict[app_label]['name'] = app_label.title()
        if not 'app_url' in self.app_dict[app_label]:
            self.app_dict[app_label]['app_url'] = reverse('admin:app_list',
                                                          kwargs={'app_label': app_label},
                                                          current_app=self.name)
        if not 'models' in self.app_dict[app_label]:
            self.app_dict[app_label]['models'] = []

    def _find_model(self, label, app_label):
        if 'models' in self.app_dict[app_label]:
            for model in self.app_dict[app_label]['models']:
                if model['classname'] == label:
                    return model
        if 'extras' in self.app_dict[app_label]:
            for extra in self.app_dict[app_label]['extras']:
                if 'label' in extra and extra['label'] == label:
                    return extra       
 
    @classmethod
    def app_sorter(self, x):
        return x['name']

    def get_app_list(self, request, registry, label=''):
        #register the explicit app_labels
        if label:
            self.app_dict = {label: self.app_labels[label]} if label in self.app_labels else {}
        else:
            self.app_dict = self.app_labels
        user = request.user

        for model, model_admin in registry.items():
            app_label = model._meta.app_label
            if label and not label == app_label:
                continue

            has_module_perms = user.has_module_perms(app_label)

            if has_module_perms and not app_label in self.exclude:
                perms = model_admin.get_model_perms(request)
        
                # Check whether user has any perm for this module.
                # If so, add the module to the model_list.
                if True in perms.values():
                    info = (app_label, model._meta.module_name)
                    model_dict = {
                        'classname': model.__name__,
                        'name': capfirst(model._meta.verbose_name_plural),
                        'perms': perms,
                    }
                    if perms.get('change', False):
                        try:
                            model_dict['admin_url'] = reverse('admin:%s_%s_changelist' % info, current_app=self.name)
                        except NoReverseMatch:
                            pass
                    if perms.get('add', False):
                        try:
                            model_dict['add_url'] = reverse('admin:%s_%s_add' % info, current_app=self.name)
                        except NoReverseMatch:
                            pass
                    self._check_app_dict(app_label, has_module_perms)
                    if not 'exclude' in self.app_dict[app_label] or \
                        model_dict['classname'] not in self.app_dict[app_label]['exclude']:
                        self.app_dict[app_label]['models'].append(model_dict)

        self._app_dict_sets()

        if not label:
            # Sort the apps by the specified sorter - alphabetically by default.
            app_list = list(six.itervalues(self.app_dict))    
            app_list.sort(key=self.app_sorter)
            return app_list

        return self.app_dict[label]

    @property
    def show_app_label_link(self):
        return not getattr(settings, 'ADMIN_DISABLE_APP_INDEX', False)


class YawdAdminSite(AdminSite):
    top_menu_default_order = 3
    dashboard_class = YawdAdminDashboard

    def __init__(self, *args, **kwargs):
        super(YawdAdminSite, self).__init__(*args, **kwargs)
        self._top_menu = {}
        self._app_labels = {}

    def check_dependencies(self):
        """
        Override the default method to check that the 
        :class:`yawdadmin.middleware.PopupMiddleware` is installed
        and ``yawdadmin`` is found in the INSTALLED_APPS setting **before**
        ``django.contrib.admin``.
        """
        super(YawdAdminSite, self).check_dependencies()
        if not AppOption._meta.installed:  #@UndefinedVariable
            raise ImproperlyConfigured("Put 'yawdadmin' in your "
                                       "INSTALLED_APPS setting in order to "
                                       "use the yawd-admin application.")
        if settings.INSTALLED_APPS.index('yawdadmin') > settings.INSTALLED_APPS.index('django.contrib.admin'):
            raise ImproperlyConfigured("Put 'yawdadmin' before "
                                       "'django.contrib.admin' in your "
                                       "INSTALLED_APPS setting to use the "
                                       "yawd-admin application") 
        if not 'yawdadmin.middleware.PopupMiddleware' in settings.MIDDLEWARE_CLASSES and \
            DJANGO_VERSION[0]== 1 and DJANGO_VERSION[1] <= 5:
            raise ImproperlyConfigured("Put 'yawdadmin.middleware.PopupMiddleware' "
                                       "in your MIDDLEWARE_CLASSES setting "
                                       "in order to use the yawd-admin application.")

    def get_index_template(self):
        return self.index_template

    def get_urls(self):
        global _optionset_labels
        
        def wrap(view, cacheable=False):
            def wrapper(*args, **kwargs):
                return self.admin_view(view, cacheable)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        up = patterns('',
                      url(r'^configuration-options/(?P<optionset_label>%s)/$' % '|'.join(_optionset_labels.keys()), wrap(AppOptionView.as_view()), name='optionset-label-options'),
                      url(r'^oauth2callback/$', wrap(AnalyticsAuthView.as_view()), name='oauth2-callback'),
                      url(r'^google-analytics/$', wrap(AnalyticsConfigView.as_view()), name='analytics'),
                      url(r'^google-analytics/connect/$', wrap(AnalyticsConnectView.as_view()), name='analytics-connect'),
                      url(r'^my-account/$', wrap(MyAccountView.as_view()), name='my-account'),
            )

        up += super(YawdAdminSite, self).get_urls() 
        return up

    def register_app_label(self, app_label, app_dict={}):
        if not app_label in self._app_labels:
            self._app_labels[app_label] = app_dict

    def unregister_app_label(self, app_label):
        if app_label in self._app_labels:
            del self._app_labels[app_label]

    def register_top_menu_item(self, item, icon_class='', children={}, perms=None):
        """
        When no children are provided, the ``item`` is expected to be a
        valid application label.
        Otherwise, a custom menu can be constructed based on the children
        structure.
        The ``perms`` argument can be a function that will be called at
        runtime. Given the request and a model item as keyword arguments, 
        the function should return whether the item is to be displayed or
        not (``True`` or ``False``).
        """
        app_labels = []
        for model, model_admin in self._registry.iteritems():
            if not model._meta.app_label in app_labels:
                app_labels.append(model._meta.app_label)
        
        if isinstance(item, basestring) and item in app_labels:
            if not item in self._top_menu:
                self._top_menu[item] = icon_class
        elif item and children:
            for child in children:
                if not 'name' in child or not 'admin_url' in child:
                    raise Exception("Children must contain at least a 'name' and an 'admin_url'")
                if not perms:
                    child['show'] = True
                if not 'order' in child:
                    child['order'] = self.top_menu_default_order

            if not item in self._top_menu:
                self._top_menu[force_text(item)] = {'name': item,
                                        'icon': icon_class,
                                        'models': children}
                if perms:
                    #store the function reference
                    self._top_menu[item]['perms'] = perms
        else:
            raise Exception("Item has to be a valid app_label or children must be explicitly set.")

    def unregister_top_menu_item(self, item):
        if isinstance(item, basestring) and item in self._top_menu:
            del self._top_menu[item]
        else:
            raise Exception("Item is not registered in the top menu")

    def top_menu(self, request):
        user = request.user
        app_dict = {}

        for model, model_admin in self._registry.items():
            app_label = model._meta.app_label
            if app_label in self._top_menu and (not hasattr(model_admin, 'exclude_from_top_menu') or not model_admin.exclude_from_top_menu):
                has_module_perms = user.has_module_perms(app_label)

                if has_module_perms:
                    perms = model_admin.get_model_perms(request)
        
                    # Check whether user has any perm for this module.
                    # If so, add the module to the model_list.
                    if True in perms.values():
                        info = (app_label, model._meta.module_name)
                        model_dict = {
                            'name': capfirst(model._meta.verbose_name_plural),
                            'show': perms['change'],
                        }
                        if perms.get('change', False):
                            try:
                                model_dict['admin_url'] = reverse('admin:%s_%s_changelist' % info, current_app=self.name)
                            except NoReverseMatch:
                                pass
                        if perms.get('add', False):
                            try:
                                model_dict['add_url'] = reverse('admin:%s_%s_add' % info, current_app=self.name)
                            except NoReverseMatch:
                                pass

                        model_dict['order'] = model_admin.order if hasattr(model_admin, 'order') else self.top_menu_default_order
                        model_dict['separator'] = model_admin.separator if hasattr(model_admin, 'separator') else False
                        model_dict['title_icon'] = model_admin.title_icon if hasattr(model_admin, 'title_icon') else False

                        if app_label in app_dict:
                            app_dict[app_label]['models'].append(model_dict)
                        else:
                            app_dict[app_label] = {
                                'name': app_label.title(),
                                'icon': self._top_menu[app_label],
                                'app_url': reverse('admin:app_list', kwargs={'app_label': app_label}, current_app=self.name),
                                'has_module_perms': has_module_perms,
                                'models': [model_dict],
                            }

        app_list = app_dict.values()

        #register custom menus
        for app in self._top_menu.values():
            if isinstance(app, dict):
                for child in app['models']:
                    if not 'show' in child and 'perms' in app and hasattr(app['perms'], '__call__'):
                        child['show'] = app['perms'](request, child)
                app_list.append(app)

        app_list.sort(key=lambda x: x['name'])

        # Sort the models alphabetically within each app.
        for app in app_list:
            app['models'].sort(key=lambda x: x['order'])

        return app_list

    def register_options(self, optionset_admin):
        """
        Allows an application to register admin options like so::

            admin_site.register_options(OptionSetAdminClass)
        """
        global _optionset_labels
        if not optionset_admin.optionset_label in _optionset_labels:
            #Add admin optionset to the registry
            _optionset_labels[optionset_admin.optionset_label] = optionset_admin
            #Initialize options
            optionset_admin()

    def unregister_options(self, optionset_admin, delete_db_records=False):
        optionset_label = optionset_admin.optionset_label
        if optionset_label in _optionset_labels:
            del _optionset_labels[optionset_label]
            if delete_db_records:
                AppOption.objects.filter(optionset_label=optionset_label).delete()

    def get_option_admin_urls(self):
        """
        Return a list of key-value pairs, containing all available optionset urls 
        """
        global _optionset_labels

        if not hasattr(self, 'option_admin_urls'):
            option_urls = []
            for option in _optionset_labels:
                option_urls.append({ 'optionset_label' : _optionset_labels[option].verbose_name, 'url' : reverse('admin:optionset-label-options', kwargs={ 'optionset_label' : option }, current_app='admin')})
            self.option_admin_urls = option_urls

        return self.option_admin_urls

    def get_optionset_admin(self, optionset_label):
        """
        Returns the OptionSetAdmin class for this label
        """
        global _optionset_labels
        if optionset_label in _optionset_labels:
            return _optionset_labels[optionset_label]

    @never_cache
    def index(self, request, extra_context={}):
        """
        This index view implementation adds Google Analytics
        integration so that you can view important metrics 
        right from the administrator interface.
        """        
        dashboard = self.dashboard_class(self._app_labels, self.name)

        #if admin google analytics is enabled
        if ls.ADMIN_GOOGLE_ANALYTICS_FLOW:
            #get the analytics user credentials
            storage = Storage(ls.ADMIN_GOOGLE_ANALYTICS['token_file_name'])
            credential = storage.get()
            
            if credential is None or credential.invalid == True:
                extra_context['ga_data'] = { 'error' : 'authentication' }
            else:
                #get the data
                from utils import get_analytics_data
                http = httplib2.Http()
                extra_context['ga_data'] = get_analytics_data(credential.authorize(http))

        context = {
            'title': _('Site administration'),
            'app_list': dashboard.get_app_list(request, self._registry),
            'dashboard': dashboard
        }
        context.update(extra_context or {})
        return TemplateResponse(request, self.get_index_template() or
                                'admin/index.html', context,
                                current_app=self.name)

    def app_index(self, request, app_label, extra_context=None):
        #check if the view is disabled
        if getattr(settings, 'ADMIN_DISABLE_APP_INDEX', False):
            raise Http404

        dashboard = self.dashboard_class(self._app_labels, self.name)
        app_dict = dashboard.get_app_list(request, self._registry, app_label)
        if not app_dict:
            raise Http404('The requested admin page does not exist.')
        context = {
            'title': _('%s administration') % capfirst(app_label),
            'app_list': [app_dict],
        }
        context.update(extra_context or {})

        return TemplateResponse(request, self.app_index_template or [
            'admin/%s/app_index.html' % app_label,
            'admin/app_index.html'
        ], context, current_app=self.name)
        

    def i18n_javascript(self, request):
        """
        Override the original js catalog function to include additional
        js translation messages based on a yawd-admin setting and cache
        the results per language.
        """
        cache_key = 'ya-jsi18n-%s' % get_language()
        cache_timeout = getattr(settings, 'ADMIN_JS_CATALOG_CACHE_TIMEOUT', 60 * 60)
        cached = cache.get(cache_key)

        if not cached or not cache_timeout:
            if settings.USE_I18N:
                from django.views.i18n import javascript_catalog
            else:
                from django.views.i18n import null_javascript_catalog as javascript_catalog

            cached = javascript_catalog(request, packages=['django.conf',
                                                     'django.contrib.admin',
                                                     'yawdadmin']
                                  + getattr(settings, 'ADMIN_JS_CATALOG', []))
            cache.set(cache_key, cached, cache_timeout)

        return cached
