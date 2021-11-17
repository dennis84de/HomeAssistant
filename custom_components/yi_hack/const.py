"""Constants for yi_hack integration."""

DOMAIN = "yi_hack"

DEFAULT_BRAND = "yi-hack"
DEFAULT_BRAND_R = "yi_hack"

MSTAR = "yi-hack-mstar"
ALLWINNER = "yi-hack-allwinner"
ALLWINNERV2 = "yi-hack-allwinner-v2"
V5 = "yi-hack-v5"
SONOFF = "sonoff-hack"
MSTAR_R = "yi_hack_m"
ALLWINNER_R = "yi_hack_a"
ALLWINNERV2_R = "yi_hack_a2"
V5_R = "yi_hack_v5"
SONOFF_R = "yi_hack_s"

DEFAULT_HOST = ""
DEFAULT_PORT = 8080
DEFAULT_USERNAME = ""
DEFAULT_PASSWORD = ""
DEFAULT_EXTRA_ARGUMENTS = "-rtsp_transport tcp"

SERVICE_PTZ = "ptz"
SERVICE_SPEAK = "speak"

HTTP_TIMEOUT = 10

CONF_HACK_NAME = "HACK_NAME"
CONF_SERIAL = "SERIAL_NUMBER"
CONF_PTZ = "PTZ"
CONF_RTSP_PORT = "RTSP_PORT"
CONF_MAC_ADDRESS = "MAC_ADDRESS"
CONF_MQTT_PREFIX = "MQTT_PREFIX"
CONF_TOPIC_STATUS = "TOPIC_BIRTH_WILL"
CONF_TOPIC_MOTION_DETECTION = "TOPIC_MOTION"
CONF_TOPIC_SOUND_DETECTION = "TOPIC_SOUND_DETECTION"
CONF_TOPIC_BABY_CRYING = "TOPIC_BABY_CRYING"
CONF_TOPIC_MOTION_DETECTION_IMAGE = "TOPIC_MOTION_IMAGE"

CONF_MOTION_START_MSG = "MOTION_START_MSG"
CONF_MOTION_STOP_MSG = "MOTION_STOP_MSG"
CONF_BABY_CRYING_MSG = "BABY_CRYING_MSG"
CONF_BIRTH_MSG = "BIRTH_MSG"
CONF_WILL_MSG = "WILL_MSG"
CONF_SOUND_DETECTION_MSG = "SOUND_DETECTION_MSG"

LINK_LOW_RES_STREAM = "low_res_stream"
LINK_HIGH_RES_STREAM = "high_res_stream"

END_OF_POWER_OFF = "END_OF_POWER_OFF"
END_OF_POWER_ON = "END_OF_POWER_ON"
