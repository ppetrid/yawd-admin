import re
from functools import update_wrapper
from django.contrib.admin.sites import AdminSite
from django.conf.urls import patterns, url
from django.utils.text import capfirst
from django.core.urlresolvers import reverse, NoReverseMatch
from django.contrib import admin
from models import AppOption
from utils import load_form_field, add_option_app_label, get_option_app_labels, init_option
from views import AppOptionView

class YawdAdminSite(AdminSite):
    
    def __init__(self, *args, **kwargs):
        super(YawdAdminSite, self).__init__(*args, **kwargs)
        self._registry = admin.site._registry
        self._top_menu = {}
        
    def get_urls(self):
        urlpatterns = super(YawdAdminSite, self).get_urls()
        
        def wrap(view, cacheable=False):
            def wrapper(*args, **kwargs):
                return self.admin_view(view, cacheable)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        urlpatterns += patterns('',
            url(r'^(?P<app_label>%s)/configuration-options/$' % '|'.join(get_option_app_labels()),
            wrap(AppOptionView.as_view()),
            name='app_label_options'))

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
    
    def register_options(self, app_label, options):
        """
        Allows an application to register admin options
        on a certain field_label like so::
        
            admin_site.register_options('myapp', [{
                'name' : 'Site name',
                'field_type' : 'django.forms.EmailField'
            }])
        """
        
        if not app_label or not re.match(r'[a-zA-z_]+', app_label):
            raise Exception("app_label must be set in register_options and contain only letters and underscores")
        
        for option in options:
            
            #check if option has a proper name
            try:
                name = option['name']
            except KeyError:
                raise Exception("Each option dictionary should have a 'name' key.")
            
            #Check if field_type is a valid type
            try:
                load_form_field(option['field_type'], 
                    option['field_type_kwargs'] if 'field_type_kwargs' in option else {},
                    label=option['label'] if 'label' in option else option['name'].title(),
                    help_text = option['help_text'] if 'help_text' in option else '') 
            except KeyError:
                raise Exception("Each option dictionary should have a 'field_type' key.")
            except Exception:
                raise Exception("'field_type' should be a path to a python class defining a Form Field.")

            db_option, created = AppOption.objects.get_or_create(name = name, app_label = app_label)
            init_option(db_option, option)

        if options:            
            add_option_app_label(app_label)
            
    def unregister_option(self, app_label, name):
        try:
            AppOption.objects.filter(name=name, app_label=app_label).delete()
        except:
            raise Exception("Option not found")