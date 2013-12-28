from oauth2client.client import flow_from_clientsecrets
from django.conf import settings


ADMIN_GOOGLE_ANALYTICS = {
    'client_secrets' : '',
    'token_file_name' : '',
    'profile_id' : '',
    'admin_root_url' : 'http://localhost:8000/admin/',
    'interval' : 30 #how many days back should we look for data?
}


try:
    ADMIN_GOOGLE_ANALYTICS.update(settings.ADMIN_GOOGLE_ANALYTICS)
except AttributeError:
    pass


if ADMIN_GOOGLE_ANALYTICS['client_secrets'] and ADMIN_GOOGLE_ANALYTICS['profile_id'] and ADMIN_GOOGLE_ANALYTICS['token_file_name']:
    ADMIN_GOOGLE_ANALYTICS_FLOW = flow_from_clientsecrets( ADMIN_GOOGLE_ANALYTICS['client_secrets'],
        scope='https://www.googleapis.com/auth/analytics.readonly', redirect_uri='%soauth2callback/' % (
        ADMIN_GOOGLE_ANALYTICS['admin_root_url']))
    #always prompt for authentication
    ADMIN_GOOGLE_ANALYTICS_FLOW.params['approval_prompt'] = 'force'
else:
    ADMIN_GOOGLE_ANALYTICS_FLOW = None


ADMIN_USER_MODELFORM = getattr(settings, 'ADMIN_USER_MODELFORM',
    'yawdadmin.admin_forms.AdminUserModelForm')


#load the modelform if it's a string
if isinstance(ADMIN_USER_MODELFORM, str):
    from django.utils.importlib import import_module
    _user_modelform_split = ADMIN_USER_MODELFORM.split('.')
    _user_modelform_module = import_module('.'.join(_user_modelform_split[:-1]))
    ADMIN_USER_MODELFORM = getattr(_user_modelform_module, _user_modelform_split[-1])


ADMIN_CACHE_DB_OPTIONS = getattr(settings, 'ADMIN_CACHE_DB_OPTIONS', 3600)
