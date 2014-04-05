__version__ = '0.7.1-rc1'

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module
from yawdadmin.sites import YawdAdminSite


def _get_site():
    yawdadmin_site = getattr(settings, 'ADMIN_SITE', YawdAdminSite)
    if isinstance(yawdadmin_site, str):
        yawdadmin_site_split = yawdadmin_site.split('.')
        yawdadmin_site_module = import_module('.'.join(yawdadmin_site_split[:-1]))
        return getattr(yawdadmin_site_module, yawdadmin_site_split[-1])
    return yawdadmin_site


admin_site = _get_site()()


if not isinstance(admin_site, YawdAdminSite):
    raise ImproperlyConfigured('The specified admin site is not a subclass of '\
                               'yawdadmin.sites.YawdAdminSite')
