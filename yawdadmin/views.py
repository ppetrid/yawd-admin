from django.views.generic import FormView
from django.utils.translation import ugettext as _
from forms import AppOptionForm

class AppOptionView(FormView):
    form_class = AppOptionForm
    template_name = 'admin/options.html'
    
    def get_form_kwargs(self):
        kwargs = {'app_label' : self.kwargs['app_label'] }
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super(AppOptionView, self).get_context_data(**kwargs)
        context['app_label'] = self.kwargs['app_label']
        context['title'] = '%s %s' % (self.kwargs['app_label'].title(), _('configuration options'))
        return context