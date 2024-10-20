from urllib.parse import urlencode
import requests


BASE_URL = 'https://harmonogramy.dsw.edu.pl/'
SCHEDULES_URL = 'Plany/PlanyTokow/{id}'
SCHEDULES_SET_DATE_RANGE_URL = 'Plany/PlanyTokowGridCustom/{id}'
ICAL_URL = 'Plany/WydrukTokuical/{id}'


def generate_url(path: str = '', params: dict | None = None, queryParams: dict | None = None):
    """
    Generate a URL with the specified path, params and query parameters.
    """
    url = BASE_URL + path

    if params:
        url = url.format(**params)

    if queryParams:
        url = '{}?{}'.format(url, urlencode(queryParams))

    return url


def get_schedule_ical(group_id: str, start_date: str, end_date: str) -> str:
    """
    Fetch the schedule for the specified group and date range.
    """
    schedules_url = generate_url(SCHEDULES_URL, {'id': group_id})
    schedules_set_date_range_url = generate_url(SCHEDULES_SET_DATE_RANGE_URL, {'id': group_id})
    schedules_set_date_range_data = {
        'DXCallbackName': 'gridViewPlanyTokow',
        'parametry': f'{start_date};{end_date};5;{group_id}',
        'id': group_id,
    }
    schedules_ical_url = generate_url(ICAL_URL, {'id': group_id}, {'dO': start_date, 'dD': end_date})

    with requests.Session() as session:
        # The requested date range is stored in the server session
        # Simulate loading the schedules page and setting the date range
        # This is necessary to generate iCal with the correct date range

        # Load schedules page to aquire session cookie
        response = session.get(schedules_url)

        print(response.status_code, session.cookies)

        session_cookie = session.cookies.get_dict().get('ASP.NET_SessionId')
        if session_cookie:
            print(f'Aquired session: {session_cookie}')
        else:
            exit('Failed to aquire server session')

        # Simulate setting the date range
        response = session.post(schedules_set_date_range_url, data=schedules_set_date_range_data)
        if response.status_code != 200:
            exit('Failed to set date range')

        # Fetch the schedule in iCal format
        response = session.get(schedules_ical_url)
        if response.status_code != 200:
            exit('Failed to fetch schedule')

        return response.text
