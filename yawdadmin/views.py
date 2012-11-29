from oauth2client import xsrfutil
from oauth2client.file import Storage
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponseBadRequest, Http404
from django.utils.translation import ugettext as _
from django.views.generic import TemplateView, RedirectView
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
        context['title'] = '%s %s' % (context['optionset_admin'].verbose_name, _('Configuration'))
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
    
class AnalyticsAuthView(RedirectView):
    """
    This view implements the oauth2 authentication callback.
    It stores the user credential to a file and redirects the user
    to the admin index page on success. 
    """
    permanent = False
    
    def get(self, request, *args, **kwargs):
        if not ls.ADMIN_GOOGLE_ANALYTICS_FLOW:
            raise Http404
        
        if not ('state' in request.REQUEST and xsrfutil.validate_token(settings.SECRET_KEY, request.REQUEST['state'], request.user)):
            return  HttpResponseBadRequest()
        
        credential = ls.ADMIN_GOOGLE_ANALYTICS_FLOW.step2_exchange(request.REQUEST) #@UndefinedVariable
        storage = Storage(ls.ADMIN_GOOGLE_ANALYTICS['token_file_name'])
        storage.put(credential)
        
        self.url = reverse('admin:index')
        return super(AnalyticsAuthView, self).get(request) 