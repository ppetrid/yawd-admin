import re
from itertools import chain
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext as _, ugettext_lazy, get_language
from django.utils.safestring import mark_safe

try: #Django 1.7+
    from django.contrib.admin.options import TO_FIELD_VAR #@UnresolvedImport
except:
    TO_FIELD_VAR = 't'

try: #Django 1.6+
    from django.contrib.admin.options import IS_POPUP_VAR #@UnresolvedImport
except:
    IS_POPUP_VAR = 'pop'


class ContentTypeSelect(forms.Select):
    def __init__(self, object_id,  attrs=None, choices=()):
        self.object_id = 'id_%s' % object_id
        super(ContentTypeSelect, self).__init__(attrs, choices)
  
    def render(self, name, value, attrs=None, choices=()):
        output = super(ContentTypeSelect, self).render(name, value, attrs, choices)

        choiceoutput = ' var %s_choice_urls = {' % (attrs['id'],)

        for ctype in ContentType.objects.filter(pk__in=[int(c[0])for c in chain(self.choices, choices) if c[0]]):
            choiceoutput += '    \'%s\' : \'../../../%s/%s?%s=%s\','  % ( str(ctype.pk), 
                    ctype.app_label, ctype.model,
                    TO_FIELD_VAR, ctype.model_class()._meta.pk.name)

        choiceoutput += '};'

        output += ('<script>'
                   '(function($) {'
                   '  $(document).ready( function() {'
                   '%(choiceoutput)s'
                   '    $(\'#%(id)s\').change(function (){'
                   '        $(\'#%(fk_id)s\').val(\'\');'
                   '        $(\'#lookup_%(fk_id)s\').attr(\'href\',%(id)s_choice_urls[$(this).val()]+"&%(popup_var)s=1").siblings(\'strong\').html(\'\');'
                   '    });'
                   '  });'
                   '})(yawdadmin.jQuery);'
                   '</script>' % { 'choiceoutput' : choiceoutput, 
                                    'id' : attrs['id'],
                                    'fk_id' : self.object_id,
                                    'popup_var': IS_POPUP_VAR
                                  })
        return mark_safe(u''.join(output))


class AutoCompleteTextInput(forms.TextInput):

    def __init__(self, *args, **kwargs):
        if 'source' in kwargs:
            self.source = kwargs['source']
            del kwargs['source']
        else:
            self.source = None
        super(AutoCompleteTextInput, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None):
        if self.source:
            attrs['autocomplete'] = 'off'
        output = super(AutoCompleteTextInput, self).render(name, value, attrs)
        if self.source:
            js = '<script>(function($){$("#%(id)s").typeahead({source: ' \
                'function(query, process) { $.get("%(source)s", {query: ' \
                'query},function(data) { return typeof data.results == ' \
                '"undefined" ? false : process(data.results); }, "json") ' \
                '}});})(yawdadmin.jQuery);</script>' % {'id': attrs['id'],
                                                        'source': self.source}
        return output + mark_safe(js)


class BootstrapRadioRenderer(forms.RadioSelect.renderer):
    def render(self):
        return mark_safe(u'\n'.join([u'%s\n' % unicode(w).replace('<label ', '<label class="radio inline" ') for w in self])+'&#xa0;')


class Select2MultipleWidget(forms.SelectMultiple):
    """
    Custom multiple selection widget based on http://ivaynberg.github.io/select2/
    
    Note that the resulting JavaScript assumes that the jsi18n
    catalog has been loaded in the page
    """    
    def _media(self):
        """
        Set the widget's javascript and css
        """
        return forms.Media(css = {'all': ('yawd-admin/css/select2/select2.css',)}, 
                           js = ('yawd-admin/css/select2/select2.min.js',
                                 'yawd-admin/css/select2/select2_locale_'+
                                 get_language()+'.js'))
    media = property(_media)

    def render(self, name, value, attrs=None, choices=()):
        result = super(Select2MultipleWidget, self).render(name, value, attrs, choices)
        return result + mark_safe('<script>(function($){'\
                                  '$(\'#%s\').select2();'\
                                  '})(yawdadmin.jQuery);</script>' % attrs['id'])


class Select2Widget(forms.Select):
    """
    Custom selection widget based on http://ivaynberg.github.io/select2/
    
    Note that the resulting JavaScript assumes that the jsi18n
    catalog has been loaded in the page
    """
    select2_options = ''
    
    def _media(self):
        """
        Set the widget's javascript and css
        """
        return forms.Media(css = {'all': ('yawd-admin/css/select2/select2.css',)}, 
                           js = ('yawd-admin/css/select2/select2.min.js',
                                 'yawd-admin/css/select2/select2_locale_'+
                                 get_language()+'.js'))
    media = property(_media)

    def render(self, name, value, attrs=None, choices=()):
        result = super(Select2Widget, self).render(name, value, attrs, choices)
        #read-only mode
        ro = ''
        if self.attrs and 'readonly' in self.attrs and self.attrs['readonly']:
            ro = '.select2("readonly", true)'

        return result + mark_safe('<script>(function($){'\
                                  '$(\'#%s\').select2(%s)%s;'\
                                  '})(yawdadmin.jQuery);</script>' % (attrs['id'],
                                                            self.select2_options,
                                                            ro))


class SwitchWidget(forms.CheckboxInput):
    class Media:
        js = ('yawd-admin/js/bootstrap.switch.min.js',)

    def render(self, name, value, attrs=None):
        switch_defaults = {
            'data-on-label': ugettext_lazy('YES'),
            'data-off-label': ugettext_lazy('NO'),
            'data-on': 'success',
            'data-off': 'danger'
        }
        switch_defaults.update(self.attrs)
        self.attrs = switch_defaults

        return super(SwitchWidget, self).render(name, value, attrs) + \
            mark_safe("<script>yawdadmin.jQuery('#%s').bootstrapSwitch();</script>" \
                        % attrs['id'])
