"""The tests for the iNode ble_parser."""
import pytest
from ble_monitor.ble_parser import ble_parser


class TestInode:

    @pytest.fixture(autouse=True)
    def _init_ble_monitor(self):
        self.lpacket_ids = {}
        self.movements_list = {}
        self.adv_priority = {}
        self.trackerlist = []
        self.report_unknown = "other"
        self.discovery = True

    def test_inode_energy_meter(self):
        """Test inode parser for iNode Energy Monitor."""
        data_string = "043E2102010000473A6D6F1200150201060EFF90820400CFE40000DC05B0ED10020A08A5"
        data = bytes(bytearray.fromhex(data_string))

        # get the mac to fill in an initial packet id
        is_ext_packet = True if data[3] == 0x0D else False
        mac = (data[8 if is_ext_packet else 7:14 if is_ext_packet else 13])[::-1]
        self.lpacket_ids[mac] = "0400cfe40000dc05b0ed20"
        # pylint: disable=unused-variable
        sensor_msg, tracker_msg = ble_parser(self, data)

        assert sensor_msg["firmware"] == "iNode"
        assert sensor_msg["type"] == "iNode Energy Meter"
        assert sensor_msg["mac"] == "00126F6D3A47"
        assert sensor_msg["packet"] == "0400cfe40000dc05b0ed10"
        assert sensor_msg["data"]
        assert sensor_msg["energy"] == 39.05
        assert sensor_msg["energy unit"] == "kWh"
        assert sensor_msg["power"] == 160.0
        assert sensor_msg["power unit"] == "W"
        assert sensor_msg["constant"] == 1500
        assert sensor_msg["battery"] == 100
        assert sensor_msg["voltage"] == 2.88
        assert sensor_msg["light level"] == 0.0
        assert sensor_msg["week day"] == 0
        assert sensor_msg["week day total"] == 4333
        assert sensor_msg["rssi"] == -91
