from django import forms
from django.core.urlresolvers import reverse_lazy
from yawdadmin.widgets import AutoCompleteTextInput, Select2MultipleWidget, \
    Select2Widget, SwitchWidget, BootstrapRadioRenderer


class SideBarExampleAdminForm(forms.ModelForm):
    class Meta:
        widgets = {
            'field2': forms.TextInput(attrs={"class" : "input-small"}),
            'field3': forms.TextInput(attrs={"class" : "input-medium"}),
            'field5': forms.TextInput(attrs={"class" : "input-xlarge"}),
            'field6': forms.TextInput(attrs={"class" : "input-xxlarge"}),
        }


class WidgetsExampleAdminForm(forms.ModelForm):
    class Meta:
        widgets = {
            'autocomplete': AutoCompleteTextInput(source=\
                                    reverse_lazy('autocomplete-example-view')),
            'radio_select': forms.RadioSelect(renderer=BootstrapRadioRenderer),
            'boolean2': SwitchWidget,
            'boolean3': SwitchWidget(attrs={'class': 'switch-large',
                                            'data-on-label': 'ON',
                                            'data-off-label': 'OFF',
                                            'data-on': 'success',
                                            'data-off': 'danger'}),
            'boolean4': SwitchWidget(attrs={'class': 'switch-small',
                                            'data-on': 'info',
                                            'data-off': 'warning'}),
            #for text areas you can use the textarea-large, textarea-small etc classes
            'text_area': forms.Textarea(attrs={'class': 'textarea-medium'}),
            'foreign_key3': Select2Widget(attrs={'style': 'width: 220px;'}),
            'multiple_select2': Select2MultipleWidget,
        } 
