"""Constants for the samsungtv_smart integration."""
from enum import Enum


class AppLoadMethod(Enum):
    All = 1
    Default = 2
    NotLoad = 3


APP_LOAD_METHODS = {
    AppLoadMethod.All.value: "All Apps",
    AppLoadMethod.Default.value: "Default Apps",
    AppLoadMethod.NotLoad.value: "Not Load",
}

DOMAIN = "samsungtv_smart"

UPDATE_METHODS = {
    "SmartThings": "smartthings",
    "Ping": "ping",
    "WebSockets": "websockets",
}

RESULT_NOT_SUCCESSFUL = "not_successful"
RESULT_NOT_SUPPORTED = "not_supported"
RESULT_ST_DEVICE_USED = "st_device_used"
RESULT_ST_DEVICE_NOT_FOUND = "st_device_not_found"
RESULT_ST_MULTI_DEVICES = "st_multiple_device"
RESULT_SUCCESS = "success"
RESULT_WRONG_APIKEY = "wrong_api_key"

DEFAULT_PORT = 8001
DEFAULT_TIMEOUT = 5
DEFAULT_UPDATE_METHOD = UPDATE_METHODS["Ping"]
CONF_APP_LIST = "app_list"
CONF_APP_LOAD_METHOD = "app_load_method"
CONF_DEVICE_NAME = "device_name"
CONF_DEVICE_MODEL = "device_model"
CONF_SOURCE_LIST = "source_list"
CONF_SHOW_CHANNEL_NR = "show_channel_number"
CONF_WS_NAME = "ws_name"
CONF_DEVICE_OS = "device_os"
CONF_LOAD_ALL_APPS = "load_all_apps"
CONF_POWER_ON_DELAY = "power_on_delay"
CONF_USE_ST_CHANNEL_INFO = "use_st_channel_info"
CONF_USE_ST_STATUS_INFO = "use_st_status_info"
CONF_USE_MUTE_CHECK = "use_mute_check"
CONF_SYNC_TURN_OFF = "sync_turn_off"
CONF_SYNC_TURN_ON = "sync_turn_on"

# obsolete
CONF_UPDATE_METHOD = "update_method"
CONF_UPDATE_CUSTOM_PING_URL = "update_custom_ping_url"
CONF_SCAN_APP_HTTP = "scan_app_http"

DATA_LISTENER = "listener"
DEFAULT_POWER_ON_DELAY = 30.0

WS_PREFIX = "[Home Assistant]"

DEFAULT_SOURCE_LIST = {"TV": "KEY_TV", "HDMI": "KEY_HDMI"}
DEFAULT_APP = "TV/HDMI"

STD_APP_LIST = {
    # app_id: smartthings app id (if different and available)
    "org.tizen.browser": "",                    #Internet
    "11101200001": "org.tizen.netflix-app",     #Netflix
    "111299001912": "9Ur5IzDKqV.TizenYouTube",  #YouTube
    "3201512006785": "org.tizen.ignition",      #Prime Video
    "3201901017640": "MCmYXNxgcu.DisneyPlus",   #Disney+
    "11091000000": "4ovn894vo9.Facebook",       #Facebook
    "3201601007250": "QizQxC7CUf.PlayMovies",   #Google Play
    "3201606009684": "rJeHak5zRg.Spotify",      #Spotify
}
