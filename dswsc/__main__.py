from datetime import datetime, timedelta

from .config import settings
from .schedules import get_schedule_ical
from .events import parse_ical_to_events
from .google_calendar import clear_event_from_date, add_events_to_google_calendar


def main():
    start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = (datetime.now() + timedelta(weeks=settings.date_range))

    schedule_ical = get_schedule_ical(settings.group_id, start_date.strftime(settings.date_format), end_date.strftime(settings.date_format))
    clear_event_from_date(settings.google_calendar_id, start_date)
    
    events = parse_ical_to_events(schedule_ical)
    add_events_to_google_calendar(events, settings.google_calendar_id)

    print('Sync complete!')

if __name__ == '__main__':
    main()
