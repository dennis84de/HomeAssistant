"""Constants for the Passive BLE monitor integration."""

DOMAIN = "ble_monitor"
PLATFORMS = ["binary_sensor", "sensor"]

# Configuration options
CONF_ROUNDING = "rounding"
CONF_DECIMALS = "decimals"
CONF_PERIOD = "period"
CONF_LOG_SPIKES = "log_spikes"
CONF_USE_MEDIAN = "use_median"
CONF_ACTIVE_SCAN = "active_scan"
CONF_HCI_INTERFACE = "hci_interface"
CONF_BT_INTERFACE = "bt_interface"
CONF_BATT_ENTITIES = "batt_entities"
CONF_REPORT_UNKNOWN = "report_unknown"
CONF_RESTORE_STATE = "restore_state"
CONF_ENCRYPTION_KEY = "encryption_key"
CONF_DEVICE_DECIMALS = "decimals"
CONF_DEVICE_USE_MEDIAN = "use_median"
CONF_DEVICE_RESTORE_STATE = "restore_state"
CONF_DEVICE_RESET_TIMER = "reset_timer"
CONFIG_IS_FLOW = "is_flow"

SERVICE_CLEANUP_ENTRIES = "cleanup_entries"

# Default values for configuration options
DEFAULT_ROUNDING = True
DEFAULT_DECIMALS = 1
DEFAULT_PERIOD = 60
DEFAULT_LOG_SPIKES = False
DEFAULT_USE_MEDIAN = False
DEFAULT_ACTIVE_SCAN = False
DEFAULT_BATT_ENTITIES = True
DEFAULT_REPORT_UNKNOWN = False
DEFAULT_DISCOVERY = True
DEFAULT_RESTORE_STATE = False
DEFAULT_DEVICE_DECIMALS = "default"
DEFAULT_DEVICE_USE_MEDIAN = "default"
DEFAULT_DEVICE_RESTORE_STATE = "default"
DEFAULT_DEVICE_RESET_TIMER = 35

# regex constants for configuration schema
MAC_REGEX = "(?i)^(?:[0-9A-F]{2}[:]){5}(?:[0-9A-F]{2})$"
# MiBeacon V2/V3 uses 24 character long key
AES128KEY24_REGEX = "(?i)^[A-F0-9]{24}$"
# MiBeacon V4/V5 uses 32 character long key
AES128KEY32_REGEX = "(?i)^[A-F0-9]{32}$"

"""Fixed constants."""

# Sensor measurement limits to exclude erroneous spikes from the results (temperature in °C)
CONF_TMIN = -40.0
CONF_TMAX = 60.0
CONF_HMIN = 0.0
CONF_HMAX = 99.9

# Sensor type indexes dictionary for sensor platform
# Sensor:
# T  = temperature
# H  = humidity
# M  = moisture
# P  = pressure
# C  = conductivity
# I  = illuminance
# F  = formaldehyde
# Cn = consumable
# Bu = button
# Re = remote
# Fr = fan remote
# Vr = ventilator fan remote
# Br = bathroom heater remote
# Di = dimmer
# W  = weight
# NW = non-stabilized Weight
# Im = impedance
# Vd = volume dispensed
# To = toothbrush mode
# V  = voltage
# B  = battery

# Binary_sensor:
# Rb = remote binary
# Sw = switch
# Op = opening
# L  = light
# Mo = moisture
# Mn = motion
# WR = weight wemoved
# B  = battery (add only when other binary sensor is available)

