import re, copy
from django import forms
from django.utils import simplejson as json
from utils import get_options
from models import AppOption

#decouple yawd-admin and yawd-translations applications
try:
    from translations.utils import get_supported_languages
except:
    #mimic the yawd-translations get_supported languages() behavior
    #for the languages defined in settings.LANGUAGES
    from django.conf import settings
    def get_supported_languages():
        return [x[0] for x in settings.LANGUAGES]
    
_optionsetadmin_classes = {}

class SiteOption(object):
    order_counter = 0
    
    def __init__(self, field=None, lang_dependant=False):
        
        if not isinstance(field, forms.Field):
            raise Exception('The field must be a valid field instance')
        
        self.field = field
        self.lang_dependant = lang_dependant
        #remember the order in which fields were initialized
        self.order_counter = SiteOption.order_counter
        SiteOption.order_counter += 1

class OptionSetBase(type):
    """
    metaclass for all OptionSets
    """ 
    def __new__(self, name, bases, attrs):
        super_new = super(OptionSetBase, self).__new__
        parents = [b for b in bases if isinstance(b, OptionSetBase)]
        if not parents:
            # If this isn't a subclass of Model, don't do anything special.
            return super_new(self, name, bases, attrs)
        
        # Create the class.
        # Add the options and form fields
        module = attrs.pop('__module__')
        
        try:
            optionset_label = attrs.pop('optionset_label')
        except KeyError:
            optionset_label = None

        if not optionset_label or not re.match(r'[a-zA-z-]+', optionset_label):
            raise TypeError("optionset_label must be set and contain only letters and underscores")
        
        # Because of the way imports happen (recursively), it may or may not be
        # the first time this model tries to register with the framework. 
        # There should only be one class for each OptionSetAdmin.
        global _optionsetadmin_classes
        if optionset_label in _optionsetadmin_classes:
            return _optionsetadmin_classes[optionset_label]

        try:        
            verbose_name = attrs.pop('verbose_name')
        except KeyError:
            verbose_name = optionset_label.title().replace ('-', ' ')
        
        new_class = super_new(self, name, bases, {
            '__module__': module, 
            'options' : {},
            'lang_options' : {},
            'attrs' : [],
            'optionset_label' : optionset_label,
            'verbose_name' : verbose_name,
        })
        
        for attr, value in attrs.items():
            if not isinstance(value, SiteOption):
                raise TypeError('Invalid attribute %s - should be a SiteOption instance' % attr)
            
            if not hasattr(value.field, 'label') or not value.field.label:
                value.field.label = attr.title().replace('_', ' ')

            new_class.attrs.append((attr, value))
            new_class.options[attr] = value.field 
            
        new_class.attrs.sort(lambda (attr1, value1), (attr2, value2): cmp(value1.order_counter, value2.order_counter))
        
        _optionsetadmin_classes[optionset_label] = new_class
        return new_class

def _init_option(optionset_label, name, siteoption):
    db_option, created = AppOption.objects.get_or_create(name = name, optionset_label = optionset_label)
    
    if siteoption.lang_dependant:
        ret = {}
        for l in get_supported_languages():
            ret[l] = ''
        db_option.value = json.dumps(ret)
    else:
        ret = ''
        db_option.value = ret
    
    if db_option.lang_dependant != siteoption.lang_dependant:
        db_option.lang_dependant = siteoption.lang_dependant
            
    if created:
        db_option.save()
    
    return ret
    
class OptionSetAdmin(object):
    __metaclass__ = OptionSetBase
    
    def __init__(self, **kwargs):
        self.form = forms.Form(**kwargs)

        #load option values from the database
        self.value_dict = get_options(optionset_label = self.optionset_label, current_only=False)
        self.formfields = []
        self.langformfields = {}

        for (attr, value) in self.attrs:

            if not attr in self.value_dict:
                self.value_dict[attr] = _init_option(self.optionset_label, attr, value)

            if value.lang_dependant:
                for lang in get_supported_languages():
                    #generate the form field
                    field_name = '%s_%s' % (attr, lang)
                    lang_field = copy.deepcopy(value.field)
                    lang_field.label = '%s (%s)' % (lang_field.label, lang.upper())
                    
                    self.form.fields[field_name] = lang_field
                    try:
                        self.form.fields[field_name].initial = self.value_dict[attr][lang]
                    except KeyError:
                        self.form.fields[field_name].initial = ''
                    
                    #add to land dependant options
                    self.lang_options[field_name] = (attr, lang)
                    
                    #langformfields fieldset
                    if not lang in self.langformfields:
                        self.langformfields[lang] = []
                    self.langformfields[lang].append(self.form[field_name])
            else:
                self.form.fields[attr] = value.field
                self.form.fields[attr].initial = self.value_dict[attr]
                self.formfields.append(self.form[attr])
    
    def save(self):
        #this dictionary is used to collect lang-dependant field values
        lang_dependant_value_dict = {}

        for field, value in self.form.cleaned_data.iteritems():
            #prepare value for save
            prep_value = self.form.fields[field].prepare_value(value)
             
            if field in self.lang_options:
                original_field = self.lang_options[field][0]
                lang = self.lang_options[field][1]
                
                if not original_field in lang_dependant_value_dict:
                    lang_dependant_value_dict[original_field] = {}
                
                lang_dependant_value_dict[original_field].update({
                    lang : prep_value
                })
            else:
                if self.value_dict[field] != prep_value:
                    AppOption.objects.filter(optionset_label=self.optionset_label, name=field).update(value = prep_value)
    
        #save lang-dependant options
        for key, value in lang_dependant_value_dict.iteritems():
            if self.value_dict[key] != value:
                AppOption.objects.filter(optionset_label=self.optionset_label, name=key).update(value = json.dumps(value))