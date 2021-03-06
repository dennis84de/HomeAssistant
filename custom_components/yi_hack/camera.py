"""Support for Xiaomi Cameras: yi-hack-MStar, yi-hack-Allwinner and yi-hack-Allwinner-v2."""

import asyncio
import logging

from haffmpeg.camera import CameraMjpeg
from haffmpeg.tools import IMAGE_JPEG, ImageFrame
import requests
from requests.auth import HTTPBasicAuth
import voluptuous as vol

from homeassistant.components import mqtt
from homeassistant.components.camera import SUPPORT_STREAM, Camera
from homeassistant.components.ffmpeg import CONF_EXTRA_ARGUMENTS, DATA_FFMPEG
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_HOST,
    CONF_MAC,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_USERNAME,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_platform
from homeassistant.helpers.aiohttp_client import async_aiohttp_proxy_stream
from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC

from .const import (
    ALLWINNER,
    ALLWINNERV2,
    CONF_HACK_NAME,
    CONF_MQTT_PREFIX,
    CONF_PTZ,
    CONF_SERIAL,
    CONF_TOPIC_MOTION_DETECTION_IMAGE,
    DEFAULT_BRAND,
    DOMAIN,
    HTTP_TIMEOUT,
    LINK_HIGH_RES_STREAM,
    LINK_LOW_RES_STREAM,
    MSTAR,
    SERVICE_PTZ,
    SERVICE_SPEAK,
)

_LOGGER = logging.getLogger(__name__)

DIR_UP = "up"
DIR_DOWN = "down"
DIR_LEFT = "left"
DIR_RIGHT = "right"
ATTR_MOVEMENT = "movement"
ATTR_TRAVELTIME = "travel_time"
DEFAULT_TRAVELTIME = 0.3

LANG_DE = "de-DE"
LANG_GB = "en-GB"
LANG_US = "en-US"
LANG_ES = "es-ES"
LANG_FR = "fr-FR"
LANG_IT = "it-IT"
ATTR_LANGUAGE = "language"
ATTR_GENDER = "gender"
ATTR_SENTENCE = "sentence"
DEFAULT_LANGUAGE = "en-US"
DEFAULT_SENTENCE = ""

ICON = "mdi:camera"


async def async_setup_entry(hass: HomeAssistant, config: ConfigEntry, async_add_entities):
    """Set up a Yi Camera."""

    platform = entity_platform.current_platform.get()
    platform.async_register_entity_service(
        SERVICE_PTZ,
        {
            vol.Required(ATTR_MOVEMENT): vol.In(
                [
                    DIR_UP,
                    DIR_DOWN,
                    DIR_LEFT,
                    DIR_RIGHT,
                ]
            ),
            vol.Optional(ATTR_TRAVELTIME, default=DEFAULT_TRAVELTIME): vol.Coerce(float),
        },
        "async_perform_ptz",
    )

    if (config.data[CONF_HACK_NAME] == MSTAR) or (config.data[CONF_HACK_NAME] == ALLWINNER) or (config.data[CONF_HACK_NAME] == ALLWINNERV2):
        platform.async_register_entity_service(
            SERVICE_SPEAK,
            {
                vol.Required(ATTR_LANGUAGE, default=DEFAULT_LANGUAGE): vol.In(
                    [
                        LANG_DE,
                        LANG_GB,
                        LANG_US,
                        LANG_ES,
                        LANG_FR,
                        LANG_IT,
                    ]
                ),
                vol.Required(ATTR_SENTENCE, default=DEFAULT_SENTENCE): str,
            },
            "async_perform_speak",
        )

    async_add_entities(
        [
            YiHackCamera(hass, config),
            YiHackMqttCamera(hass, config)
        ],
        True
    )


