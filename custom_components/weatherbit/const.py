"""Constants in weatherbit component."""

ATTR_ALERTS = "alerts"
ATTR_ALERTS_CITY_NAME = "city_name"
ATTR_ALERT_DESCRIPTION_EN = "description_english"
ATTR_ALERT_DESCRIPTION_LOC = "description_local"
ATTR_ALERT_EFFECTIVE = "effective"
ATTR_ALERT_ENDS = "ends"
ATTR_ALERT_EXPIRES = "expires"
ATTR_ALERT_ONSET = "onset"
ATTR_ALERT_REGIONS = "regions"
ATTR_ALERT_SEVERITY = "severity"
ATTR_ALERT_TITLE = "title"
ATTR_ALERT_URI = "uri"
ATTR_ALT_CONDITION = "alt_condition"
ATTR_AQI_LEVEL = "aqi_level"
ATTR_FORECAST_CLOUDINESS = "cloudiness"
ATTR_FORECAST_SNOW = "snow"
ATTR_FORECAST_WEATHER_TEXT = "weather_text"

CONF_INTERVAL_SENSORS = "update_interval"
CONF_INTERVAL_FORECAST = "forecast_interval"
CONF_FORECAST_LANGUAGE = "forecast_language"
CONFIG_OPTIONS = [
    CONF_FORECAST_LANGUAGE,
    CONF_INTERVAL_FORECAST,
    CONF_INTERVAL_SENSORS,
]
CONF_UNIT_SYSTEM_IMPERIAL = "imperial"
CONF_UNIT_SYSTEM_METRIC = "metric"

DEFAULT_ATTRIBUTION = "Powered by Weatherbit.io"
DEFAULT_INTERVAL_SENSORS = 60
DEFAULT_INTERVAL_FORECAST = 60
DEFAULT_BRAND = "Weatherbit.io"
DEFAULT_FORECAST_LANGUAGE = "en"

DOMAIN = "weatherbit"

TRANSLATION_BEAUFORT = "beaufort"
TRANSLATION_CARDINAL = "wind_cardinal"
TRANSLATION_UV_DESCRIPTION = "uv_description"

WEATHERBIT_API_VERSION = "2.0"
WEATHERBIT_PLATFORMS = [
    "weather",
    "sensor",
]
