""" TeamTracker Team Status """
import asyncio
import logging
from datetime import date, datetime, timedelta, timezone
import arrow
import json
import codecs
import locale
import os

import aiohttp
import aiofiles
from async_timeout import timeout
from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_registry import (
    async_entries_for_config_entry,
    async_get,
)
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .clear_values import async_clear_values
from .event import async_process_event
from .set_values import (
    async_set_values,
    async_set_in_values,
)
from .set_baseball import async_set_baseball_values
from .set_hockey import async_set_hockey_values
from .set_soccer import async_set_soccer_values
from .set_volleyball import async_set_volleyball_values
from .utils import async_get_value

from .const import (
    API_LIMIT,
    CONF_CONFERENCE_ID,
    CONF_LEAGUE_ID,
    CONF_LEAGUE_PATH,
    CONF_SPORT_PATH,
    CONF_TIMEOUT,
    CONF_TEAM_ID,
    COORDINATOR,
    DEFAULT_CONFERENCE_ID,
    DEFAULT_TIMEOUT,
    DEFAULT_KICKOFF_IN,
    DEFAULT_LAST_UPDATE,
    DEFAULT_LEAGUE,
    DEFAULT_LOGO,
    DEFAULT_LEAGUE_PATH,
    DEFAULT_PROB,
    DEFAULT_SPORT_PATH,
    DOMAIN,
    ISSUE_URL,
    LEAGUE_LIST,
    PLATFORMS,
    SPORT_LIST,
    URL_HEAD,
    URL_TAIL,
    USER_AGENT,
    VERSION,
)

_LOGGER = logging.getLogger(__name__)
#team_prob = {}
#oppo_prob = {}

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Load the saved entities."""
    # Print startup message
    _LOGGER.info("TeamTracker version %s is starting, if you have any issues please report them here: %s", VERSION, ISSUE_URL,)
    hass.data.setdefault(DOMAIN, {})

#
#  No support for an Options flow at this time.  Uncomment line below if ever added.
#    entry.add_update_listener(update_listener)

    if entry.unique_id is not None:
        hass.config_entries.async_update_entry(entry, unique_id=None)

        ent_reg = async_get(hass)
        for entity in async_entries_for_config_entry(ent_reg, entry.entry_id):
            ent_reg.async_update_entity(entity.entity_id, new_unique_id=entry.entry_id)

    # Setup the data coordinator
    coordinator = TeamTrackerDataUpdateCoordinator(
        hass,
        entry.data,
        entry.data.get(CONF_TIMEOUT)
    )

    # Fetch initial data so we have data when entities subscribe
    await coordinator.async_refresh()

    hass.data[DOMAIN][entry.entry_id] = {
        COORDINATOR: coordinator,
    }

    hass.config_entries.async_setup_platforms(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""

    _LOGGER.debug("Attempting to unload entities from the %s integration", DOMAIN)

    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(config_entry, platform)
                for platform in PLATFORMS
            ]
        )
    )

    if unload_ok:
        _LOGGER.debug("Successfully removed entities from the %s integration", DOMAIN)
        hass.data[DOMAIN].pop(config_entry.entry_id)

    return unload_ok

#
#  Only needed if Options Flow is added
#
#async def update_listener(hass, entry):
#    """Update listener."""
#    entry.data = entry.options
#    await hass.config_entries.async_forward_entry_unload(entry, "sensor")
#    hass.async_add_job(hass.config_entries.async_forward_entry_setup(entry, "sensor"))


async def async_migrate_entry(hass, config_entry):
    """Migrate an old config entry."""
    version = config_entry.version

    # 1-> 2->3: Migration format
    # Add CONF_TIMEOUT, CONF_LEAGUE_ID, CONF_SPORT_PATH, and CONF_LEAGUE_PATH if not already populated
    if version < 3:
        _LOGGER.debug("Migrating from version %s", version)
        updated_config = config_entry.data.copy()

        if CONF_TIMEOUT not in updated_config.keys():
            updated_config[CONF_TIMEOUT] = DEFAULT_TIMEOUT
        if CONF_LEAGUE_ID not in updated_config.keys():
            updated_config[CONF_LEAGUE_ID] = DEFAULT_LEAGUE
        if (CONF_SPORT_PATH not in updated_config.keys()) or (CONF_LEAGUE_PATH not in updated_config.keys()):
            league_id = updated_config[CONF_LEAGUE_ID].upper()
            updated_config[CONF_SPORT_PATH] = DEFAULT_SPORT_PATH
            updated_config[CONF_LEAGUE_PATH] = DEFAULT_LEAGUE_PATH
            for x in range(len(LEAGUE_LIST)):
                if LEAGUE_LIST[x][0] == league_id:
                    updated_config[CONF_SPORT_PATH] = LEAGUE_LIST[x][1]
                    updated_config[CONF_LEAGUE_PATH] = LEAGUE_LIST[x][2]

        if updated_config != config_entry.data:
            hass.config_entries.async_update_entry(config_entry, data=updated_config)

        config_entry.version = 3
        _LOGGER.debug("Migration to version %s complete", config_entry.version)

    return True


class TeamTrackerDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching TeamTracker data."""

    data_cache = {}
    last_update = {}
    c_cache = {}

    def __init__(self, hass, config, the_timeout: int):
        """Initialize."""
        self.interval = timedelta(minutes=10)
        self.name = config[CONF_NAME]
        self.timeout = the_timeout
        self.config = config
        self.hass = hass

        _LOGGER.debug("%s: Data will be updated every %s minutes", self.name, self.interval)

        super().__init__(hass, _LOGGER, name=self.name, update_interval=self.interval)

