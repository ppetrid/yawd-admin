from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.views.generic import FormView
from django.utils.translation import ugettext as _
from forms import AppOptionForm

class AppOptionView(FormView):
    form_class = AppOptionForm
    template_name = 'admin/options.html'
    success_url = reverse_lazy('admin:index')
    
    def get_form_kwargs(self):
        kwargs = super(AppOptionView, self).get_form_kwargs()
        kwargs.update({'app_label' : self.kwargs['app_label'] })
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super(AppOptionView, self).get_context_data(**kwargs)
        context['app_label'] = self.kwargs['app_label']
        context['title'] = '%s %s' % (self.kwargs['app_label'].title(), _('configuration options'))
        return context
    
    def form_valid(self, form):
        """
        This method is called when valid form data has been POSTed.
        Saves form data to the database
        """
        form.save()
        messages.add_message(self.request, messages.SUCCESS, _('The options were succesfully saved.'))
        return super(AppOptionView, self).form_valid(form)