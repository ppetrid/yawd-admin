import datetime
import json
import time
from oauth2client.client import AccessTokenRefreshError
from django.core.cache import cache
from django.utils.translation import get_language
from django.utils.encoding import force_str
from yawdadmin import admin_site
from conf import settings as ls
from models import AppOption


def get_option_cache_key(optionset_label):
    return 'yawdadmin_options_%s' % optionset_label


def get_option(optionset_label, name, current_only=True, as_stored=False):
    """
    Return the value of an option. The ``current only`` kwarg affects
    only language-dependant options and decides whether to return its value
    for all languages or only the current language.
    """
    #Hit the cache
    optionset = get_options(optionset_label, current_only, as_stored)
    if name in optionset:
        return optionset[name]
    return None

def get_options(optionset_label, current_only=True, as_stored=False):
    """
    Return all options for this app_label as dictionary with the option name
    being the key. 
    """
    #Hit the cache
    cached = {}
    if ls.ADMIN_CACHE_DB_OPTIONS:
        cached = cache.get(get_option_cache_key(optionset_label), {})

    if cached:
        options = cached
    else:
        options = AppOption.objects.filter(optionset_label=optionset_label)
        if ls.ADMIN_CACHE_DB_OPTIONS:
            cache.set(get_option_cache_key(optionset_label), options,
                  ls.ADMIN_CACHE_DB_OPTIONS)

    optionset_admin = admin_site.get_optionset_admin(optionset_label)

    option_dict = {}
    for option in options:
        option_dict[force_str(option.name)] = get_option_value(optionset_admin,
                                                               option,
                                                               current_only,
                                                               as_stored)
    return option_dict


def get_option_value(optionset_admin, db_option, current_only, as_stored):
    """
    Given an AppOption object, return its value for the current language.
    """
    if not db_option:
        return None

    name = force_str(db_option.name)
    if not name in optionset_admin.options:
        return None

    field = optionset_admin.options[name]

    if not db_option.lang_dependant:
        if as_stored:
            return db_option.value
        return field.to_python(db_option.value) if db_option.value else ''

    value_dict = {}
    for key, value in json.loads(db_option.value).items():
        value_dict[force_str(key)] = value

    if current_only:
        curr_lang = get_language()
        if curr_lang in value_dict:
            if as_stored:
                return value_dict[curr_lang]
            return field.to_python(value_dict[curr_lang]) if value_dict[curr_lang] else ''
    else:
        for key in value_dict:
            value_dict[key] = field.to_python(value_dict[key]) if as_stored else \
                                                                    value_dict[key]
            return value_dict


def get_analytics_data(http):
    
    #try to get cached data
    data = cache.get('yawdadmin_ga', None)
    if data:
        return data

    from apiclient.discovery import build
    from apiclient.errors import HttpError

    end_date = datetime.datetime.now()
    start_date = end_date + datetime.timedelta(-ls.ADMIN_GOOGLE_ANALYTICS['interval'])

    try:
        service = build('analytics', 'v3', http=http)
        pie_data = service.data().ga()\
            .get(ids = 'ga:' + ls.ADMIN_GOOGLE_ANALYTICS['profile_id'],
                 start_date = start_date.strftime('%Y-%m-%d'),
                 end_date = end_date.strftime('%Y-%m-%d'),
                 metrics='ga:visits',
                 dimensions='ga:date,ga:visitorType').execute()

        summed_data = service.data().ga()\
            .get(ids = 'ga:' + ls.ADMIN_GOOGLE_ANALYTICS['profile_id'],
                 start_date = start_date.strftime('%Y-%m-%d'), end_date = end_date.strftime('%Y-%m-%d'),
                 metrics='ga:pageviews, ga:visitors, ga:avgTimeOnSite, '
                 'ga:entranceBounceRate, ga:percentNewVisits').execute()

    except HttpError as e:
        return {'error': e.resp.reason}
    except AccessTokenRefreshError:
        return {'error': 'refresh'}

    if not 'rows' in summed_data:
        return {'error':  'empty'}

    data = {
        'summed': {
            'visits': pie_data['totalsForAllResults']['ga:visits'],
            'pageviews': summed_data['rows'][0][0],
            'visitors': summed_data['rows'][0][1],
            'avg_time': time.strftime('%H:%M:%S', time.gmtime(float(summed_data['rows'][0][2]))),
            'bounce_rate': round(float(summed_data['rows'][0][3]), 2),
            'new_visits': round(float(summed_data['rows'][0][4]), 2),
        },
        'chart': _extract_chart_data(pie_data, start_date, end_date)
    }

    cache.set('yawdadmin_ga', data, 3600)
    return data


def _extract_chart_data(pie_data, start_date, end_date):
    """
    Format the Google Analytics data for use within an Area Chart.
    """

    def update_record(record):
        visits = 0
        for key in ('new','returning'):
            if not key in record:
                record[key] = 0
            visits += record[key]
        record['total'] = visits

    date = start_date
    current_row = date.strftime('%Y%m%d')
    data = [{ 'date': date.strftime('%A, %B %d, %Y')}]

    #calculate chart-ready data
    for row in pie_data['rows']:
        while row[0] != current_row:
            update_record(data[len(data)-1])
            date = date + datetime.timedelta(1)
            data.append({'date': date.strftime('%A, %B %d, %Y')})
            current_row = date.strftime('%Y%m%d')

        if row[1] == 'New Visitor':
            data[len(data)-1]['new'] = int(row[2])
        else:
            data[len(data)-1]['returning'] = int(row[2])

    update_record(data[len(data)-1])

    return data
