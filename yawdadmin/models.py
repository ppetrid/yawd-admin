from django.db import models
from fields import OptionNameField

class AppOption(models.Model):
    optionset_label = models.CharField(max_length=50)
    name = OptionNameField(max_length=50)
    value = models.TextField(null=True)
    lang_dependant = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('optionset_label', 'name')
        ordering = ['optionset_label', 'lang_dependant']

    def __unicode__(self):
        return u'%s.%s' % (self.optionset_label, self.name)