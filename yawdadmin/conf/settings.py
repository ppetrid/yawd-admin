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

ADMIN_GOOGLE_ANALYTICS_FLOW = flow_from_clientsecrets( ADMIN_GOOGLE_ANALYTICS['client_secrets'],
        scope='https://www.googleapis.com/auth/analytics.readonly', redirect_uri='%soauth2callback/' % (
        ADMIN_GOOGLE_ANALYTICS['admin_root_url'])) if ADMIN_GOOGLE_ANALYTICS['client_secrets'] and ADMIN_GOOGLE_ANALYTICS['profile_id'] and ADMIN_GOOGLE_ANALYTICS['token_file_name'] else None