import json
import time

import requests
from saic_ismart_client.ota_v2_1.data_model import OtaRvmVehicleStatusResp25857, RvsPosition, RvsBasicStatus25857
from saic_ismart_client.ota_v3_0.data_model import OtaChrgMangDataResp


class AbrpApiException(Exception):
    def __init__(self, msg: str):
        self.message = msg

    def __str__(self):
        return self.message


class AbrpApi:
    def __init__(self, abrp_api_key: str, abrp_user_token: str) -> None:
        self.abrp_api_key = abrp_api_key
        self.abrp_user_token = abrp_user_token

    def update_abrp(self, vehicle_status: OtaRvmVehicleStatusResp25857, charge_status: OtaChrgMangDataResp) -> str:
        if (
                self.abrp_api_key is not None
                and self.abrp_user_token is not None
                and vehicle_status is not None
                and charge_status is not None
        ):
            # Request
            tlm_send_url = 'https://api.iternio.com/1/tlm/send'
            data = {
                'utc': int(time.time()), # We assume the timestamp is now, we will update it later from GPS if available
                'soc': (charge_status.bmsPackSOCDsp / 10.0),
                'power': charge_status.get_power(),
                'voltage': charge_status.get_voltage(),
                'current': charge_status.get_current(),
                'is_charging': vehicle_status.is_charging(),
                'is_parked': vehicle_status.is_parked(),
            }

            basic_vehicle_status = vehicle_status.get_basic_vehicle_status()
            if basic_vehicle_status is not None:
                data.update(self.__extract_basic_vehicle_status(basic_vehicle_status))

            gps_position = vehicle_status.get_gps_position()
            if gps_position is not None:
                data.update(self.__extract_gps_position(gps_position))

            headers = {
                'Authorization': f'APIKEY {self.abrp_api_key}'
            }

            try:
                response = requests.post(url=tlm_send_url, headers=headers, params={
                    'token': self.abrp_user_token,
                    'tlm': json.dumps(data)
                })
                return response.content.decode()
            except requests.exceptions.ConnectionError as ece:
                raise AbrpApiException(f'Connection error: {ece}')
            except requests.exceptions.Timeout as et:
                raise AbrpApiException(f'Timeout error {et}')
            except requests.exceptions.HTTPError as ehttp:
                raise AbrpApiException(f'HTTP error {ehttp}')
            except requests.exceptions.RequestException as e:
                raise AbrpApiException(f'{e}')
        else:
            return 'ABRP request skipped because of missing configuration'

    @staticmethod
    def __extract_basic_vehicle_status(basic_vehicle_status: RvsBasicStatus25857) -> dict:
        data = {}

        exterior_temperature = basic_vehicle_status.exterior_temperature
        if exterior_temperature is not None and exterior_temperature != -128:
            data['ext_temp'] = exterior_temperature
        mileage = basic_vehicle_status.mileage
        if mileage is not None and mileage > 0:
            data['odometer'] = mileage / 10.0
        range_elec = basic_vehicle_status.fuel_range_elec
        if range_elec is not None and range_elec > 0:
            data['est_battery_range'] = float(range_elec) / 10.0

        return data

    @staticmethod
    def __extract_gps_position(gps_position: RvsPosition) -> dict:

        # Do not transmit GPS data if we have no timestamp
        if gps_position.timestamp_4_short is None:
            return {}

        way_point = gps_position.get_way_point()

        # Do not transmit GPS data if we have no speed info
        if way_point is None:
            return {}

        data = {
            'utc': gps_position.timestamp_4_short.seconds,
            'speed': (way_point.speed / 10.0),
            'heading': way_point.heading,
        }

        position = way_point.get_position()

        if position is None or position.latitude <= 0 or position.longitude <= 0:
            return data

        data.update({
            'lat': (position.latitude / 1000000.0),
            'lon': (position.longitude / 1000000.0),
            'elevation': position.altitude,
        })

        return data


