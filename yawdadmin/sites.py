from functools import update_wrapper
from django.conf.urls import patterns, url
from django.conf import settings
from django.contrib.admin.sites import AdminSite
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse, NoReverseMatch
from django.utils.text import capfirst
from models import AppOption
from views import AppOptionView

_optionset_labels = {}

class YawdAdminSite(AdminSite):
    
    def __init__(self, *args, **kwargs):
        super(YawdAdminSite, self).__init__(*args, **kwargs)
        self._top_menu = {}
        
    def check_dependencies(self):
        """
        Override the default method to check that the 
        :class:`yawdadmin.middleware.PopupMiddleware` is installed
        and ``yawdadmin`` is found in the INSTALLED_APPS setting **before**
        ``django.contrib.admin``.
        """
        super(YawdAdminSite, self).check_dependencies()
        if not AppOption._meta.installed:
            raise ImproperlyConfigured("Put 'yawdadmin' in your "
                "INSTALLED_APPS setting in order to use the yawd-admin application.")
        if settings.INSTALLED_APPS.index('yawdadmin') > settings.INSTALLED_APPS.index('django.contrib.admin'):
            raise ImproperlyConfigured("Put 'yawdadmin' before 'django.contrib.admin' "
                "in your INSTALLED_APPS setting to use the yawd-admin application") 
        if not 'yawdadmin.middleware.PopupMiddleware' in settings.MIDDLEWARE_CLASSES:
            raise ImproperlyConfigured("Put 'yawdadmin.middleware.PopupMiddleware' "
                "in your MIDDLEWARE_CLASSES setting in order to use the yawd-admin application.")
        
    def get_urls(self):
        global _optionset_labels
        urlpatterns = super(YawdAdminSite, self).get_urls()
        
        def wrap(view, cacheable=False):
            def wrapper(*args, **kwargs):
                return self.admin_view(view, cacheable)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        urlpatterns += patterns('',
            url(r'^configuration-options/(?P<optionset_label>%s)/$' % '|'.join(_optionset_labels.keys()),
            wrap(AppOptionView.as_view()),
            name='optionset-label-options'))

        return urlpatterns
        
    def register_top_menu_item(self, item, icon_class=''):
        app_labels = []
        for model, model_admin in self._registry.iteritems():
            if not model._meta.app_label in app_labels:
                app_labels.append(model._meta.app_label)
        
        if isinstance(item, basestring) and item in app_labels:
            if not item in self._top_menu:
                self._top_menu[item] = icon_class
        else:
            raise Exception("Item has to be a valid app_label")
        
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
            if app_label in self._top_menu:
                has_module_perms = user.has_module_perms(app_label)

                if has_module_perms:
                    perms = model_admin.get_model_perms(request)
        
                    # Check whether user has any perm for this module.
                    # If so, add the module to the model_list.
                    if True in perms.values():
                        info = (app_label, model._meta.module_name)
                        model_dict = {
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

                        model_dict['order'] = model_admin.order if hasattr(model_admin, 'order') else 3
                        model_dict['separator'] = model_admin.separator if hasattr(model_admin, 'separator') else False

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
    
    def unregister_options(self, optionset_admin):
        optionset_label = optionset_admin.optionset_label
        if optionset_label in _optionset_labels:
            AppOption.objects.filter(optionset_label=optionset_label).delete()
            del _optionset_labels[optionset_label]
        
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