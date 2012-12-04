from django import forms
from itertools import chain
from django.contrib.contenttypes.models import ContentType
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