# -*- coding: utf-8 -*-
import itertools
from django import template
from ..admin import PopupInline
from ..forms import PopupInlineFormSet


register = template.Library()


@register.filter
def divide(value, num):
    return int(value / num)


@register.filter
def app_title(value):
    return value.replace('_', ' ')


@register.filter
def utfupper(value):
    orig = [u'Ά', u'Έ', u'Ή', u'Ί', u'ΐ', u'Ό', u'Ύ', u'Ώ']
    rep = [u'Α', u'Ε', u'Η', u'Ι', u'Ϊ', u'Ο', u'Υ', u'Ω']
    return u''.join([rep[orig.index(x)] if x in orig else x
                     for x in value.upper()])


@register.filter
def filter_show(app_list):
    return list(itertools.ifilter(lambda x: x['show'], app_list)) 


@register.filter
def filters_on(change_list):
    for spec in change_list.filter_specs:
        if spec.used_parameters:
            return True
    return False


@register.filter
def istranslationinline(value):
    """
    This filter is used if yawd-translations is installed.
    """
    try:
        from translations.admin import TranslationInline #@UnresolvedImport
    except:
        return False

    if hasattr(value, 'opts') and isinstance(value.opts, TranslationInline):
        return True
    return False


@register.filter
def ispopupinline(value):
    """
    This filter is used if yawd-translations is installed.
    """
    if hasattr(value, 'opts') and isinstance(value.opts, PopupInline):
        return True
    return False


@register.filter
def popup_change_url(formset, obj_id):
    """
    Used in PopupInline
    """
    if isinstance(formset, PopupInlineFormSet):
        return formset.get_change_url(obj_id)


@register.filter
def popup_delete_url(formset, obj_id):
    if isinstance(formset, PopupInlineFormSet):
        return formset.get_delete_url(obj_id)


@register.filter
def fix_collapse(classes):
    return classes.replace('collapse', '')


@register.filter
def indexof_non_hidden(fields):
    """
    Used in TabularInline
    """
    for index, field in enumerate(fields):
        if not hasattr(field, 'widget') or not field.widget.is_hidden:
            return index
