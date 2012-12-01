# -*- coding: utf-8 -*-
from django import template

register = template.Library()

@register.filter
def divide(value, num):
    return int(value / num)

@register.filter
def app_title(value):
    return value.replace('_',' ')

@register.filter
def utfupper(value):
    orig = [u'Ά', u'Έ', u'Ή', u'Ί', u'Ό', u'Ύ', u'Ώ']
    rep = [u'Α', u'Ε', u'Η', u'Ι', u'Ο', u'Υ', u'Ω']
    return u''.join([rep[orig.index(x)] if x in orig else x for x in value.upper()])
        