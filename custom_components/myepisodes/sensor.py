"""
Support for myepisodes.com

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/sensor.myepisodes/
"""

import logging
from datetime import timedelta
from datetime import datetime
import voluptuous as vol

from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import (
    ENTITY_ID_FORMAT, PLATFORM_SCHEMA)
from homeassistant.const import (
    CONF_NAME, CONF_PASSWORD, CONF_USERNAME)
from homeassistant.util import Throttle
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)
REQUIREMENTS = ['feedparser']
PLATFORM = 'myepisodes'

CONF_MAX_EPISODES = 'max_episodes'
DEFAULT_NAME = 'myepisodes'
DEFAULT_MAX_EPISODES = 10

SCAN_INTERVAL = timedelta(minutes=15)

# Return cached results if last scan was less then this time ago.
MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=120)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_USERNAME): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional(CONF_MAX_EPISODES, default=DEFAULT_MAX_EPISODES): cv.positive_int,
})

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Setup the myepisodes sensor."""
    username = config.get(CONF_USERNAME)
    password = config.get(CONF_PASSWORD)
  
    name = config.get(CONF_NAME)
    maxevents = config.get(CONF_MAX_EPISODES)

    data_object = MyEpisodesData(username, password)
    data_object.update()

    if data_object.data is None:
        _LOGGER.error('Unable to fetch rss')
        return False

    sensors = []
    for eventnumber in range(maxevents):
        sensors.append(MyEpisodesSensor(hass, data_object, name, eventnumber))

    add_entities(sensors)


def episodeparser(myEpisodesData):    
    events = []
    
    for index, event in enumerate(myEpisodesData.entries):       
        series, episode, title, airdate = event.title.split(' ][ ')
        
        airdateFormatted = datetime.strptime(airdate.replace(" ]", ""), '%d-%b-%Y')
        today = datetime.today()
        
        event_dict = {
            'series': series.replace("[ ", ""),
            'episode': episode,
            'title': title,
            'airdate': airdateFormatted.strftime("%d.%m.%Y"),
            'is_today': (True if today.date() == airdateFormatted.date() else False)
        }

        events.append(event_dict)

    return events


class MyEpisodesSensor(Entity):
    """
    Implementation of a myepisodes sensor.
    Represents the Nth upcoming event.
    """
    def __init__(self, hass, data_object, sensor_name, eventnumber):
        """
        Initialize the sensor.
        sensor_name is typically the name of the sensor
        eventnumber indicates which upcoming event this is, starting at zero
        """
        self._eventno = eventnumber
        self._hass = hass
        self.data_object = data_object
        self.entity_id = ENTITY_ID_FORMAT.format(sensor_name.lower() + '_episode_' + str(eventnumber))        
        self._name = sensor_name + '_episode_' + str(eventnumber)
        self._isToday = False
        self._event_attributes = {}
        self.update()

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def icon(self):
        """Return the icon for the frontend."""
        if self._isToday == True:
          return 'mdi:calendar-alert'
        else:
          return 'mdi:calendar'

    @property
    def state(self):
        """Return the date of the next event."""
        return self._state

    @property
    def device_state_attributes(self):
        """The name and date of the event."""
        return self._event_attributes

    def update(self):
        """Get the latest update and set the state and attributes."""
        # Defaults:
        self._state = "-"
        # I guess the number and details of attributes probably
        # shouldn't change, so we should really prepopulate them.
        self._event_attributes = {
            'series': None,
            'episode': None,
            'title': None,
            'airdate': None,
            'is_today': None
        }
        # Get the data
        self.data_object.update()

        event_list = self.data_object.data
        if event_list and (self._eventno < len(event_list)):
            val = event_list[self._eventno]

            series = val.get('series', 'unknown')
            episode = val.get('episode', 'unknown')
            title = val.get('title', 'unknown')
            airdate = val.get('airdate', 'unknown')
            is_today = val.get('is_today', 'unknown')
            
            self._name = series + ' - ' + episode
            self._event_attributes['series'] = series
            self._event_attributes['episode'] = episode
            self._event_attributes['title'] = title
            self._event_attributes['airdate'] = airdate
            self._event_attributes['is_today'] = is_today
            
            self._state = airdate
            self._isToday = is_today


class MyEpisodesData(object):
    def __init__(self, username, password):
        
        self._url = "http://www.myepisodes.com/rss.php?feed=mylist&uid=" + username + "&pwdmd5=" + password + "&onlyunacquired=1" 
        self.data = None

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        import feedparser

        self.data = []

        rssData = feedparser.parse(self._url)
        events = episodeparser(rssData)
        
        self.data = events