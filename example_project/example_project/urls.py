from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from yawdadmin import admin_site

admin.autodiscover()
admin_site._registry.update(admin.site._registry)

urlpatterns = patterns('',
    #register the yawd-admin URLs
    url(r'^', include(admin_site.urls)),
)

if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': settings.MEDIA_ROOT, }),
    )
