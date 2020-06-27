import logging
import hashlib
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from gkeepapi.node import NodeType
from homeassistant.components.sensor import PLATFORM_SCHEMA, ENTITY_ID_FORMAT
from homeassistant.const import CONF_NAME, CONF_USERNAME, CONF_PASSWORD
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity import async_generate_entity_id

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = 'Google Keep'
CONF_TITLES = 'titles'
CONF_LABELS = 'labels'
CONF_PINNED = 'pinned'

DOMAIN = "google_keep"

DEFAULT_LIST_NAME = 'Grocery'

ATTR_ITEM_TITLE = "item_title"
ATTR_ITEM_CHECKED = "item_checked"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Required(CONF_USERNAME): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
    vol.Optional(CONF_TITLES, default=[]): cv.ensure_list,
    vol.Optional(CONF_LABELS, default=[]): cv.ensure_list,
    vol.Optional(CONF_PINNED, default=False): cv.boolean
})

# Service constants and validation
SERVICE_LIST_NAME = 'list'
SERVICE_LIST_ITEM = 'items'

SERVICE_LIST_SCHEMA = vol.Schema({
    vol.Optional(SERVICE_LIST_NAME): cv.string,
    vol.Required(SERVICE_LIST_ITEM): cv.ensure_list_csv,
})

CHECKED_ITEM_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ITEM_TITLE): cv.string,
        vol.Required(ATTR_ITEM_CHECKED): cv.boolean,
    }
)

def replace_leading_spaces(s):
    stripped = s.lstrip()
    return '&nbsp;' * 2 * (len(s) - len(stripped)) + stripped


def setup_platform(hass, config, add_entities, discovery_info=None):
    sensor_name = config.get(CONF_NAME)
    username = config.get(CONF_USERNAME)
    password = config.get(CONF_PASSWORD)
    titles = config.get(CONF_TITLES)
    labels = config.get(CONF_LABELS)
    pinned = config.get(CONF_PINNED)

    import gkeepapi
    keep = gkeepapi.Keep()
    login_success = keep.login(username, password)

    if not login_success:
        raise Exception('Invalid username or password')

    dev = []
    hash_value = hashlib.md5(str((username, str(titles), str(labels), pinned)).encode()).hexdigest()[-10:]
    uid = '{}_{}'.format(sensor_name, hash_value)
    entity_id = async_generate_entity_id(ENTITY_ID_FORMAT, uid, hass=hass)

    dev.append(GoogleKeepSensor(entity_id, sensor_name, username, keep, titles, labels, pinned))
    add_entities(dev, True)

    def item_checked(call):
        item_title = call.data.get(ATTR_ITEM_TITLE)
        item_checked = call.data.get(ATTR_ITEM_CHECKED)

        try:
            for item in keep.list.items:
                if item.text == item_title:
                    item.checked = item_checked
                    break
            keep.sync()
        except Exception as e:
            _LOGGER.exception(e)

    def add_to_list(call):
        """Add things to a Google Keep list."""

        list_name = call.data.get(SERVICE_LIST_NAME, DEFAULT_LIST_NAME)
        things = call.data.get(SERVICE_LIST_ITEM)

        # Split any things in the list separated by ' , '
        things = [x for thing in things for x in thing.split(', ')]

        keep.sync()

        # Find the target list amongst all the Keep notes/lists
        for l in keep.all():
            if l.title == list_name:
                _LOGGER.info("List with name {} found on Keep.".format(list_name))
                list_to_update = l
                break
        else:
            _LOGGER.info("List with name {} not found on Keep. Creating new list.".format(list_name))
            list_to_update = keep.createList(list_name)

        _LOGGER.info("Things to add: {}".format(things))

        for thing in things:
            _LOGGER.debug("Adding element: {}".format(thing))

            for old_thing in list_to_update.items:                
                if old_thing.text.lower() == thing:
                    _LOGGER.debug("Element '{}' already on list.".format(thing))
                    old_thing.checked = False
                    break            
            else:                
                list_to_update.add(thing, False)

        keep.sync()

    # Register the service google_keep.add_to_list with Home Assistant.
    hass.services.register(DOMAIN, 'add_to_list', add_to_list, schema=SERVICE_LIST_SCHEMA)

    #Register "item_checked" service
    hass.services.async_register(
        DOMAIN, 'item_checked', item_checked, schema=CHECKED_ITEM_SCHEMA
    )

class GoogleKeepSensor(Entity):
    def __init__(self, entity_id, name, username, keep, titles, labels, pinned):
        self.entity_id = entity_id
        self._name = name
        self._username = username
        self._titles = titles
        self._labels = labels
        self._pinned = pinned
        self._keep = keep
        self._notes = []
        self._state = None

    @property
    def name(self):
        return '{} - {}'.format(self._name, self._username)

    @property
    def state(self):
        return len(self._notes)

    @property
    def unit_of_measurement(self):
        return None

    @property
    def device_state_attributes(self):
        attr = dict()
        attr['notes'] = self._notes
        attr[CONF_TITLES] = self._titles
        attr[CONF_LABELS] = self._labels
        attr[CONF_PINNED] = self._pinned
        attr[CONF_USERNAME] = self._username
        return attr

    def update(self):
        self._keep.sync()
        if self._pinned:
            notes = self._keep.find(pinned=True)
        else:
            notes = self._keep.all()
        if len(self._labels) > 0:
            notes = list(
                filter(lambda n: set(self._labels).intersection(set(map(lambda l: str(l), n.labels.all()))), notes))
        if len(self._titles) > 0:
            notes = list(filter(lambda n: str(n.title) in self._titles, notes))
        self._notes = []
        for note in notes:
            note_type = note.type
            title = str(note.title)
            lines = list(map(lambda n: str(n), note.text.split("\n")))
            color = note.color.name
            checked = []
            unchecked = []
            children = []
            if note_type == NodeType.List:
                checked = list(map(lambda n: str(n), note.checked))
                unchecked = list(map(lambda n: str(n), note.unchecked))
                children = list(
                    map(lambda c: GoogleKeepSensor.map_node(c), filter(lambda c: not c.indented, note.items)))
            parsed_note = GoogleKeepSensor.make_note(str(note_type), title, lines, children, checked, unchecked, color)
            self._notes.append(parsed_note)

    @staticmethod
    def make_note(note_type, title, lines, children, checked, unchecked, color):
        note = dict()
        note["note_type"] = note_type
        note["title"] = title
        note["lines"] = lines
        note["children"] = children
        note["color"] = color
        note["checked"] = checked
        note["unchecked"] = unchecked
        return note

    @staticmethod
    def map_node(node):
        node_data = dict()
        node_data["checked"] = node.checked
        node_data["text"] = node.text
        node_data["children"] = list(map(lambda c: GoogleKeepSensor.map_node(c), node.subitems))
        return node_data
