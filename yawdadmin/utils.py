from django.utils import simplejson as json
from django.utils.translation import get_language
from django.utils.encoding import smart_str
from yawdadmin import admin_site
from models import AppOption

def get_option(optionset_label, name, current_only=True):
    """
    Return the value of an option.
    """
    try:
        option = AppOption.objects.get(optionset_label=optionset_label, name=name)
    except AppOption.DoesNotExist:
        return None
    
    optionset_admin = admin_site.get_optionset_admin(optionset_label)
    return get_option_value(optionset_admin, option, current_only)

def get_options(optionset_label, current_only=True):
    """
    Return all options for this app_label as dictionary with the option name
    being the key. 
    """
    try:
        options = AppOption.objects.filter(optionset_label=optionset_label)
    except:
        return {}
    
    optionset_admin = admin_site.get_optionset_admin(optionset_label)
    
    option_dict = {}
    for option in options:
        option_dict[smart_str(option.name)] = get_option_value(optionset_admin, option, current_only)
        
    return option_dict

def get_option_value(optionset_admin, db_option, current_only):
    """
    Given an AppOption object, return its value for the current language.
    """
    
    name = smart_str(db_option.name)
    if not name in optionset_admin.options:
        return None
    
    field = optionset_admin.options[name]

    if not db_option.lang_dependant:
        return field.to_python(db_option.value) if db_option.value else '' 
    
    value_dict = json.loads(db_option.value)

    if current_only:
        curr_lang = get_language()
        if curr_lang in value_dict:
            return field.to_python(value_dict[curr_lang]) if value_dict[curr_lang] else ''
    else:
        for key in value_dict:
            value_dict[key] = field.to_python(value_dict[key])
            return value_dict