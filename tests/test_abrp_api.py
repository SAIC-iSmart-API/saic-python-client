import json
from unittest import TestCase
from unittest.mock import patch, PropertyMock

import requests
from saic_ismart_client.abrp_api import AbrpApi
from saic_ismart_client.ota_v2_1.data_model import OtaRvmVehicleStatusResp25857, RvsPosition, RvsWayPoint, \
    RvsWgs84Point, Timestamp4Short, RvsBasicStatus25857
from saic_ismart_client.ota_v3_0.data_model import OtaChrgMangDataResp

TLM_URL = 'https://api.iternio.com/1/tlm/send'
ABRP_API_KEY = '8cfc314b-03cd-4efe-ab7d-4431cd8f2e2d'
ABRP_USER_TOKEN = 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'


def get_mocked_vehicle_status() -> OtaRvmVehicleStatusResp25857:
    vehicle_status = OtaRvmVehicleStatusResp25857()
    vehicle_status.gps_position = RvsPosition()
    vehicle_status.gps_position.way_point = RvsWayPoint()
    vehicle_status.gps_position.way_point.position = RvsWgs84Point()
    vehicle_status.gps_position.way_point.position.latitude = 10000000
    vehicle_status.gps_position.way_point.position.longitude = 10000000
    vehicle_status.gps_position.way_point.position.altitude = 100
    vehicle_status.gps_position.timestamp_4_short = Timestamp4Short()
    vehicle_status.gps_position.timestamp_4_short.seconds = 1000000000
    vehicle_status.gps_position.way_point.speed = 100
    vehicle_status.gps_position.way_point.heading = 90
    vehicle_status.basic_vehicle_status = RvsBasicStatus25857()
    # is charging
    vehicle_status.basic_vehicle_status.extended_data2 = 0
    # is parked
    vehicle_status.basic_vehicle_status.engine_status = 0
    vehicle_status.basic_vehicle_status.hand_brake = False
    # temperature
    vehicle_status.basic_vehicle_status.exterior_temperature = 10
    vehicle_status.basic_vehicle_status.mileage = 1000
    vehicle_status.basic_vehicle_status.fuel_range_elec = 32000
    return vehicle_status


def get_mocked_charge_status() -> OtaChrgMangDataResp:
    charge_status = OtaChrgMangDataResp()
    charge_status.bmsPackSOCDsp = 841
    charge_status.bmsPackCrnt = 20000
    charge_status.bmsPackVol = 1602
    return charge_status


def mock_post(mocked_post):
    def res():
        r = requests.Response()
        r.status_code = 200
        return r

    mocked_post.return_value = res()
    type(mocked_post.return_value).content = PropertyMock(return_value=json.dumps({'status': 'ok'}).encode())


class TestAbrpApi(TestCase):
    def setUp(self) -> None:
        self.abrp_api = AbrpApi(ABRP_API_KEY, ABRP_USER_TOKEN)

    @patch.object(requests, 'post')
    def test_update_abrp(self, mocked_post):
        vehicle_status = get_mocked_vehicle_status()
        charge_status = get_mocked_charge_status()

        mock_post(mocked_post)

        self.abrp_api.update_abrp(vehicle_status, charge_status)
        self.assertEqual(TLM_URL, mocked_post.call_args.kwargs['url'])
        header_dict = mocked_post.call_args.kwargs['headers']
        self.check_dict_value(header_dict, 'Authorization', f'APIKEY {ABRP_API_KEY}')
        params_dict = mocked_post.call_args.kwargs['params']
        self.check_dict_value(params_dict, 'token', ABRP_USER_TOKEN)
        tlm_value = params_dict['tlm']
        tlm_json = json.loads(tlm_value)
        self.check_dict_value(tlm_json, 'utc', 1000000000)
        self.check_dict_value(tlm_json, 'soc', 84.1)
        self.check_dict_value(tlm_json, 'power', 0.0)
        self.check_dict_value(tlm_json, 'speed', 10.0)
        self.check_dict_value(tlm_json, 'lat', 10.00000000)
        self.check_dict_value(tlm_json, 'lon', 10.00000000)
        self.check_dict_value(tlm_json, 'is_charging', 0)
        self.check_dict_value(tlm_json, 'is_parked', 1)
        self.check_dict_value(tlm_json, 'heading', 90)
        self.check_dict_value(tlm_json, 'elevation', 100)
        self.check_dict_value(tlm_json, 'voltage', 400.5)
        self.check_dict_value(tlm_json, 'current', 0.0)
        self.check_dict_value(tlm_json, 'ext_temp', 10)
        self.check_dict_value(tlm_json, 'odometer', 100.0)
        self.check_dict_value(tlm_json, 'est_battery_range', 3200.0)

    def check_dict_value(self, data: dict, key: str, expected_value):
        if key in data:
            self.assertEqual(expected_value, data[key])
        else:
            self.fail(f'{key} missing')
