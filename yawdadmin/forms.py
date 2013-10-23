from django import forms
from django.core.urlresolvers import reverse
from django.forms.models import BaseInlineFormSet
from django.contrib.auth import get_user_model


class PopupInlineFormSet(BaseInlineFormSet):
    changed_objects = []
    deleted_objects = []
    new_objects = []

    def is_valid(self):
        """
        Do not validate any forms, no forms actually exist
        """
        return True

    def clean(self):
        """
        Clean should not validate forms.
        """
        pass

    def full_clean(self):
        """
        Do not check for form errors as it will force form validation.
        The clean() hook remains for possible use in subclasses.
        """
        self._errors = []
        if not self.is_bound: # Stop further processing.
            return

        # Give self.clean() a chance to do cross-form validation.
        try:
            self.clean()
        except ValidationError as e:
            self._non_form_errors = self.error_class(e.messages)

    def get_add_url(self):
        return '%s?fk_name=%s&fk_id=%s' % (reverse('admin:%s_%s_add' % \
            (self.model._meta.app_label, self.model._meta.object_name.lower())),
                                  self.fk.name,
                                  self.instance.pk)

    def get_change_url(self, obj_id):
        return '%s?fk_name=%s' % (reverse('admin:%s_%s_change' % \
            (self.model._meta.app_label, self.model._meta.object_name.lower()),
            args=(obj_id,)),
                                  self.fk.name)

    def get_delete_url(self, obj_id):
        return reverse('admin:%s_%s_deleteit' % (self.model._meta.app_label,
                                                 self.model._meta.object_name.lower()),
                       args=(obj_id,))

    def get_reorder_url(self):
        return reverse('admin:%s_%s_inlinereorder' % (self.model._meta.app_label,
                                                 self.model._meta.object_name.lower()))

    def save(self, commit=True):
        """
        Override save_new to do nothing, as everything is handled by ajax requests.
        """
        return True


class AdminUserModelForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ('username', 'first_name', 'last_name', 'email')
