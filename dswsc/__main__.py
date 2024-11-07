from datetime import datetime, timedelta

from .config import settings
from .schedules import get_schedule_ical
from .events import parse_ical_to_events
from .cache import load_events_cache, save_events_cache, events_to_hash, string_to_hash
from .google_calendar import clear_event_from_date, add_events_to_google_calendar


def main():
    start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = (datetime.now() + timedelta(weeks=settings.date_range))

    schedule_ical = get_schedule_ical(settings.group_id, start_date.strftime(settings.date_format), end_date.strftime(settings.date_format))
    events = parse_ical_to_events(schedule_ical)
    
    if len(events) == 0:
        print('Empty schedule, nothing to sync!')
        return
    
    if not settings.ignore_cache:
        try:
            cache = load_events_cache(settings.group_id)
        except Exception:
            print('Invalid cache, ignoring...')
            cache = None
            
        if cache and events_to_hash(events) == string_to_hash(cache):
            print('No changes in schedule, skipping sync!')
            return
    
    if settings.dry_run:
        print('Dry run, skipping sync!')
    else:
        clear_event_from_date(settings.google_calendar_id, start_date)
        add_events_to_google_calendar(events, settings.google_calendar_id)
        
    save_events_cache(settings.group_id, events)

    print('Sync complete!')

if __name__ == '__main__':
    main()
