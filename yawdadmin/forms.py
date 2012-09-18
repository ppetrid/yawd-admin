import re
from django import forms
from django.utils import simplejson as json
from django.utils.translation import get_language_info, ugettext as _
from models import AppOption
from utils import load_form_field

#decouple yawd-admin and yawd-translations applications
try:
    from translations.utils import get_supported_languages
except:
    #mimic the yawd-translations get_supported languages() behavior
    #for the languages defined in settings.LANGUAGES
    from django.conf import settings
    def get_supported_languages():
        return [x[0] for x in settings.LANGUAGES]

class AppOptionForm(forms.Form):

    def __init__(self, app_label, *args, **kwargs):
        """
        Overrides the default form constructor to iterate over the
        ``app_label``'s available AppOption instances 
        and inject appropiate Form Fields to the form.
        """

        options = AppOption.objects.filter(app_label=app_label)
                
        if not options:
            raise Exception("A valid app_label containing options must be set for this form to initialize")
        
        super(AppOptionForm, self).__init__(*args, **kwargs)
        
        self.options = {}
 
        for option in options:
            if not option.lang_dependant:
                #instantiate the form field
                field = load_form_field(option.field_type, 
                    json.loads(option.field_type_kwargs) if option.field_type_kwargs else {},
                    help_text = option.help_text, 
                    label = option.label)

                self.fields[option.name] = field
                self.fields[option.name].initial = field.to_python(option.value)
            else:
                #deserialize a dictionary with all values per language 
                value_dict = json.loads(option.value) if option.value else {} 

                for lang in get_supported_languages():

                    #instatiate a form field for each language
                    field = load_form_field(option.field_type, 
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

                    if lang in value_dict:
                        self.fields[field_name].initial = field.to_python(value_dict[lang])
            
            #store the option in self.options to access it later on
            self.options[option.name] = option
                        
    def save(self):
        """
        Iterates over the form elements, converts them back to AppOption
        instances and saves them to the database.
        """

        #this dictionary is used to collect lang-dependant field values
        lang_dependant_value_dict = {}

        for field, value in self.cleaned_data.iteritems():
            #prepare value for save
            prep_value = self.fields[field].prepare_value(value)

            #check if is lang-dependant option
            field_match = re.match(r'^(?P<original>[a-zA-Z_]+)_0_(?P<lang>[a-zA-Z-]+)$', field)
            if field_match:
                original_field = field_match.group('original')
                lang = field_match.group('lang')
                
                if not original_field in lang_dependant_value_dict:
                    lang_dependant_value_dict[original_field] = {}
                
                lang_dependant_value_dict[original_field].update({
                    lang : prep_value
                })
            else:
                if self.options[field].value != prep_value:
                    self.options[field].value = prep_value
                    self.options[field].save()

        #save lang-dependant options
        for key, value in lang_dependant_value_dict.iteritems():
            self.options[key].value = json.dumps(value)
            self.options[key].save()