#                                            sensor                                   binary sensor
# Measurement type         [T  H  M  P  C  I  F  Cn Bu Re Fr Vr Br Di W  NW Im Vd To V  B]  [Rb Sw Op L  Mo Mn WR B]
# start from 0 till 8. 9 means no data
MMTS_DICT = {
    'LYWSDCGQ'          : [[0, 1, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 2], [9, 9, 9, 9, 9, 9, 9, 9]],
    'CGG1'              : [[0, 1, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 2], [9, 9, 9, 9, 9, 9, 9, 9]],
    'CGG1-ENCRYPTED'    : [[0, 1, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 2], [9, 9, 9, 9, 9, 9, 9, 9]],
    'CGDK2'             : [[0, 1, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 2], [9, 9, 9, 9, 9, 9, 9, 9]],
    'LYWSD02'           : [[0, 1, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 2], [9, 9, 9, 9, 9, 9, 9, 9]],
    'LYWSD03MMC'        : [[0, 1, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 3, 2], [9, 9, 9, 9, 9, 9, 9, 9]],
    'CGD1'              : [[0, 1, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 2], [9, 9, 9, 9, 9, 9, 9, 9]],
    'CGP1W'             : [[0, 1, 9, 2, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 3], [9, 9, 9, 9, 9, 9, 9, 9]],
    'MHO-C401'          : [[0, 1, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 2], [9, 9, 9, 9, 9, 9, 9, 9]],
    'MHO-C303'          : [[0, 1, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 2], [9, 9, 9, 9, 9, 9, 9, 9]],
    'JQJCY01YM'         : [[0, 1, 9, 9, 9, 9, 2, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 3], [9, 9, 9, 9, 9, 9, 9, 9]],
    'HHCCJCY01'         : [[0, 9, 1, 9, 2, 3, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9], [9, 9, 9, 9, 9, 9, 9, 9]],
    'GCLS002'           : [[0, 9, 1, 9, 2, 3, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9], [9, 9, 9, 9, 9, 9, 9, 9]],
    'HHCCPOT002'        : [[9, 9, 0, 9, 1, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9], [9, 9, 9, 9, 9, 9, 9, 9]],
    'WX08ZM'            : [[9, 9, 9, 9, 9, 9, 9, 0, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 1], [9, 0, 9, 9, 9, 9, 9, 1]],
    'MCCGQ02HL'         : [[9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 0], [9, 9, 0, 1, 9, 9, 9, 2]],
    'CGH1'              : [[9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 0], [9, 9, 0, 9, 9, 9, 9, 1]],
    'YM-K1501'          : [[0, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9], [9, 0, 9, 9, 9, 9, 9, 9]],
    'YM-K1501EU'        : [[0, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9], [9, 0, 9, 9, 9, 9, 9, 9]],
    'V-SK152'           : [[0, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9], [9, 0, 9, 9, 9, 9, 9, 9]],
    'SJWS01LM'          : [[9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 0], [9, 9, 9, 9, 0, 9, 9, 1]],
    'MJYD02YL'          : [[9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 0], [9, 9, 9, 0, 9, 1, 9, 2]],
    'MUE4094RT'         : [[9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9], [9, 9, 9, 9, 9, 0, 9, 9]],
    'RTCGQ02LM'         : [[9, 9, 9, 9, 9, 9, 9, 9, 0, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 1], [9, 9, 9, 0, 9, 1, 9, 2]],
    'CGPR1'             : [[9, 9, 9, 9, 9, 0, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 1], [9, 9, 9, 9, 9, 0, 9, 1]],
    'MMC-T201-1'        : [[0, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 1], [9, 9, 9, 9, 9, 9, 9, 9]],
    'M1S-T500'          : [[9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 0, 9, 1], [9, 9, 9, 9, 9, 9, 9, 9]],
    'YLAI003'           : [[9, 9, 9, 9, 9, 9, 9, 9, 0, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 1], [9, 9, 9, 9, 9, 9, 9, 9]],
    'YLYK01YL'          : [[9, 9, 9, 9, 9, 9, 9, 9, 9, 0, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9], [0, 9, 9, 9, 9, 9, 9, 9]],
    'YLYK01YL-FANCL'    : [[9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 0, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9], [9, 9, 9, 9, 9, 9, 9, 9]],
    'YLYK01YL-VENFAN'   : [[9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 0, 9, 9, 9, 9, 9, 9, 9, 9, 9], [9, 9, 9, 9, 9, 9, 9, 9]],
    'YLYB01YL-BHFRC'    : [[9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 0, 9, 9, 9, 9, 9, 9, 9, 9], [9, 9, 9, 9, 9, 9, 9, 9]],
    'YLKG07YL/YLKG08YL' : [[9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 0, 9, 9, 9, 9, 9, 9, 9], [9, 9, 9, 9, 9, 9, 9, 9]],
    'ATC'               : [[0, 1, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 3, 2], [9, 9, 9, 9, 9, 9, 9, 9]],
    'Mi Scale V1'       : [[9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 0, 1, 9, 9, 9, 9, 9], [9, 9, 9, 9, 9, 9, 0, 9]],
    'Mi Scale V2'       : [[9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 0, 1, 2, 9, 9, 9, 9], [9, 9, 9, 9, 9, 9, 0, 9]],
    'Kegtron KT-100'    : [[9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 0, 9, 9, 9], [9, 9, 9, 9, 9, 9, 9, 9]],
    'Kegtron KT-200'    : [[9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 0, 9, 9, 9], [9, 9, 9, 9, 9, 9, 9, 9]],
}

