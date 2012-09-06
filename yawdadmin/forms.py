from django import forms
from django.utils import simplejson as json
from django.utils.encoding import smart_str
from django.utils.translation import get_language_info, ugettext as _
from translations.utils import get_supported_languages
from models import AppOption
from utils import load_form_field

class AppOptionForm(forms.Form):

    def __init__(self, app_label, *args, **kwargs):
        
        options = AppOption.objects.filter(app_label=app_label)
                
        if not options:
            raise Exception("A valid app_label containing options must be set for this form to initialize")
        
        super(AppOptionForm, self).__init__(*args, **kwargs)
        
        for option in options:
            if not option.lang_dependant:
                #instantiate the form field
                field = load_form_field(smart_str(option.field_type), 
                    json.loads(option.field_type_kwargs) if option.field_type_kwargs else {},
                    help_text = option.help_text, 
                    label = option.label)

                self.fields[option.name] = field
                self.fields[option.name].initial = option.value 
            else:
                #deserialize a dictionary with all values per language 
                value_dict = {}
                if option.value:
                    value_dict = json.loads(option.value)

                for lang in get_supported_languages():

                    #intatiate a form field for each language
                    field = load_form_field(smart_str(option.field_type), 
                        json.loads(option.field_type_kwargs) if option.field_type_kwargs else {},
                        help_text = _(option.help_text), 
                        label = '%(label)s (%(lang)s)' % {
                                'label' : _(option.label),
                                'lang' : _(get_language_info(lang)['name']) })
                    
                    #Use '_0_' as separator for dynamic multilingual options
                    #since numbers are not allowed in option names, we can
                    #distinguish multilingual options based solely on their name
                    field_name = '%s_0_%s' % (option.name, lang)
                    self.fields[field_name] = field

                    if 'lang' in value_dict:
                        self.fields[field_name].initial = value_dict[lang]
