"""
Get recent calls from fritzbox

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/sensor.fritzbox_calllust/
"""

import logging
from datetime import timedelta
from datetime import datetime
import voluptuous as vol

from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import (
    ENTITY_ID_FORMAT, PLATFORM_SCHEMA)
from homeassistant.const import (
    CONF_HOST, CONF_NAME, CONF_PASSWORD, CONF_USERNAME)
from homeassistant.util import Throttle
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)
REQUIREMENTS = ['fritzconnection==0.6.5']

PLATFORM = 'fritz_calllist'

CONF_MAX_CALLS = 'max_calls'
CONF_DEFAULT_NAME = 'fritz_calllist'
CONF_DEFAULT_IP = '169.254.1.1'
DEFAULT_MAX_CALLS = 5

SCAN_INTERVAL = timedelta(minutes=15)

# Return cached results if last scan was less then this time ago.
MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=120)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_USERNAME): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
    vol.Optional(CONF_NAME, default=CONF_DEFAULT_NAME): cv.string,
    vol.Optional(CONF_HOST, default=CONF_DEFAULT_IP): cv.string,
    vol.Optional(CONF_MAX_CALLS, default=DEFAULT_MAX_CALLS): cv.positive_int,
})

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Setup the sensor."""
    username = config.get(CONF_USERNAME)
    password = config.get(CONF_PASSWORD)
    host = config.get(CONF_HOST)
  
    name = config.get(CONF_NAME)
    maxcalls = config.get(CONF_MAX_CALLS)

    data_object = CallData(host, username, password)
    data_object.update()

    if data_object.data is None:
        _LOGGER.error('Unable to fetch call data')
        return False

    sensors = []
    for callnumber in range(maxcalls):
        sensors.append(CallDataSensor(hass, data_object, name, callnumber))

    add_entities(sensors)


def callparser(callData):    
    calls = []
    
    for call in callData:
        callType = None
      
        if (call['Type'] == 1):
          callType = "incoming"
        elif (call['Type'] == 2):
          callType = "missed"
        elif (call['Type'] == 3):
          callType = "outgoing"
          
        number = call['Called'] if call['Type'] == 3 else call['Caller']
        name = number if call['Name'] == None else call['Name']
        
        call_dict = {
            'calltype': callType,
            'name': name,
            'number': number,
            'date': call['Date'].strftime("%d.%m.%Y %H:%M"),
            'duration': call['Duration'].seconds // 60 % 60
        }

        calls.append(call_dict)

    return calls


class CallDataSensor(Entity):
    """
    Implementation of a call sensor.
    Represents the Nth call.
    """
    def __init__(self, hass, data_object, sensor_name, callnumber):
        """
        Initialize the sensor.
        sensor_name is typically the name of the sensor
        callnumber indicates which recent call this is, starting at zero
        """
        self._callno = callnumber
        self._hass = hass
        self.data_object = data_object
        self.entity_id = ENTITY_ID_FORMAT.format(sensor_name.lower() + '_call_' + str(callnumber))        
        self._name = sensor_name + '_call_' + str(callnumber)
        self._callType = None
        self._call_attributes = {}
        self.update()

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def icon(self):
        """Return the icon for the frontend."""
        if self._callType == 'incoming':
          return 'mdi:phone-incoming'
        elif self._callType == 'missed':
          return 'mdi:phone-missed'        
        elif self._callType == 'outgoing':
          return 'mdi:phone-outgoing'
        else:
          return 'mdi:phone-hangup'

    @property
    def state(self):
        """Return the date of the next call."""
        return self._state

    @property
    def device_state_attributes(self):
        """The attributes of the call."""
        return self._call_attributes

    def update(self):
        """Get the latest update and set the state and attributes."""
        # Defaults:
        self._state = "-"
        # I guess the number and details of attributes probably
        # shouldn't change, so we should really prepopulate them.
        self._call_attributes = {
            'calltype': None,
            'name': None,
            'number': None,
            'date': None,
            'duration': None
        }
  
        # Get the data
        self.data_object.update()

        call_list = self.data_object.data
        if call_list and (self._callno < len(call_list)):
            val = call_list[self._callno]

            calltype = val.get('calltype', 'unknown')
            name = val.get('name', 'unknown')
            number = val.get('number', 'unknown')
            date = val.get('date', 'unknown')
            duration = val.get('duration', 'unknown')
            
            self._name = name
            self._call_attributes['calltype'] = calltype
            self._call_attributes['name'] = name
            self._call_attributes['number'] = number
            self._call_attributes['date'] = date
            self._call_attributes['duration'] = duration
            
            self._callType = calltype
            self._state = date

class CallData(object):
    def __init__(self, host, username, password):      
        import fritzconnection as fc
    
        self.conn = fc.FritzCall(address=host, user=username, password=password)
        self.data = None

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        self.data = []

        callData = self.conn.get_calls()
        calls = callparser(callData)
        
        self.data = calls