# Dictionary with list with supported measurement sensors (first list) and binary sensor (second list)
MEASUREMENT_DICT = {
    'LYWSDCGQ'          : [["temperature", "humidity", "battery"], []],
    'CGG1'              : [["temperature", "humidity", "battery"], []],
    'CGG1-ENCRYPTED'    : [["temperature", "humidity", "battery"], []],
    'CGDK2'             : [["temperature", "humidity", "battery"], []],
    'LYWSD02'           : [["temperature", "humidity", "battery"], []],
    'LYWSD03MMC'        : [["temperature", "humidity", "battery", "voltage"], []],
    'CGD1'              : [["temperature", "humidity", "battery"], []],
    'CGP1W'             : [["temperature", "humidity", "battery", "pressure"], []],
    'MHO-C401'          : [["temperature", "humidity", "battery"], []],
    'MHO-C303'          : [["temperature", "humidity", "battery"], []],
    'JQJCY01YM'         : [["temperature", "humidity", "battery", "formaldehyde"], []],
    'HHCCJCY01'         : [["temperature", "moisture", "conductivity", "illuminance", "remote"], ["remote binary"]],
    'GCLS002'           : [["temperature", "moisture", "conductivity", "illuminance"], []],
    'HHCCPOT002'        : [["moisture", "conductivity"], []],
    'WX08ZM'            : [["consumable", "battery"], ["switch", "battery"]],
    'MCCGQ02HL'         : [["battery"], ["opening", "light", "battery"]],
    'CGH1'              : [["battery"], ["opening", "battery"]],
    'YM-K1501'          : [["temperature"], ["switch"]],
    'YM-K1501EU'        : [["temperature"], ["switch"]],
    'V-SK152'           : [["temperature"], ["switch"]],
    'SJWS01LM'          : [["battery"], ["moisture", "battery"]],
    'MJYD02YL'          : [["battery"], ["light", "motion", "battery"]],
    'MUE4094RT'         : [[], ["motion"]],
    'RTCGQ02LM'         : [["button"], ["light", "motion", "battery"]],
    'CGPR1'             : [["illuminance", "battery"], ["motion", "battery"]],
    'MMC-T201-1'        : [["temperature", "battery"], []],
    'M1S-T500'          : [["toothbrush mode", "battery"], []],
    'YLAI003'           : [["button", "battery"], []],
    'YLYK01YL'          : [["remote"], ["remote binary"]],
    'YLYK01YL-FANCL'    : [["fan remote"], []],
    'YLYK01YL-VENFAN'   : [["byte_1"], []],
    'YLYB01YL-BHFRC'    : [["bathroom heater remote"], []],
    'YLKG07YL/YLKG08YL' : [["dimmer"], []],
    'ATC'               : [["temperature", "humidity", "battery", "voltage"], []],
    'Mi Scale V1'       : [["weight", "non-stabilized weight"], ["weight removed"]],
    'Mi Scale V2'       : [["weight", "non-stabilized weight", "impedance"], ["weight removed"]],
    'Kegtron KT-100'    : [["volume dispensed"], []],
    'Kegtron KT-200'    : [["volume dispensed"], []],
}

KETTLES = ('YM-K1501', 'YM-K1501EU', 'V-SK152')

# Sensor manufacturer dictionary
MANUFACTURER_DICT = {
    'LYWSDCGQ'          : 'Xiaomi',
    'CGG1'              : 'Qingping',
    'CGG1-ENCRYPTED'    : 'Qingping',
    'CGDK2'             : 'Qingping',
    'LYWSD02'           : 'Xiaomi',
    'LYWSD03MMC'        : 'Xiaomi',
    'CGD1'              : 'Qingping',
    'CGP1W'             : 'Qingping',
    'MHO-C401'          : 'Miaomiaoce',
    'MHO-C303'          : 'Miaomiaoce',
    'JQJCY01YM'         : 'Honeywell',
    'HHCCJCY01'         : 'Xiaomi',
    'GCLS002'           : 'Xiaomi',
    'HHCCPOT002'        : 'Xiaomi',
    'WX08ZM'            : 'Xiaomi',
    'MCCGQ02HL'         : 'Xiaomi',
    'CGH1'              : 'Qingping',
    'YM-K1501'          : 'Xiaomi',
    'YM-K1501EU'        : 'Xiaomi',
    'V-SK152'           : 'Viomi',
    'SJWS01LM'          : 'Xiaomi',
    'MJYD02YL'          : 'Xiaomi',
    'MUE4094RT'         : 'Xiaomi',
    'RTCGQ02LM'         : 'Xiaomi',
    'CGPR1'             : 'Qingping',
    'MMC-T201-1'        : 'Xiaomi',
    'M1S-T500'          : 'Xiaomi Soocas',
    'YLAI003'           : 'Yeelight',
    'YLYK01YL'          : 'Yeelight',
    'YLYK01YL-FANCL'    : 'Yeelight',
    'YLYK01YL-VENFAN'   : 'Yeelight',
    'YLYB01YL-BHFRC'    : 'Yeelight',
    'YLKG07YL/YLKG08YL' : 'Yeelight',
    'ATC'               : 'ATC',
    'Mi Scale V1'       : 'Xiaomi',
    'Mi Scale V2'       : 'Xiaomi',
    'Kegtron KT-100'    : 'Kegtron',
    'Kegtron KT-200'    : 'Kegtron',
}
