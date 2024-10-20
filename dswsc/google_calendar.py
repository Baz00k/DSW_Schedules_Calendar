import json
from datetime import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from icalendar import Calendar

from .config import settings

SCOPES = ['https://www.googleapis.com/auth/calendar']
TIMEZONE = 'Europe/Warsaw'

def authenticate_google_calendar():
    """
    Authenticate with Google Calendar using service account credentials.
    """
    service_account_info = json.loads(settings.google_service_account_key)
    creds = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
    return creds

def clear_event_from_date(calendar_id: str, date: datetime):
    """
    Clear all future events from the specified date in the Google Calendar.
    """
    creds = authenticate_google_calendar()
    service = build('calendar', 'v3', credentials=creds)

    date_formatted = date.isoformat() + 'Z'
    events_result = service.events().list(calendarId=calendar_id, timeMin=date_formatted).execute()
    events = events_result.get('items', [])

    for event in events:
        service.events().delete(calendarId=calendar_id, eventId=event['id']).execute()
        print(f'Event deleted: {event["id"]}')

def add_events_to_google_calendar(schedule_ical: str, calendar_id: str):
    """
    Add events from the iCal data to the specified Google Calendar.
    """
    creds = authenticate_google_calendar()
    service = build('calendar', 'v3', credentials=creds)

    cal = Calendar.from_ical(schedule_ical)
    for component in cal.walk():
        if component.name == "VEVENT":
            event = {
                'summary': str(component.get('summary')),
                'location': str(component.get('location')),
                'description': str(component.get('description')),
                'start': {
                    'dateTime': component.get('dtstart').dt.isoformat(),
                    'timeZone': TIMEZONE,
                },
                'end': {
                    'dateTime': component.get('dtend').dt.isoformat(),
                    'timeZone': TIMEZONE,
                },
            }

            created_event = service.events().insert(calendarId=calendar_id, body=event).execute()
            print(f'Event created: {created_event.get("htmlLink")}')
