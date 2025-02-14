from pydantic import Field, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        cli_parse_args=True, env_file=".env", env_file_encoding="utf-8"
    )

    group_id: str = Field(
        alias="GROUP_ID",
        description="ID of the group to fetch the schedule for",
        examples=["995"],
    )
    date_range: int = Field(
        alias="DATE_RANGE",
        description="Number of weeks to fetch the schedule for",
        default=4,
        examples=[4],
    )
    google_calendar_id: str = Field(
        alias="GOOGLE_CALENDAR_ID",
        description="ID of the Google Calendar to add events to",
    )
    google_service_account_key: str = Field(
        alias="GOOGLE_SERVICE_ACCOUNT_KEY",
        description="Service account key for Google Calendar API",
    )

    cache_dir: str = Field(
        alias="CACHE_DIR", description="Directory to store the cache", default=".cache"
    )
    cache_file_template: str = Field(
        alias="CACHE_FILE_TEMPLATE",
        description="Template for the cache file",
        default="{group_id}",
    )
    ignore_cache: bool = Field(
        alias="IGNORE_CACHE",
        description="Ignore the cache and always sync the schedule",
        default=False,
    )

    dry_run: bool = Field(
        alias="DRY_RUN", description="Do not modify the Google Calendar", default=False
    )

    date_format: str = "%Y-%m-%d"
    timezone: str = "Europe/Warsaw"


try:
    settings = Settings()
except ValidationError as e:
    exit(f"Invalid configuration: {e}")
