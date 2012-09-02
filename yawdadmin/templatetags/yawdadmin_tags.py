from django import template
from django.core import urlresolvers
from yawdadmin import admin_site

register = template.Library()

def admin_top_menu(context):
    return {
        'top_menu' : admin_site.top_menu(context['request']),
        'homeurl' : urlresolvers.reverse('admin:index'),
        'user' : context['user'],
        'langs' : context['langs'] if 'langs' in context else [],
        'default_lang': context['default_lang'] if 'default_lang' in context else None,
        'clean_url' : context['clean_url'] if 'clean_url' in context else '',
        'LANGUAGE_CODE' : context['LANGUAGE_CODE']
    }
register.inclusion_tag('admin/includes/topmenu.html', takes_context=True)(admin_top_menu)
    
    