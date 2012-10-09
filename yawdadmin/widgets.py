from django import forms
from itertools import chain
from django.contrib.contenttypes.models import ContentType
from django.utils.safestring import mark_safe

class ContentTypeSelect(forms.Select):
    def __init__(self, lookup_id,  attrs=None, choices=()):
        self.lookup_id = lookup_id
        super(ContentTypeSelect, self).__init__(attrs, choices)
        
    def render(self, name, value, attrs=None, choices=()):
        output = super(ContentTypeSelect, self).render(name, value, attrs, choices)
        
        choices = chain(self.choices, choices)
        choiceoutput = ' var %s_choice_urls = {' % (attrs['id'],)
        for choice in choices:
            try:
                ctype = ContentType.objects.get(pk=int(choice[0]))
                choiceoutput += '    \'%s\' : \'../../../%s/%s?t=%s\','  % ( str(choice[0]), 
                    ctype.app_label, ctype.model, ctype.model_class()._meta.pk.name)
            except:
                pass
        choiceoutput += '};'
        
        output += ('<script type="text/javascript">'
                   '(function($) {'
                   '  $(document).ready( function() {'
                   '%(choiceoutput)s'
                   '    $(\'#%(id)s\').change(function (){'
                   '        $(\'#%(fk_id)s\').attr(\'href\',%(id)s_choice_urls[$(this).val()]);'
                   '    });'
                   '  });'
                   '})(yawdadmin.jQuery);'
                   '</script>' % { 'choiceoutput' : choiceoutput, 
                                    'id' : attrs['id'],
                                    'fk_id' : self.lookup_id
                                  })
        return mark_safe(u''.join(output))