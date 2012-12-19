import re
from django import template
from django.conf import settings
from django.core import urlresolvers
from django.contrib.admin.views.main import PAGE_VAR
from django.utils.safestring import mark_safe
from django.utils.translation import get_language
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