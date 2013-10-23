from itertools import chain
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe


class ContentTypeSelect(forms.Select):
    def __init__(self, object_id,  attrs=None, choices=()):
        self.object_id = 'id_%s' % object_id
        super(ContentTypeSelect, self).__init__(attrs, choices)
  
    def render(self, name, value, attrs=None, choices=()):
        output = super(ContentTypeSelect, self).render(name, value, attrs, choices)

        choiceoutput = ' var %s_choice_urls = {' % (attrs['id'],)

        for ctype in ContentType.objects.filter(pk__in=[int(c[0])for c in chain(self.choices, choices) if c[0]]):
            choiceoutput += '    \'%s\' : \'../../../%s/%s?t=%s\','  % ( str(ctype.pk), 
                    ctype.app_label, ctype.model, ctype.model_class()._meta.pk.name)

        choiceoutput += '};'

        output += ('<script>'
                   '(function($) {'
                   '  $(document).ready( function() {'
                   '%(choiceoutput)s'
                   '    $(\'#%(id)s\').change(function (){'
                   '        $(\'#%(fk_id)s\').val(\'\');'
                   '        $(\'#lookup_%(fk_id)s\').attr(\'href\',%(id)s_choice_urls[$(this).val()]+"&pop=1").siblings(\'strong\').html(\'\');'
                   '    });'
                   '  });'
                   '})(yawdadmin.jQuery);'
                   '</script>' % { 'choiceoutput' : choiceoutput, 
                                    'id' : attrs['id'],
                                    'fk_id' : self.object_id
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

    class Media:
        css = {'all': ('yawd-admin/css/select2/select2.css',)}
        js = ('yawd-admin/css/select2/select2.min.js',)

    def render(self, name, value, attrs=None, choices=()):
        result = super(Select2MultipleWidget, self).render(name, value, attrs, choices)
        return result + mark_safe('<script>(function($){'\
                                  '$(\'#%s\').select2();'\
                                  '})(yawdadmin.jQuery);</script>' % attrs['id'])


class Select2Widget(forms.Select):
    select2_options = ''

    class Media:
        css = {'all': ('yawd-admin/css/select2/select2.css',)}
        js = ('yawd-admin/css/select2/select2.min.js',)

    def render(self, name, value, attrs=None, choices=()):
        result = super(Select2Widget, self).render(name, value, attrs, choices)
        return result + mark_safe('<script>(function($){'\
                                  '$(\'#%s\').select2(%s);'\
                                  '})(yawdadmin.jQuery);</script>' % (attrs['id'],
                                                                      self.select2_options))


class SwitchWidget(forms.CheckboxInput):
    class Media:
        js = ('yawd-admin/js/bootstrap.switch.min.js',)

    def render(self, name, value, attrs=None):
        output = super(SwitchWidget, self).render(name, value, attrs)

        data_on_label = self.attrs.pop('data-on-label', _('YES'))
        data_off_label = self.attrs.pop('data-off-label', _('NO'))
        data_on = self.attrs.pop('data-on', 'primary')
        data_off = self.attrs.pop('data-off', 'default')
        classes = self.attrs.pop('class', '')

        return mark_safe('<div class="switch %s" data-on="%s" data-off="%s" '\
                         'data-on-label="%s" data-off-label="%s">' % (
                    classes, data_on, data_off,
                    data_on_label, data_off_label)) + output + mark_safe('</div>')
