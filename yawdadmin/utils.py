from django.core.urlresolvers import reverse
from django.utils import simplejson as json
from django.utils.translation import get_language
from django.utils.encoding import smart_str
from models import AppOption

#TODO: option permissions???

_option_app_labels = []

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
        
    if 'order' in option and db_option.order != option['order']:
        db_option.order = option['order'] 
    
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
        option_urls.append({ 'app_label' : option.title().replace ('_', ' '), 'url' : reverse('admin:app_label_options', kwargs={ 'app_label' : option }, current_app='admin')})
    return option_urls

def get_option(app_label, name):
    """
    Return the value of an option.
    """
    try:
        option = AppOption.objects.get(app_label=app_label, name=name)
    except AppOption.DoesNotExist:
        return None
    
    return get_option_value(option)

def get_options(app_label):
    """
    Return all options for this app_label as dictionary with the option name
    being the key. 
    """
    try:
        options = AppOption.objects.filter(app_label=app_label)
    except:
        return {}
    
    option_dict = {}
    for option in options:
        option_dict[option.name] = get_option_value(option)
        
    return option_dict

def get_option_value(db_option):
    """
    Given an AppOption object, return its value for the current language.
    """
    
    field = load_form_field(db_option.field_type, 
                    json.loads(db_option.field_type_kwargs) if db_option.field_type_kwargs else {},
                    help_text = db_option.help_text, 
                    label = db_option.label)

    if not db_option.lang_dependant:
        return field.to_python(db_option.value)
    
    value_dict = json.loads(db_option.value)
    curr_lang = get_language()

    if curr_lang in value_dict:
        return field.to_python(value_dict[curr_lang])
    
def load_form_field(field_type, init_args, label, help_text=''):
    """
    Instantiate a form field.
    
        ``field_type``: a string representing the full path to the for field class
        ``init_args`` a dictionary that will be used to provide keyword arguments when calling the __init__() method
    """
    field = _get_class_from_string(field_type)
    
    init_args = init_args.copy()
    init_args['label'] = label
    if help_text:
        init_args['help_text'] = help_text
    if 'widget' in init_args:
        init_args['widget'] = _get_class_from_string(init_args['widget'])
        if 'widget_kwargs' in init_args:
            #instantiate the widget if widget_kwargs are provided
            init_args['widget'] = init_args['widget'](**init_args['widget_kwargs'])  
            del init_args['widget_kwargs']

    return field(**init_args)

def _get_class_from_string(path):
    comp = smart_str(path).split('.')
    module = __import__('.'.join(comp[:-1]), fromlist=[comp[-1]])
    return getattr(module, comp[-1])