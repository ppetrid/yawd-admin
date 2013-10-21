from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from yawdadmin import admin_site
from demo_application.views import TypeaheadProfessionsView

admin.autodiscover()
admin_site._registry.update(admin.site._registry)

urlpatterns = patterns('',
    #register the yawd-admin URLs
    url(r'^admin/', include(admin_site.urls)),
    url(r'^autocomplete-example/', TypeaheadProfessionsView.as_view(), name='autocomplete-example-view')
)

if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': settings.MEDIA_ROOT, }),
    )
