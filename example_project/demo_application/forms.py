from django import forms
from models import Income

class IncomeForm(forms.ModelForm):
    class Meta:
        widgets = {
            'description' : forms.Textarea(attrs={"class" : "textarea-medium"})
        }
    