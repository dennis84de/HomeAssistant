"""
Component to integrate with blueprint.

For more details about this component, please refer to
https://github.com/custom-components/blueprint
"""
import os
from datetime import timedelta
import pickle
import logging
import asyncio
import voluptuous as vol
from homeassistant import config_entries
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers import discovery, event
from homeassistant.util import Throttle
from homeassistant.core import callback

import gkeepapi

from integrationhelper.const import CC_STARTUP_VERSION

from .const import (
    CONF_PASSWORD,
    CONF_USERNAME,
    CONF_DEFAULT_LIST,
    ATTR_ITEM_TITLE,
    ATTR_ITEM_CHECKED,
    SERVICE_NEW_ITEM,
    SERVICE_ITEM_CHECKED,
    DEFAULT_NAME,
    SENSOR_NAME,
    DOMAIN_DATA,
    DOMAIN,
    ISSUE_URL,
    PLATFORMS,
    REQUIRED_FILES,
    VERSION,
)

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=300)

_LOGGER = logging.getLogger(__name__)

NEW_ITEM_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ITEM_TITLE): cv.string,
    }
)

CHECKED_ITEM_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ITEM_TITLE): cv.string,
        vol.Required(ATTR_ITEM_CHECKED): cv.boolean,
    }
)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_USERNAME): cv.string,
                vol.Required(CONF_PASSWORD): cv.string,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass, config):
    """Set up this component using YAML."""

    # Check that all required files are present
    file_check = await check_files(hass)
    if not file_check:
        return False

    return True


async def async_setup_entry(hass, config_entry):
    """Set up this integration using UI."""
    conf = hass.data.get(DOMAIN_DATA)
    if config_entry.source == config_entries.SOURCE_IMPORT:
        if conf is None:
            hass.async_create_task(
                hass.config_entries.async_remove(config_entry.entry_id)
            )
        return False

    # Print startup message
    _LOGGER.info(
        CC_STARTUP_VERSION.format(name=DOMAIN, version=VERSION, issue_link=ISSUE_URL)
    )


    # Create DATA dict
    hass.data[DOMAIN_DATA] = {}

    # Get "global" configuration.
    username = config_entry.data.get(CONF_USERNAME)
    password = config_entry.data.get(CONF_PASSWORD)
    default_list = config_entry.data.get(CONF_DEFAULT_LIST)

    # Configure the client.
    keep = gkeepapi.Keep()
    gkeep_token = None
    if os.path.exists('/home/homeassistant/.homeassistant/.storage/gkeep.pickle'):
        with open('/home/homeassistant/.homeassistant/.storage/gkeep.pickle', 'rb') as token:
            gkeep_token = pickle.load(token)
            keep.resume(username, gkeep_token)
    else:
        try:
            keep.login(username, password)
            gkeep_token = keep.getMasterToken()
            with open('/home/homeassistant/.homeassistant/.storage/gkeep.pickle', 'wb') as token:
                pickle.dump(gkeep_token, token)
        except Exception as e:
            _LOGGER.exception(e)
            return False
        
    await hass.async_add_executor_job(keep.sync)
    all_list = await hass.async_add_executor_job(keep.all)
    for list in all_list:
        if list.title == default_list:
            hass.data[DOMAIN_DATA]["gkeep"] = GkeepData(hass, keep, list)
            break
    else:
        return False


    # Add sensor
    hass.async_add_job(
        hass.config_entries.async_forward_entry_setup(config_entry, "sensor")
    )

    # Add binary_sensor
    hass.async_add_job(
        hass.config_entries.async_forward_entry_setup(config_entry, "binary_sensor")
    )

    @callback
    def item_checked(call):
        item_title = call.data.get(ATTR_ITEM_TITLE)
        item_checked = call.data.get(ATTR_ITEM_CHECKED)
        gkeep = hass.data[DOMAIN_DATA]["gkeep"]
        try:
            for item in gkeep.list.items:
                if item.text == item_title:
                    item.checked = item_checked
                    break
            gkeep.gkeep.sync()
        except Exception as e:
            _LOGGER.exception(e)
        
    #Register "item_checked" service
    hass.services.async_register(
        DOMAIN, SERVICE_ITEM_CHECKED, item_checked, schema=CHECKED_ITEM_SCHEMA
    )

    @callback
    def new_item(call):
        item_title = call.data.get(ATTR_ITEM_TITLE)
        gkeep = hass.data[DOMAIN_DATA]["gkeep"]
        try:
            for item in gkeep.list.items:
                if item.text == item_title:
                    item.checked = False
                    break
            else:
                gkeep.list.add(item_title, False)
            gkeep.gkeep.sync()
        except Exception as e:
            _LOGGER.exception(e)
        
    #Register "new_item" service
    hass.services.async_register(
        DOMAIN, SERVICE_NEW_ITEM, new_item, schema=NEW_ITEM_SCHEMA
    )

    def handle_sensor_change(entity_id, old_state, new_state):
        if old_state is None:
            return
        old_list = old_state.attributes['items']
        new_list = new_state.attributes['items']
        gkeep = hass.data[DOMAIN_DATA]["gkeep"]
        return asyncio.run_coroutine_threadsafe(gkeep.update_from_sensor(hass, old_list, new_list), hass.loop).result()

    event.async_track_state_change(hass, '{}.{}_{}'.format(SENSOR_NAME, DOMAIN, hass.data[DOMAIN_DATA]["gkeep"].list.title.lower()), handle_sensor_change)
    
    return True


class GkeepData:
    """This class handle communication and stores the data."""

    def __init__(self, hass, gkeep, list):
        """Initialize the class."""
        self.hass = hass
        self.gkeep = gkeep
        self.list = list

    async def update_from_sensor(self, hass, old_list, new_list):
        diff_list = []
        for new_item in new_list:
            for old_item in old_list:
                if new_item['name'] == old_item['name'] and new_item['checked'] != old_item['checked']:
                    diff_list.append(new_item)
                    break
        for item in diff_list:
            for gkeep_item in self.list.items:
                if item['name'] == gkeep_item.text:
                    gkeep_item.checked = item['checked']
                    break
                    
        try:
            await self.hass.async_add_executor_job(self.gkeep.sync)
        except Exception as error:  # pylint: disable=broad-except
            _LOGGER.error("Could not sync - %s", error)
                    

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    async def update_data(self):
        """Update data."""
        # This is where the main logic to update platform data goes.
        try:
            await self.hass.async_add_executor_job(self.gkeep.sync)
        except Exception as error:  # pylint: disable=broad-except
            _LOGGER.error("Could not sync - %s", error)
        self.hass.data[DOMAIN_DATA]["data"] = self.list


async def check_files(hass):
    """Return bool that indicates if all files are present."""
    # Verify that the user downloaded all files.
    base = f"{hass.config.path()}/custom_components/{DOMAIN}/"
    missing = []
    for file in REQUIRED_FILES:
        fullpath = "{}{}".format(base, file)
        if not os.path.exists(fullpath):
            missing.append(file)

    if missing:
        _LOGGER.critical("The following files are missing: %s", str(missing))
        returnvalue = False
    else:
        returnvalue = True

    return returnvalue


async def async_remove_entry(hass, config_entry):
    """Handle removal of an entry."""
    try:
        await hass.config_entries.async_forward_entry_unload(config_entry, "sensor")
        _LOGGER.info("Successfully removed sensor from the gkeep integration")
    except ValueError as e:
        _LOGGER.exception(e)
        pass
        