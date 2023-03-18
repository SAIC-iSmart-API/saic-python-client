import urllib.parse

import requests
from saic_ismart_client.ota_v2_1.data_model import OtaRvmVehicleStatusResp25857
from saic_ismart_client.ota_v3_0.data_model import OtaChrgMangDataResp


class AbrpApi:
    def __init__(self, abrp_api_key: str, abrp_user_token: str) -> None:
        self.abrp_api_key = abrp_api_key
        self.abrp_user_token = abrp_user_token

    def update_abrp(self, vehicle_status: OtaRvmVehicleStatusResp25857, charge_status: OtaChrgMangDataResp):
        if (
                self.abrp_api_key is not None
                and self.abrp_user_token is not None
                and vehicle_status is not None
                and vehicle_status.get_gps_position() is not None
                and vehicle_status.get_gps_position().get_way_point() is not None
                and vehicle_status.get_gps_position().get_way_point().get_position() is not None
                and vehicle_status.get_gps_position().get_way_point().get_position().latitude > 0
                and vehicle_status.get_gps_position().get_way_point().get_position().longitude > 0
                and charge_status is not None
        ):
            # Request
            tlm_send_url = 'https://api.iternio.com/1/tlm/send'
            data = {
                'utc': vehicle_status.get_gps_position().timestamp_4_short.seconds,
                'soc': (charge_status.bmsPackSOCDsp / 10.0),
                'power': charge_status.get_power(),
                'speed': (vehicle_status.get_gps_position().get_way_point().speed / 10.0),
                'lat': (vehicle_status.get_gps_position().get_way_point().get_position().latitude / 1000000.0),
                'lon': (vehicle_status.get_gps_position().get_way_point().get_position().longitude / 1000000.0),
                'is_charging': vehicle_status.is_charging(),
                'is_parked': vehicle_status.is_parked(),
                'heading': vehicle_status.get_gps_position().get_way_point().heading,
                'elevation': vehicle_status.get_gps_position().get_way_point().get_position().altitude,
                'voltage': charge_status.get_voltage(),
                'current': charge_status.get_current()
            }
            exterior_temperature = vehicle_status.get_basic_vehicle_status().exterior_temperature
            if exterior_temperature != -128:
                data['ext_temp'] = exterior_temperature
            mileage = vehicle_status.get_basic_vehicle_status().mileage
            if mileage > 0:
                data['odometer'] = mileage / 10.0
            range_elec = vehicle_status.get_basic_vehicle_status().fuel_range_elec
            if range_elec > 0:
                data['est_battery_range'] = range_elec / 10.0

            tlm_response = requests.get(tlm_send_url, params={
                'api_key': self.abrp_api_key,
                'token': self.abrp_user_token,
                'tlm': urllib.parse.urlencode(data)
            })
            tlm_response.raise_for_status()
            print(f'ABRP: {tlm_response.content}')
