"""The tests for the Teltonika ble_parser."""
import pytest
from ble_monitor.ble_parser import ble_parser


class TestTeltonika:

    @pytest.fixture(autouse=True)
    def _init_ble_monitor(self):
        self.lpacket_ids = {}
        self.movements_list = {}
        self.adv_priority = {}
        self.trackerlist = []
        self.report_unknown = "other"
        self.discovery = True

    def test_blue_puck_T(self):
        """Test Teltonika parser for Blue Puck T."""
        data_string = "043e1e02010001e7e193546ec61202010605166e2a860b08095055434b5f5431dd"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        sensor_msg, tracker_msg = ble_parser(self, data)

        assert sensor_msg["firmware"], "Teltonika"
        assert sensor_msg["type"], "Blue Puck T"
        assert sensor_msg["mac"], "C66E5493E1E7"
        assert sensor_msg["packet"], "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature"], 29.5
        assert sensor_msg["rssi"], -35

    def test_blue_puck_RHT(self):
        """Test Teltonika parser for Blue Puck RHT."""
        data_string = "043e230201000196826a022bf01702010605166e2aa30404166f2a2308095055434b5f5448bd"
        data = bytes(bytearray.fromhex(data_string))
        # pylint: disable=unused-variable
        sensor_msg, tracker_msg = ble_parser(self, data)

        assert sensor_msg["firmware"], "Teltonika"
        assert sensor_msg["type"], "Blue Puck RHT"
        assert sensor_msg["mac"], "F02B026A8296"
        assert sensor_msg["packet"], "no packet id"
        assert sensor_msg["data"]
        assert sensor_msg["temperature"], 11.87
        assert sensor_msg["humidity"], 35
        assert sensor_msg["rssi"], -67
