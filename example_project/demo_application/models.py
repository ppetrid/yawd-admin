from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

class Income(models.Model):
    title = models.CharField(max_length='150', help_text='The income title')
    description = models.TextField(blank=True, help_text='Optional description of the transaction')
    repeated = models.BooleanField(help_text='Is this income repeated?')
    when = models.CharField(blank=True, max_length=10, choices=(('monthly','Monthly'),('yearly','Yearly')), help_text='How often does this income occur?')
    
    def __unicode__(self):
        return u'%s' % self.title

class Transaction(models.Model):
    content_type = models.ForeignKey(ContentType, limit_choices_to = {"model__in": ("income", "expense")})
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey()
    #Html in help_text is allowed for yawd-admin
    amount = models.FloatField(help_text='The amount of money for this transaction. Use <em>\'.\'</em> as decimal point.')
    date = models.DateField(blank=True, null=True, help_text='When did this transaction occur?')
    is_paid = models.BooleanField(default=False, help_text='Leave this checked only if the money is already in your pocket!')
    
class Expense(models.Model):
    title =  models.CharField(max_length='150', help_text='The expense title')
    description = models.TextField(blank=True, help_text='Optional description of the transaction')
    repeated = models.BooleanField(help_text='Is this expense repeated?')
    when = models.CharField(blank=True, max_length=10, choices=(('monthly','Monthly'),('yearly','Yearly')), help_text='How often does this expense occur?')