class YiHackCamera(Camera):
    """Define an implementation of a Yi Camera."""

    def __init__(self, hass, config):
        """Initialize."""
        super().__init__()

        self._extra_arguments = config.data[CONF_EXTRA_ARGUMENTS]
        self._manager = hass.data[DATA_FFMPEG]
        self._device_name = config.data[CONF_NAME]
        self._name = self._device_name + "_cam"
        self._unique_id = self._device_name + "_caca"
        self._mac = config.data[CONF_MAC]
        self._serial_number = config.data[CONF_SERIAL]
        self._is_on = True
        self._host = config.data[CONF_HOST]
        self._port = config.data[CONF_PORT]
        self._user = config.data[CONF_USERNAME]
        self._password = config.data[CONF_PASSWORD]
        self._ptz = config.data[CONF_PTZ]

        self._http_base_url = "http://" + self._host
        if self._port != 80:
            self._http_base_url += ":" + self._port
        self._still_image_url = self._http_base_url + "/cgi-bin/snapshot.sh?res=high&watermark=yes"

    @property
    def supported_features(self) -> int:
        """Return supported features."""
        return SUPPORT_STREAM

    async def stream_source(self) -> str:
        """Return the stream source."""
        def fetch_link():
            """Get URL from camera available links."""
            auth = None
            if self._user or self._password:
                auth = HTTPBasicAuth(self._user, self._password)

            try:
                response = requests.get(self._http_base_url + "/cgi-bin/links.sh",
                                        timeout=HTTP_TIMEOUT, auth=auth)
                if response.status_code < 300:
                    links: dict = response.json()
                    stream_source: str = links.get(LINK_HIGH_RES_STREAM) or links.get(LINK_LOW_RES_STREAM)
                    if self._user or self._password:
                        stream_source = stream_source.replace(
                            "rtsp://", f"rtsp://{self._user}:{self._password}@", 1
                        )

                    return stream_source

            except requests.exceptions.RequestException as error:
                _LOGGER.error(
                    "Error getting stream link from %s: %s",
                    self._name,
                    error,
                )

            return None

        return await self.hass.async_add_executor_job(fetch_link)

    async def async_camera_image(self):
        """Return a still image response from the camera."""
        image = None

        if self._still_image_url:
            auth = None
            if self._user or self._password:
                auth = HTTPBasicAuth(self._user, self._password)

            def fetch():
                """Read image from a URL."""
                try:
                    response = requests.get(self._still_image_url, timeout=HTTP_TIMEOUT, auth=auth)
                    if response.status_code < 300:
                        return response.content
                except requests.exceptions.RequestException as error:
                    _LOGGER.error(
                        "Fetch snapshot image failed from %s, falling back to FFmpeg; %s",
                        self._name,
                        error,
                    )

                return None

            image = await self.hass.async_add_executor_job(fetch)

        if image is None:
            stream_source = await self.stream_source()
            if stream_source:
                ffmpeg = ImageFrame(self.hass.data[DATA_FFMPEG].binary)
                image = await asyncio.shield(
                    ffmpeg.get_image(
                        stream_source,
                        output_format=IMAGE_JPEG,
                        extra_cmd=self._extra_arguments
                    )
                )

        return image

    async def handle_async_mjpeg_stream(self, request):
        """Generate an HTTP MJPEG stream from the camera."""
        _LOGGER.debug("Handling mjpeg stream from camera '%s'", self._name)

        stream_source = await self.stream_source()
        if not stream_source:
            return super().handle_async_mjpeg_stream(request)

        stream = CameraMjpeg(self._manager.binary)
        await stream.open_camera(
            stream_source,
            extra_cmd=self._extra_arguments
        )

        try:
            stream_reader = await stream.get_reader()
            return await async_aiohttp_proxy_stream(
                self.hass,
                request,
                stream_reader,
                self._manager.ffmpeg_stream_content_type,
            )
        finally:
            await stream.close()

    def _perform_ptz(self, movement, travel_time_str):
        auth = None
        if self._user or self._password:
            auth = HTTPBasicAuth(self._user, self._password)

        try:
            response = requests.get("http://" + self._host + ":" + self._port + "/cgi-bin/ptz.sh?dir=" + movement + "&time=" + travel_time_str, timeout=HTTP_TIMEOUT, auth=auth)
            if response.status_code >= 300:
                _LOGGER.error("Failed to send ptz command to device %s", self._host)
        except requests.exceptions.RequestException as error:
            _LOGGER.error("Failed to send ptz command to device %s: error %s", self._host, error)

    async def async_perform_ptz(self, movement, travel_time):
        """Perform a PTZ action on the camera."""
        _LOGGER.debug("PTZ action '%s' on %s", movement, self._name)

        if self._ptz == "no":
            _LOGGER.error("PTZ is not available on %s", self._name)
            return

        try:
            travel_time_str = str(travel_time)
        except ValueError:
            travel_time_str = str(DEFAULT_TRAVELTIME)

        await self.hass.async_add_executor_job(self._perform_ptz, movement, travel_time_str)

    def _perform_speak(self, language, sentence):
        auth = None
        if self._user or self._password:
            auth = HTTPBasicAuth(self._user, self._password)

        try:
            response = requests.post("http://" + self._host + ":" + self._port + "/cgi-bin/speak.sh?lang=" + language, data=sentence, timeout=HTTP_TIMEOUT, auth=auth)
            if response.status_code >= 300:
                _LOGGER.error("Failed to send speak command to device %s", self._host)
        except requests.exceptions.RequestException as error:
            _LOGGER.error("Failed to send speak command to device %s: error %s", self._host, error)

        if response is not None:
            try:
                if response.json()["error"] == "true":
                    _LOGGER.error("Failed to send speak command to device %s: error %s", self._host, response.json()["description"])
            except KeyError:
                _LOGGER.error("Failed to send speak command to device %s: error unknown", self._host)
        else:
            _LOGGER.error("Failed to send speak command to device %s: error unknown", self._host)

    async def async_perform_speak(self, language, sentence):
        """Perform a SPEAK action on the camera."""
        _LOGGER.debug("SPEAK action on %s", self._name)

        await self.hass.async_add_executor_job(self._perform_speak, language, sentence)

    @property
    def brand(self):
        """Camera brand."""
        return DEFAULT_BRAND

    @property
    def name(self):
        """Return the name of the camera."""
        return self._name

    @property
    def is_on(self):
        """Determine whether the camera is on."""
        return self._is_on

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._unique_id

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        return ICON

    @property
    def device_info(self):
        """Return device specific attributes."""
        return {
            "name": self._device_name,
            "connections": {(CONNECTION_NETWORK_MAC, self._mac)},
            "identifiers": {(DOMAIN, self._serial_number)},
            "manufacturer": DEFAULT_BRAND,
            "model": DOMAIN,
        }


