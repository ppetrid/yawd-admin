from datetime import date
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.timezone import now


class SideBarMenuExample(models.Model):
    #HTML in help text is allowed in yawd-admin
    title =  models.CharField(max_length='50', help_text='<strong>The affix</strong>'\
            ' example title. Help text may include HTML.')
    field1 =  models.CharField(max_length='50', blank=True)
    field2 =  models.CharField(max_length='50', blank=True, help_text='Small input field')
    field3 =  models.CharField(max_length='50', blank=True, help_text='Medium input field')
    field4 =  models.CharField(max_length='50', blank=True, help_text='Large input field (default)')
    field5 =  models.CharField(max_length='50', blank=True, help_text='XLarge input field')
    field6 =  models.CharField(max_length='50', blank=True, help_text='XXLarge input field')
    field7 =  models.CharField(max_length='50', blank=True)
    field8 =  models.CharField(max_length='50', blank=True)
    field9 =  models.CharField(max_length='50', blank=True)

    class Meta:
        verbose_name = 'Side-Bar menu example'
        verbose_name_plural = 'Side-Bar menu example'

    def __unicode__(self):
        return u'%s' % self.title


class DragNDropChangelistExample(models.Model):
    title =  models.CharField(max_length='50')
    subtitle =  models.CharField(max_length='50', blank=True)
    boolean = models.BooleanField(default=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ('order',)
        verbose_name = 'Drag n\' drop changelist example' 
        verbose_name_plural = 'Drag n\' drop changelist example'

    def __unicode__(self):
        return u'%s' % self.title


class InlineExample(models.Model):
    title =  models.CharField(max_length='50')

    class Meta:
        verbose_name = 'Inline example' 
        verbose_name_plural = 'Inline example'

    def __unicode__(self):
        return u'%s' % self.title


class InlineExampleExtension(models.Model):
    field1 = models.CharField(max_length='50', blank=True)
    field2 = models.CharField(max_length='50', blank=True)
    field3 = models.CharField(max_length='50', blank=True)
    inline = models.OneToOneField(InlineExample)

    class Meta:
        verbose_name = 'One-To-One inline example' 
        verbose_name_plural = 'One-To-One inline example'


class StackedInlineExample(models.Model):
    title =  models.CharField(max_length='50')    
    field1 =  models.CharField(max_length='50', blank=True)
    choice = models.CharField(max_length='20', choices=(('choice1', 'Choice 1'),
                                                        ('choice2', 'Choice 2')))

    inline = models.ForeignKey(InlineExample)

    class Meta:
        verbose_name = 'Stacked inline example' 
        verbose_name_plural = 'Stacked inline example'

    def __unicode__(self):
        return u'%s' % self.title


class TabularInlineExample(models.Model):
    title =  models.CharField(max_length='50')    
    choice = models.CharField(max_length='20', choices=(('choice1', 'Choice 1'),
                                                        ('choice2', 'Choice 2')))
    inline = models.ForeignKey(InlineExample)

    class Meta:
        verbose_name = 'Tabular inline example' 
        verbose_name_plural = 'Tabular inline example'

    def __unicode__(self):
        return u'%s' % self.title


class ModalStackedInlineExample(models.Model):
    title =  models.CharField(max_length='50')
    description = models.TextField(blank=True)
    choice = models.CharField(max_length='20', choices=(('choice1', 'Choice 1'),
                                                        ('choice2', 'Choice 2')))
    date = models.DateField(default=date.today)
    inline = models.ForeignKey(InlineExample)

    class Meta:
        verbose_name = 'Modal stacked inline example' 
        verbose_name_plural = 'Modal stacked inline example'

    def __unicode__(self):
        return u'%s' % self.title


class PopupInlineExample(models.Model):
    title =  models.CharField(max_length='50')
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    inline = models.ForeignKey(InlineExample)

    class Meta:
        ordering = ('order',)
        verbose_name = 'Ajax/Popup inline example' 
        verbose_name_plural = 'Ajax/Popup inline example'

    def __unicode__(self):
        return u'%s' % self.title


class NestedInlineExample(models.Model):
    property = models.CharField(max_length=50)
    popupinline = models.ForeignKey(PopupInlineExample)

    class Meta:
        verbose_name = 'Nested inline' 
        verbose_name_plural = 'Nested inline'

    def __unicode__(self):
        return u'%s' % self.property


class WidgetsExample(models.Model):
    autocomplete = models.CharField(help_text='This widget suggests values based on '\
                                    'other records',
                                    max_length=50)
    text_area = models.TextField(blank=True)
    datetime = models.DateTimeField(default=now)
    radio_select = models.CharField(max_length=20, choices=(('choice1', 'Choice 1'),
                                                             ('choice2', 'Choice 2'),
                                                             ('choice3', 'Choice 3')),
                                    blank=False, default='choice1')
    boolean = models.BooleanField(default=False)
    boolean2 = models.BooleanField(default=False, help_text='You can change the switch labels, '\
                                   'size and colors, like in the fields below.')
    boolean3 = models.BooleanField(default=False)
    boolean4 = models.BooleanField(default=False)
    foreign_key = models.ForeignKey(SideBarMenuExample, null=True, blank=True,
                                    related_name='fk1',
                                    help_text='add dialog opens in fancybox')
    foreign_key2 = models.ForeignKey(SideBarMenuExample, null=True, blank=True,
                                     help_text='raw_id opens in fancybox as well',
                                     related_name='fk2')
    foreign_key3 = models.ForeignKey(SideBarMenuExample, null=True, blank=True,
                                     help_text='select2 alternative for foreign keys. '\
                                     'This adds a search box to quickly find '\
                                     'the records you\'re looking for.',
                                     related_name='fk3')
    multiple_select = models.ManyToManyField(SideBarMenuExample, null=True, blank=True,
                                             help_text='<p>Default multiple select with '\
                                             'horizontal filtering.</p>')
    multiple_select2 = models.ManyToManyField(DragNDropChangelistExample, null=True,
                                              blank=True,
                                              help_text='<p>Same as above, but with '\
                                              'the Select2MultipleWidget widget.</p>'\
                                              '<p class="small text-info">The annoying "Hold down Control..."'\
                                              ' message that django automatically '\
                                              'appends to this help text will be at '\
                                              'last removed in django 1.6!</p>')

    
    class Meta:
        verbose_name = 'Widgets example' 
        verbose_name_plural = 'Widgets example'

    def __unicode__(self):
        return u'%s' % self.autocomplete

    