import inspect
import re
from django import template
from django.conf import settings
from django.contrib.admin.templatetags.admin_modify import submit_row
from django.contrib.admin.views.main import PAGE_VAR
from django.contrib.admin.util import lookup_field, display_for_field, display_for_value
from django.core import urlresolvers
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.encoding import force_text
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import get_language, ugettext as _
from yawdadmin import admin_site
from yawdadmin.conf import settings as ls


register = template.Library()


@register.inclusion_tag('admin/includes/topmenu.html', takes_context=True)
def admin_top_menu(context):
    return {
        'perms' : context['perms'],
        'top_menu' : admin_site.top_menu(context['request']),
        'homeurl' : urlresolvers.reverse('admin:index'),
        'user' : context['user'],
        'langs' : context['langs'] if 'langs' in context else [],
        'default_lang': context['default_lang'] if 'default_lang' in context else None,
        'clean_url' : context['clean_url'] if 'clean_url' in context else '',
        'LANGUAGE_CODE' : get_language(),
        'optionset_labels' : admin_site.get_option_admin_urls(),
        'analytics' : context['user'].is_superuser and ls.ADMIN_GOOGLE_ANALYTICS_FLOW,
        'request': context['request']
    }


@register.simple_tag
def clean_media(media):
    if hasattr(media, '_js'):
        media._js = [i for i in media._js if not re.match(
            r'%sadmin/js/((jquery(\.init)?|collapse|admin/RelatedObjectLookups)(\.min)?\.)js' % settings.STATIC_URL, i)]
    return media


@register.simple_tag
def yawdadmin_paginator_number(cl,i):
    """
    Generates an individual page index link in a paginated list.
    """
    if i == '.':
        return mark_safe('<li class="disabled"><a href="javascript:void(0);">...</a></li>')
    elif i == cl.page_num:
        return mark_safe('<li class="active"><a href="javascript:void(0);">%s</a></li>' % str(i+1))
    else:
        return '<li><a href="%s"%s>%s</a></li>' % (
                           cl.get_query_string({PAGE_VAR: i}),
                           mark_safe(' class="end"' if i == cl.paginator.num_pages-1 else ''),
                           i+1)


@register.simple_tag(takes_context=True)
def get_admin_site_meta(context):
    context['ADMIN_SITE_NAME'] = getattr(settings, 'ADMIN_SITE_NAME',
        _('Django Administration'))
    context['ADMIN_SITE_DESCRIPTION'] = getattr(settings, 'ADMIN_SITE_DESCRIPTION',
        _('Welcome to the yawd-admin administration page. Please sign in to manage your website.'))
    context['ADMIN_DISABLE_APP_INDEX'] = getattr(settings, 'ADMIN_DISABLE_APP_INDEX', False)
    return ''


@register.simple_tag
def get_admin_logo():
    return getattr(settings, 'ADMIN_SITE_LOGO_HTML', '')


@register.simple_tag
def get_object_icon(obj, default_icon=''):
    try:
        return admin_site._registry[obj if inspect.isclass(obj) else obj.__class__].title_icon
    except:
            return default_icon


@register.simple_tag
def inline_items_for_result(inline, result):
    """
    Generates the actual list of data for the inline.
    """
    list_display = inline.list_display if inline.list_display else ('__unicode__',)
    ret = ''
    for field_name in list_display:
        row_class =  mark_safe(' class="column"')
        try:
            f, attr, value = lookup_field(field_name, result, inline)
        except ObjectDoesNotExist:
            result_repr = ''
        else:
            if f is None:
                allow_tags = getattr(attr, 'allow_tags', False)
                boolean = getattr(attr, 'boolean', False)
                if boolean:
                    allow_tags = True
                result_repr = display_for_value(value, boolean)
                # Strip HTML tags in the resulting text, except if the
                # function has an "allow_tags" attribute set to True.
                if allow_tags:
                    result_repr = mark_safe(result_repr)
            else:
                if isinstance(f.rel, models.ManyToOneRel):
                    field_val = getattr(result, f.name)
                    if field_val is None:
                        result_repr = ''
                    else:
                        result_repr = field_val
                else:
                    result_repr = display_for_field(value, f)
        if force_text(result_repr) == '':
            result_repr = mark_safe('&nbsp;')

        ret += format_html(u'<span{0}>{1}</span>', row_class, result_repr)
    return ret


#TODO: Remove this in future version
@register.simple_tag
def related_lookup_popup_var():
    """
    This templatetag is here to ensure fancybox related lookups
    work for Django 1.6 and older versions. It should be removed
    once support for Django 1.5 is dropped. 
    """
    try: #Django 1.6+
        from django.contrib.admin.options import IS_POPUP_VAR #@UnresolvedImport
    except:
        IS_POPUP_VAR = 'pop'
    return '<script>rel_lookup_popup_var = "%s"</script>' % IS_POPUP_VAR


@register.inclusion_tag('admin/submit_line.html', takes_context=True)
def explicit_submit_row(context, **kwargs):
    """
    This template tag allows disabling buttons explicitly from templates.
    """
    explicit_context = {}
    for option in ('show_delete_link', 'show_save_as_new', 'show_save_and_add_another',
              'show_save_and_continue', 'show_save'):
        if option in kwargs and not kwargs[option] is None:
            explicit_context[option] = kwargs[option]

    original_context = submit_row(context)
    original_context.update(explicit_context)                                                              
    return original_context