class YiHackMqttCamera(Camera):
    """representation of a MQTT camera."""

    def __init__(self, hass: HomeAssistant, config):
        """Initialize the MQTT Camera."""
        super().__init__()

        self._hass = hass
        self._device_name = config.data[CONF_NAME]
        self._name = self._device_name  + "_motion_detection_cam"
        self._unique_id = self._device_name + "_camd"
        self._mac = config.data[CONF_MAC]
        self._serial_number = config.data[CONF_SERIAL]
        self._is_on = True
        self._state_topic = config.data[CONF_MQTT_PREFIX] + "/" + config.data[CONF_TOPIC_MOTION_DETECTION_IMAGE]
        self._last_image = None
        self._mqtt_subscription = None

    async def async_added_to_hass(self):
        """Subscribe to MQTT events."""

        @callback
        def message_received(msg):
            """Handle new MQTT messages."""
            data = msg.payload

            self._last_image = data

        self._mqtt_subscription = await mqtt.async_subscribe(
            self.hass, self._state_topic, message_received, 1, None
        )

    async def async_will_remove_from_hass(self):
        """Unsubscribe from MQTT events."""
        if self._mqtt_subscription:
            self._mqtt_subscription()

    async def async_camera_image(self):
        """Return image response."""
        return self._last_image

    @property
    def brand(self):
        """Camera brand."""
        return DEFAULT_BRAND

    @property
    def name(self):
        """Return the name of the camera."""
        return self._name

    @property
    def is_on(self):
        """Determine whether the camera is on."""
        return self._is_on

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._unique_id

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        return ICON

    @property
    def device_info(self):
        """Return device specific attributes."""
        return {
            "name": self._device_name,
            "connections": {(CONNECTION_NETWORK_MAC, self._mac)},
            "identifiers": {(DOMAIN, self._serial_number)},
            "manufacturer": DEFAULT_BRAND,
            "model": DOMAIN,
        }
