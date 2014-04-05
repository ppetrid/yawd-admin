import json
from oauth2client import xsrfutil
from oauth2client.file import Storage
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponseBadRequest, HttpResponseRedirect, Http404
from django.utils.translation import ugettext as _
from django.views.generic import TemplateView, View, UpdateView
from conf import settings as ls


class AppOptionView(TemplateView):
    template_name = 'admin/options.html'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.has_perm('yawdadmin.change_appoption'):
            raise PermissionDenied
        return super(AppOptionView, self).dispatch(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instantiating the 
        form. Copied form the generic FormView class-based view
        """
        kwargs = {}
        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data':self.request.POST, 
                'files':self.request.FILES, 
                })
        return kwargs

    def get_context_data(self, **kwargs):
        from yawdadmin import admin_site
        context = super(AppOptionView, self).get_context_data(**kwargs)
        context['optionset_admin'] = admin_site.get_optionset_admin(self.kwargs['optionset_label'])(**self.get_form_kwargs())
        context['title'] = '%s' % (unicode(context['optionset_admin'].verbose_name))
        return context
    
    def post(self, request, *args, **kwargs):
        """
        Validate the form and save the options upon success
        """
        context = self.get_context_data()
        if context['optionset_admin'].form.is_valid():
            context['optionset_admin'].save()
            messages.add_message(self.request, messages.SUCCESS, _('The options were succesfully saved.'))
        return self.render_to_response(context)
    
    def put(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


class AnalyticsAuthView(View):
    """
    This view implements the oauth2 authentication callback.
    It stores the user credential to a file and redirects the user
    to the admin index page on success. 
    """
    permanent = False
    
    def get(self, request, *args, **kwargs):
        #check view
        valid_analytics_view(request)
        
        if not ('state' in request.REQUEST and xsrfutil.validate_token(settings.SECRET_KEY, request.REQUEST['state'], request.user)):
            return  HttpResponseBadRequest()
        
        credential = ls.ADMIN_GOOGLE_ANALYTICS_FLOW.step2_exchange(request.REQUEST) #@UndefinedVariable
        storage = Storage(ls.ADMIN_GOOGLE_ANALYTICS['token_file_name'])
        storage.put(credential)
        
        messages.add_message(self.request, messages.SUCCESS, _('The user was successfully connected.'))
        return HttpResponseRedirect(reverse('admin:analytics'))


class AnalyticsConfigView(TemplateView):
    """
    Admin view for the google analytics functionality. The view is 
    accessible through the top bar navigation.
    """
    template_name = 'admin/analytics.html'
    
    def get_context_data(self, **kwargs):
    
        #check view
        valid_analytics_view(self.request)
        #get original context data
        context = super(AnalyticsConfigView, self).get_context_data(**kwargs)
        #load the token file
        try:
            dat_file = open(ls.ADMIN_GOOGLE_ANALYTICS['token_file_name'], 'r')
            analytics = json.loads(dat_file.read())
            dat_file.close()
        except (IOError, ValueError):
            analytics = {}
        
        context['analytics_info'] = {
            'profile' : ls.ADMIN_GOOGLE_ANALYTICS['profile_id'],
            'interval' : ls.ADMIN_GOOGLE_ANALYTICS['interval'],
            'data' : analytics
        }
        
        return context


class AnalyticsConnectView(View):
    """
    Connect a new user to the Google Analytics API
    """
    def get(self, request, *args, **kwargs):
        
        #check view
        valid_analytics_view(request)
        try: 
            #Empty the token file 
            dat_file = open(ls.ADMIN_GOOGLE_ANALYTICS['token_file_name'], 'w+')
            dat_file.write('')
            dat_file.close()
        except:
            messages.add_message(self.request, messages.ERROR, _('The server does not have permissions to write to the token file. Please contact your system administrator.'))
            return HttpResponseRedirect(reverse('admin:analytics'))

        #Initialize flow
        ls.ADMIN_GOOGLE_ANALYTICS_FLOW.params['state'] = xsrfutil.generate_token(settings.SECRET_KEY, request.user) #@UndefinedVariable
        return HttpResponseRedirect(ls.ADMIN_GOOGLE_ANALYTICS_FLOW.step1_get_authorize_url()) #@UndefinedVariable


def valid_analytics_view(request):
    """
    Check if the user is superuser and analytics functionality is enabled. 
    """
    if not request.user.is_superuser:
            raise PermissionDenied
    
    if not ls.ADMIN_GOOGLE_ANALYTICS_FLOW:
        raise Http404


class MyAccountView(UpdateView):
    template_name = 'registration/my_account.html'
    form_class = ls.ADMIN_USER_MODELFORM
    
    def __init__(self, *args, **kwargs):
        super(MyAccountView, self).__init__(*args, **kwargs)
        self.success_url = reverse('admin:my-account')
        
    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS,
                             _('Your account has been updated successfuly.'))
        return super(MyAccountView, self).form_valid(form)
    
    def get_object(self):
        return self.request.user
    
    def get_context_data(self, **kwargs):
        context = super(MyAccountView, self).get_context_data(**kwargs)
        context['title'] = _('My account')
        return context
