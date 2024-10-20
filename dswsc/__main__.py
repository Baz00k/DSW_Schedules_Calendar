from datetime import datetime, timedelta

from .config import settings
from .schedules import get_schedule_ical
from .google_calendar import clear_event_from_date, add_events_to_google_calendar


def main():
    start_date = datetime.now()
    end_date = (datetime.now() + timedelta(weeks=settings.date_range))

    schedule_ical = get_schedule_ical(settings.group_id, start_date.strftime(settings.date_format), end_date.strftime(settings.date_format))
    clear_event_from_date(settings.google_calendar_id, start_date)
    add_events_to_google_calendar(schedule_ical, settings.google_calendar_id)

    print('Successfully added events to Google Calendar!')


if __name__ == '__main__':
    main()
