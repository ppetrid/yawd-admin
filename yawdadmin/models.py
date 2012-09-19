from django.db import models
from fields import OptionNameField

class AppOption(models.Model):
    app_label = models.CharField(max_length=50)
    name = OptionNameField(max_length=50)
    value = models.TextField(null=True)
    field_type = models.CharField(max_length=100)
    field_type_kwargs = models.CharField(max_length=255, null=True)
    lang_dependant = models.BooleanField(default=False)
    label = models.CharField(max_length=50)
    help_text = models.CharField(max_length=255)
    order = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ('app_label', 'name')
        ordering = ['app_label', 'lang_dependant', 'order']

    def __unicode__(self):
        return u'%s.%s' % (self.app_label, self.name)