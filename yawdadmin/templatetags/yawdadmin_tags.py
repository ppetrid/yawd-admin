import re
from django import template
from django.conf import settings
from django.core import urlresolvers
from yawdadmin import admin_site

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
        'LANGUAGE_CODE' : context['LANGUAGE_CODE'],
        'optionset_labels' : admin_site.get_option_admin_urls() 
    }

@register.simple_tag
def clean_media(media):
    media._js = [i for i in media._js if not re.match(
        r'%sadmin/js/((jquery(\.init)?|collapse|admin/RelatedObjectLookups)(\.min)?\.)js' % settings.STATIC_URL, i)]
    return media
