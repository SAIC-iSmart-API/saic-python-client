from datetime import datetime, timezone

import requests

from saic_ismart_client.exceptions import SaicApiException
from saic_ismart_client.rest_v2.model import TimeZoneResponse


class SaicRestV2Api():

    def __init__(self, base_uri: str):
        self.__base_uri = base_uri

    def get_user_timezone(self, token: str, uid: str):
        response = TimeZoneResponse()
        self.__execute_get('api.app/v1/user/timezone', token, uid=uid, response_holder=response)
        return response

    def __execute_get(self, endpoint: str, token: str, uid=None, response_holder=None):
        headers = self.__get_headers(token, uid)
        try:
            response = requests.get(url=f'{self.__base_uri}/{endpoint}', headers=headers)
            if response_holder is None:
                return response.content.decode()
            else:
                return response_holder.init_from_dict(response.json())
        except requests.exceptions.ConnectionError as ece:
            raise SaicApiException(f'Connection error: {ece}')
        except requests.exceptions.Timeout as et:
            raise SaicApiException(f'Timeout error: {et}')
        except requests.exceptions.HTTPError as ehttp:
            status_code = ehttp.response.status_code
            raise SaicApiException(f'HTTP error. HTTP status: {status_code}, {ehttp}')
        except requests.exceptions.RequestException as e:
            raise SaicApiException(f'{e}')

    def __get_headers(self, token, uid=None):
        headers = {
            'Content-Type': 'application/json;charset=UTF-8',
            'APP-SEND-DATE': str(datetime.now().replace(tzinfo=timezone.utc).timestamp() * 1000),
            'APP-CONTENT-ENCRYPTED': '0',
            'APP-LANGUAGE-TYPE': 'en',
            'APP-LOGIN-TOKEN': token,
        }
        if uid:
            headers['APP-USER-ID'] = uid
        return headers
