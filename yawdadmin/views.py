from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.views.generic import TemplateView
from django.utils.translation import ugettext as _

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