#
#  Top-level method called from HA to update data for all teamtracker sensors
#
    async def _async_update_data(self):
        file_override = False

        async with timeout(self.timeout):
            try:
                data = await self.async_update_game_data(self.config, self.hass)

                # update the interval based on flag
                if data["private_fast_refresh"] == True:
                    self.update_interval = timedelta(seconds=5)
                else:
                    self.update_interval = timedelta(minutes=10)
            except Exception as error:
                raise UpdateFailed(error) from error
            return data

#
#  Update game data from data_cache or the API (if expired)
#
    async def async_update_game_data(self, config, hass) -> dict:

        sensor_name = config[CONF_NAME]
        sport_path = config[CONF_SPORT_PATH]
        league_path = config[CONF_LEAGUE_PATH]
        conference_id = config[CONF_CONFERENCE_ID]

        try:
            lang = hass.config.language
        except:
            lang, enc = locale.getlocale()
            lang = lang or "en_US"

        key = sport_path + ":" + league_path + ":" + conference_id

#
#  Use cache if not expired
#
        if key in self.data_cache:
            expiration = datetime.fromisoformat(self.last_update[key]) + self.update_interval
            now = datetime.now(timezone.utc)
                
            time_diff = now - expiration

            if now < expiration:
                data = self.data_cache[key]
                values = await self.async_update_values(config, hass, data, lang)
                if values["api_message"]:
                    values["api_message"] = "Cached data: " + values["api_message"]
                else:
                    values["api_message"] = "Cached data"
                return values

#
#  Call the API
#  Get the language based on the locale
#    Then override it if there is a value in frontend_storage for the selected language
#      (it usually takes about a minute after reboot for frontend_storage to be populated)
#

        data, file_override = await self.async_call_api(config, hass, lang)
        values = await self.async_update_values(config, hass, data, lang)
        self.data_cache[key] = data
        self.last_update[key] = values["last_update"]

        if (file_override):
            path = "/share/tt/results/" + sensor_name + ".json"
            if not os.path.exists(path):
                _LOGGER.debug("%s: Creating results file '%s'", sensor_name, path)
                values["last_update"] = DEFAULT_LAST_UPDATE # set to fixed time for compares
                values["kickoff_in"] = DEFAULT_KICKOFF_IN
                with open(path, 'w') as convert_file:
                    convert_file.write(json.dumps(values, indent=4))

        return values

