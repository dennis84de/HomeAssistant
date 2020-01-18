# """
# Creates a sensor that creates sensors for phonebooks.
# """
import asyncio
import logging
import json
import voluptuous as vol

from homeassistant.core import callback

from homeassistant.components.sensor import (
    ENTITY_ID_FORMAT,
    PLATFORM_SCHEMA,
    DEVICE_CLASSES_SCHEMA,
)

from homeassistant.const import (
    ATTR_FRIENDLY_NAME,
    ATTR_ENTITY_ID,
    CONF_SENSORS,
    EVENT_HOMEASSISTANT_START,
    STATE_UNKNOWN
)

from homeassistant.exceptions import TemplateError
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity, async_generate_entity_id
from homeassistant.helpers.event import async_track_state_change
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers import template as template_helper
from datetime import datetime

__version__ = '1.0.0'

_LOGGER = logging.getLogger(__name__)

SENSOR_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_id,
        vol.Optional(ATTR_FRIENDLY_NAME): cv.string,       
    }
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {vol.Required(CONF_SENSORS): cv.schema_with_slug_keys(SENSOR_SCHEMA)}
)

@asyncio.coroutine
def async_setup_platform(hass, config, async_add_devices, discovery_info=None):
    """Set up the attributes sensors."""
    _LOGGER.info("Setting up phonebook sensor")
    sensors = []

    """Load data from json file"""
    database = '/home/homeassistant/.homeassistant/www/werbeanrufe/liste.json'
    data = json.loads(open(database).read())

    phonebookData = {}

    _LOGGER.info("Loading phonebook data from json file")

    for i in data:
        callername = i['callername'] if 'callername' in i else i['number']
          
        _LOGGER.debug("Adding number %s to phonebook", i['number'])
        phonebookData[i['number']] = callername

    for device, device_config in config[CONF_SENSORS].items():

        entity_id = device_config.get(ATTR_ENTITY_ID)
        friendly_name = device_config.get(ATTR_FRIENDLY_NAME, device)

        state_template = ("{{% if states('{0}') != '{1}' %}}\
                          {{{{ states.{0}.state }}}}\
                          {{% else %}} {1} {{% endif %}}").format(
            entity_id, STATE_UNKNOWN)

        _LOGGER.info("Adding phonebook sensor %s", device)

        state_template = template_helper.Template(state_template)
        state_template.hass = hass

        sensors.append(
            PhonebookSensor(
                hass,
                phonebookData,
                device,
                friendly_name,
                state_template,
                entity_id)
        )

    if not sensors:
        _LOGGER.warning("No phonebook sensors added")
        return False

    async_add_devices(sensors)
    return True


class PhonebookSensor(RestoreEntity):
    """Representation of a phonebook sensor."""

    def __init__(self, hass, phonebookData, device_id, friendly_name,
                 state_template, entity_id):
        """Initialize the sensor."""
        self.hass = hass
        self.entity_id = async_generate_entity_id(ENTITY_ID_FORMAT, device_id,
                                                  hass=hass)
        self._name = friendly_name
        self._template = state_template
        self._state = None        
        self._icon = 'mdi:phone'
        self._entity = entity_id
        self._data = phonebookData

    @asyncio.coroutine
    def async_added_to_hass(self):
        """Register callbacks."""
        state = yield from self.async_get_last_state()
        if state:
            self._state = state.state

        @callback
        def template_sensor_state_listener(entity, old_state, new_state):
            """Handle device state changes."""
            self.hass.async_add_job(self.async_update_ha_state(True))

        @callback
        def template_sensor_startup(event):
            """Update on startup."""
            async_track_state_change(
                self.hass, self._entity, template_sensor_state_listener)

            self.hass.async_add_job(self.async_update_ha_state(True))

        self.hass.bus.async_listen_once(
            EVENT_HOMEASSISTANT_START, template_sensor_startup)

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        entity_state = self.hass.states.get(self._entity)
        last_updated = datetime.now()

        if entity_state is None:
            number_value = None
        else:
            number_value = entity_state.state

        return {
            'number': number_value,
            'last_updated': last_updated,
        }

    @property
    def icon(self):
        """Return the icon to use in the frontend, if any."""
        return self._icon

    @property
    def should_poll(self):
        """No polling needed."""
        return False

    @asyncio.coroutine
    def async_update(self):
        """Update the state from the template and the friendly name."""

        entity_state = self.hass.states.get(self._entity)

        _LOGGER.debug('Set entity state for number %s', entity_state.state)

        try:
            if entity_state.state in self._data.keys():
                caller_name = self._data[entity_state.state]

                if caller_name is None or caller_name == '':
                    caller_name = 'Unbekannter Anrufer'

                self._state = caller_name
                _LOGGER.debug('Found entry  in json data')
            else:
              self._state = STATE_UNKNOWN

        except TemplateError as ex:
            if ex.args and ex.args[0].startswith(
                    "UndefinedError: 'None' has no state"):
                # Common during HA startup - so just a warning
                _LOGGER.warning('Could not render phonebook sensor for %s,'
                                ' the state is unknown.', self._entity)
                return
            self._state = None
            _LOGGER.error('Could not attribute sensor for %s: %s',
                          self._entity, ex)