from django.core.urlresolvers import reverse
from django.utils import simplejson as json
from models import AppOption

#TODO: option permissions???

_option_app_labels = []

def load_form_field(field_type, init_args, label, help_text=''):
    """
    Instantiate a form field.
    
        ``field_type``: a string representing the full path to the for field class
        ``init_args`` a dictionary that will be used to provide keyword arguments when calling the __init__() method
    """
    comp = field_type.split('.')
    module = __import__('.'.join(comp[:-1]), fromlist=[comp[-1]])
    field = getattr(module, comp[-1])
    
    init_args['label'] = label
    if help_text:
        init_args['help_text'] = help_text

    return field(**init_args)

def init_option(db_option, option):

    if db_option.field_type != option['field_type']:
        db_option.field_type = option['field_type']
        db_option.value = ''
    
    if 'field_type_kwargs' in option:
        field_type_kwargs = json.dumps(option['field_type_kwargs'])
        if db_option.field_type_kwargs != field_type_kwargs:
            db_option.field_type_kwargs = field_type_kwargs
    else:
        db_option.field_type_kwargs = None
    
    if 'lang_dependant' in option and db_option.lang_dependant != option['lang_dependant']:
        db_option.lang_dependant = option['lang_dependant']
        
    if 'label' in option and db_option.label != option['label']:
        db_option.label = option['label']
    elif not 'label' in option:
        label = option['name'].replace('_', ' ').capitalize()
        if db_option.label != label:
            db_option.label = label

    if 'help_text' in option and db_option.help_text != option['help_text']:
        db_option.help_text = option['help_text']
    
    db_option.save()

def add_option_app_label(app_label):
    global _option_app_labels
    if not app_label in _option_app_labels:
        _option_app_labels.append(app_label)

def get_option_app_labels():
    return _option_app_labels

def get_option_admin_urls():
    option_urls = []
    for option in _option_app_labels:
        option_urls.append({ 'app_label' : option.title(), 'url' : reverse('admin:app_label_options', kwargs={ 'app_label' : option }, current_app='admin')})
    return option_urls
        