#
#  Call the API (or file override) and get the data returned by it
#
    async def async_call_api(self, config, hass, lang) -> dict:
        """Query API for status."""

        headers = {"User-Agent": USER_AGENT, "Accept": "application/ld+json"}
        sensor_name = config[CONF_NAME]

        data = None
        file_override = False

        league_id = config[CONF_LEAGUE_ID].upper()
        sport_path = config[CONF_SPORT_PATH]
        league_path = config[CONF_LEAGUE_PATH]
        url_parms = "?lang=" + lang[:2] + "&limit=" + str(API_LIMIT)

        d1 = (date.today() - timedelta(days = 1)).strftime("%Y%m%d")
        d2 = (date.today() + timedelta(days = 5)).strftime("%Y%m%d")
        url_parms = url_parms + "&dates=" + d1 + "-" + d2

        if CONF_CONFERENCE_ID in config.keys():
                if (len(config[CONF_CONFERENCE_ID]) > 0):
                    url_parms = url_parms + "&groups=" + config[CONF_CONFERENCE_ID]
                    if (config[CONF_CONFERENCE_ID] == '9999'):
                        file_override = True
        team_id = config[CONF_TEAM_ID].upper()
        url = URL_HEAD + sport_path + "/" + league_path + URL_TAIL + url_parms
    
        if (file_override):
            _LOGGER.debug("%s: Overriding API for '%s'", sensor_name, team_id)
            async with aiofiles.open('/share/tt/test.json', mode='r') as f:
                contents = await f.read()
            data = json.loads(contents)
        else:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as r:
                    _LOGGER.debug("%s: Getting state for '%s' from %s", sensor_name, team_id, url)
                    if r.status == 200:
                        data = await r.json()

            num_events = 0
            if data is not None:
                try:
                    num_events = len(data["events"])
                except:
                    num_events = 0

            if num_events == 0:
                url_parms = "?lang=" + lang[:2]
                if CONF_CONFERENCE_ID in config.keys():
                        if (len(config[CONF_CONFERENCE_ID]) > 0):
                            url_parms = url_parms + "&groups=" + config[CONF_CONFERENCE_ID]
                            if (config[CONF_CONFERENCE_ID] == '9999'):
                                file_override = True
                url = URL_HEAD + sport_path + "/" + league_path + URL_TAIL + url_parms

                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=headers) as r:
                        _LOGGER.debug("%s: Getting state without date constraint for '%s' from %s", sensor_name, team_id, url)
                        if r.status == 200:
                            data = await r.json()

        return data, file_override

#
#  Return values based on the data passed into method
#
    async def async_update_values(self, config, hass, data, lang) -> dict:
        values = {}
        prev_values = {}
        sensor_name = config[CONF_NAME]

        league_id = config[CONF_LEAGUE_ID].upper()
        sport_path = config[CONF_SPORT_PATH]
        league_path = config[CONF_LEAGUE_PATH]

        team_id = config[CONF_TEAM_ID].upper()

        search_key = team_id
        sport = sport_path
        found_competitor = False

        values = await async_clear_values()
        values["sport"] = sport_path
        values["league"] = league_id
        values["league_logo"] = DEFAULT_LOGO
        values["team_abbr"] = team_id
        values["state"] = "NOT_FOUND"
        values["last_update"] = arrow.now().format(arrow.FORMAT_W3C)
        values["private_fast_refresh"] = False

        if data is None:
            values["api_message"] = "API error, no data returned"
            _LOGGER.warn("%s: API did not return any data for team '%s'", sensor_name, team_id)
            return values

        values = await async_process_event(values, sensor_name, data, sport_path, league_id, DEFAULT_LOGO, team_id, lang)

        return values
