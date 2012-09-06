import re
from django.db import models
from django.core.exceptions import ValidationError

class OptionNameField(models.CharField):
    
    def clean(self, value):
        value = super(OptionNameField, self).clean(value)
        if not re.match(r'[a-zA-Z_]+', value):
            raise ValidationError('Only letters and underscores are allowed.')
        return value