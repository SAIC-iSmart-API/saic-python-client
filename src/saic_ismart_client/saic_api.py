import datetime
import hashlib
import logging
import os
import time
import urllib.parse
from typing import cast

import requests as requests

from saic_ismart_client.common_model import AbstractMessage, AbstractMessageBody, Header, MessageBodyV2, MessageV2, \
    ScheduledChargingMode, TargetBatteryCode
from saic_ismart_client.ota_v1_1.Message import MessageCoderV11
from saic_ismart_client.ota_v1_1.data_model import AbortSendMessageReq, AlarmSwitch, AlarmSwitchReq, Message, \
    MessageBodyV11, MessageListReq, MessageListResp, MessageV11, MpAlarmSettingType, MpUserLoggingInReq, \
    MpUserLoggingInRsp, StartEndNumber, Timestamp, VinInfo
from saic_ismart_client.ota_v2_1.Message import MessageCoderV21
from saic_ismart_client.ota_v2_1.data_model import OtaRvcReq, OtaRvcStatus25857, OtaRvmVehicleStatusReq, \
    OtaRvmVehicleStatusResp25857, RvcReqParam
from saic_ismart_client.ota_v3_0.Message import MessageBodyV30, MessageCoderV30, MessageV30
from saic_ismart_client.ota_v3_0.data_model import OtaChrgCtrlReq, OtaChrgCtrlStsResp, OtaChrgHeatReq, \
    OtaChrgHeatResp, OtaChrgMangDataResp, OtaChrgRsvanReq, OtaChrgSetngReq, OtaChrgSetngResp, OtaChrgRsvanResp

UID_INIT = '0000000000000000000000000000000000000000000000000#'
AVG_SMS_DELIVERY_TIME = 15
logging.basicConfig(format='%(asctime)s %(message)s')
LOG = logging.getLogger(__name__)
LOG.setLevel(level=os.getenv('LOG_LEVEL', 'INFO').upper())


class SaicMessage:
    def __init__(self, message_id: int, message_type: str, title: str, message_time: datetime, sender: str,
                 content: str, read_status: int, vin: str):
        self.message_id = message_id
        self.message_type = message_type
        self.title = title
        self.message_time = message_time
        self.sender = sender
        self.content = content
        self.read_status = read_status
        self.vin = vin

    def get_read_status_str(self) -> str:
        if self.read_status is None:
            return 'unknown'
        elif self.read_status == 0:
            return 'unread'
        else:
            return 'read'

    def get_details(self) -> str:
        return f'ID: {self.message_id}, Time: {self.message_time}, Type: {self.message_type}, Title: {self.title}, ' \
            + f'Content: {self.content}, Status: {self.get_read_status_str()}, Sender: {self.sender}, VIN: {self.vin}'


def convert(message: Message) -> SaicMessage:
    if message.content is not None:
        content = message.content.decode()
    else:
        content = None
    return SaicMessage(message.message_id, message.message_type, message.title.decode(),
                       message.message_time.get_timestamp(), message.sender.decode(), content, message.read_status,
                       message.vin)


class SaicApiException(Exception):
    def __init__(self, msg: str, return_code: int = None):
        if return_code is not None:
            self.message = f'return code: {return_code}, message: {msg}'
        else:
            self.message = msg

    def __str__(self):
        return self.message


class SaicApi:
    def __init__(self, saic_uri: str, saic_user: str, saic_password: str, relogin_delay: int = None):
        self.saic_uri = saic_uri
        self.saic_user = saic_user
        self.saic_password = saic_password
        if relogin_delay is None:
            self.relogin_delay = 0
        else:
            self.relogin_delay = relogin_delay
        self.message_v1_1_coder = MessageCoderV11()
        self.message_V2_1_coder = MessageCoderV21()
        self.message_V3_0_coder = MessageCoderV30()
        self.cookies = None
        self.uid = ''
        self.token = ''
        self.token_expiration = None
        self.on_publish_raw_value = None
        self.on_publish_json_value = None

    def login(self) -> MessageV11:
        application_data = MpUserLoggingInReq()
        application_data.password = self.saic_password
        header = Header()
        header.protocol_version = 17
        login_request_message = MessageV11(header, MessageBodyV11(), application_data)
        application_id = '501'
        application_data_protocol_version = 513
        self.message_v1_1_coder.initialize_message(
            UID_INIT[len(self.saic_user):] + self.saic_user,
            cast(str, None),
            application_id,
            application_data_protocol_version,
            1,
            login_request_message)
        self.publish_json_request(application_id, application_data_protocol_version, login_request_message.get_data())
        login_request_hex = self.message_v1_1_coder.encode_request(login_request_message)
        self.publish_raw_request(application_id, application_data_protocol_version, login_request_hex)
        login_response_hex = self.send_request(login_request_hex,
                                               urllib.parse.urljoin(self.saic_uri, '/TAP.Web/ota.mp'))
        self.publish_raw_response(application_id, application_data_protocol_version, login_response_hex)
        logging_in_rsp = MpUserLoggingInRsp()
        login_response_message = MessageV11(header, MessageBodyV11(), logging_in_rsp)
        self.message_v1_1_coder.decode_response(login_response_hex, login_response_message)
        self.publish_json_response(application_id, application_data_protocol_version, login_response_message.get_data())
        if login_response_message.body.error_message is not None:
            raise SaicApiException(login_response_message.body.error_message.decode(),
                                   login_response_message.body.result)
        else:
            self.uid = login_response_message.body.uid
            self.token = logging_in_rsp.token
            if logging_in_rsp.token_expiration is not None:
                self.token_expiration = logging_in_rsp.token_expiration
        return login_response_message

    def set_geofence_alarm_switch(self) -> None:
        return self.set_alarm_switches(
            [create_alarm_switch(MpAlarmSettingType.REGION)],
            pin='22222222222222222222222222222222'
        )

    def set_alarm_switches(self, alarm_switches: list, pin: str = None) -> None:
        alarm_switch_req = AlarmSwitchReq()
        alarm_switch_req.alarm_switch_list = alarm_switches
        alarm_switch_req.pin = hash_md5('123456') if pin is None else pin

        header = Header()
        header.protocol_version = 17
        alarm_switch_req_message = MessageV11(header, MessageBodyV11(), alarm_switch_req)
        application_id = '521'
        application_data_protocol_version = 513
        self.message_v1_1_coder.initialize_message(
            self.uid,
            self.get_token(),
            application_id,
            application_data_protocol_version,
            1,
            alarm_switch_req_message)
        self.publish_json_request(application_id, application_data_protocol_version,
                                  alarm_switch_req_message.get_data())
        alarm_switch_request_hex = self.message_v1_1_coder.encode_request(alarm_switch_req_message)
        self.publish_raw_request(application_id, application_data_protocol_version, alarm_switch_request_hex)
        alarm_switch_response_hex = self.send_request(alarm_switch_request_hex,
                                                      urllib.parse.urljoin(self.saic_uri, '/TAP.Web/ota.mp'))
        self.publish_raw_response(application_id, application_data_protocol_version, alarm_switch_response_hex)
        alarm_switch_response_message = MessageV11(header, MessageBodyV11())
        self.message_v1_1_coder.decode_response(alarm_switch_response_hex, alarm_switch_response_message)
        self.publish_json_response(application_id, application_data_protocol_version,
                                   alarm_switch_response_message.get_data())

        if alarm_switch_response_message.body.error_message is not None:
            raise SaicApiException(alarm_switch_response_message.body.error_message.decode(),
                                   alarm_switch_response_message.body.result)

    def get_vehicle_status(self, vin_info: VinInfo, event_id: str = None) -> MessageV2:
        vehicle_status_req = OtaRvmVehicleStatusReq()
        vehicle_status_req.veh_status_req_type = 2
        vehicle_status_req_msg = MessageV2(MessageBodyV2(), vehicle_status_req)
        application_id = '511'
        application_data_protocol_version = 25857
        self.message_V2_1_coder.initialize_message(self.uid, self.get_token(), vin_info.vin, application_id,
                                                   application_data_protocol_version, 1, vehicle_status_req_msg)
        vehicle_status_req_msg.body.ack_required = False
        if event_id is not None:
            vehicle_status_req_msg.body.event_id = event_id
        self.publish_json_request(application_id, application_data_protocol_version, vehicle_status_req_msg.get_data())
        vehicle_status_req_hex = self.message_V2_1_coder.encode_request(vehicle_status_req_msg)
        self.publish_raw_request(application_id, application_data_protocol_version, vehicle_status_req_hex)
        vehicle_status_rsp_hex = self.send_request(vehicle_status_req_hex,
                                                   urllib.parse.urljoin(self.saic_uri, '/TAP.Web/ota.mpv21'))
        self.publish_raw_response(application_id, application_data_protocol_version, vehicle_status_rsp_hex)
        vehicle_status_rsp_msg = MessageV2(MessageBodyV2(), OtaRvmVehicleStatusResp25857())
        self.message_V2_1_coder.decode_response(vehicle_status_rsp_hex, vehicle_status_rsp_msg)
        self.publish_json_response(application_id, application_data_protocol_version, vehicle_status_rsp_msg.get_data())
        return vehicle_status_rsp_msg

    def get_vehicle_status_with_retry(self, vin_info: VinInfo) -> MessageV2:
        return self.handle_retry(self.get_vehicle_status, vin_info)

    def unknown_engine_control(self, vin_info: VinInfo) -> MessageV2:
        rvc_params = []
        param1 = RvcReqParam()
        param1.param_id = 16
        param1.param_value = b'\x01'
        rvc_params.append(param1)

        return self.send_vehicle_ctrl_cmd_with_retry(vin_info, b'\x11', rvc_params, True)

    def lock_vehicle(self, vin_info: VinInfo) -> MessageV2:
        rvc_params = []
        return self.send_vehicle_ctrl_cmd_with_retry(vin_info, b'\x01', rvc_params, False)

    def unlock_vehicle(self, vin_info: VinInfo) -> MessageV2:
        rvc_params = []
        param1 = RvcReqParam()
        param1.param_id = 4
        param1.param_value = b'\x00'
        rvc_params.append(param1)

        param2 = RvcReqParam()
        param2.param_id = 5
        param2.param_value = b'\x00'
        rvc_params.append(param2)

        param3 = RvcReqParam()
        param3.param_id = 6
        param3.param_value = b'\x00'
        rvc_params.append(param3)

        param4 = RvcReqParam()
        param4.param_id = 7
        param4.param_value = b'\x03'
        rvc_params.append(param4)

        param5 = RvcReqParam()
        param5.param_id = 255
        param5.param_value = b'\x00'
        rvc_params.append(param5)

        return self.send_vehicle_ctrl_cmd_with_retry(vin_info, b'\x02', rvc_params, False)

    def start_rear_window_heat(self, vin_info: VinInfo) -> MessageV2:
        return self.__control_rear_window_heat(vin_info, True)

    def stop_rear_window_heat(self, vin_info: VinInfo) -> MessageV2:
        return self.__control_rear_window_heat(vin_info, False)

    def __control_rear_window_heat(self, vin_info: VinInfo, enable: bool) -> MessageV2:
        rvc_params = []
        param1 = RvcReqParam()
        param1.param_id = 23
        param1.param_value = bool_to_bit(enable)
        rvc_params.append(param1)

        param2 = RvcReqParam()
        param2.param_id = 255
        param2.param_value = b'\x00'
        rvc_params.append(param2)

        return self.send_vehicle_ctrl_cmd_with_retry(vin_info, b'\x20', rvc_params, False)

    def control_heated_seats(self, vin_info: VinInfo, driver_side=True, passenger_side=True):
        rcv_params = []
        param1 = RvcReqParam()
        param1.param_id = 17
        param1.param_value = bool_to_bit(driver_side)
        rcv_params.append(param1)

        param2 = RvcReqParam()
        param2.param_id = 18
        param2.param_value = bool_to_bit(passenger_side)
        rcv_params.append(param2)

        param3 = RvcReqParam()
        param3.param_id = 255
        param3.param_value = b'\x00'
        rcv_params.append(param3)
        return self.send_vehicle_ctrl_cmd_with_retry(vin_info, b'\x05', rcv_params, True)

    def start_ac(self, vin_info: VinInfo) -> MessageV2:
        rcv_params = []
        param1 = RvcReqParam()
        param1.param_id = 19
        param1.param_value = b'\x02'
        rcv_params.append(param1)

        param2 = RvcReqParam()
        param2.param_id = 20
        param2.param_value = b'\x08'
        rcv_params.append(param2)

        param3 = RvcReqParam()
        param3.param_id = 255
        param3.param_value = b'\x00'
        rcv_params.append(param3)

        return self.send_vehicle_ctrl_cmd_with_retry(vin_info, b'\x06', rcv_params, True)

    def stop_ac(self, vin_info: VinInfo) -> MessageV2:
        return self.control_climate(vin_info, fan_speed=0, ac_on=False, temperature_idx=0)

    def start_ac_blowing(self, vin_info: VinInfo) -> MessageV2:
        return self.control_climate(vin_info, fan_speed=1, ac_on=False, temperature_idx=0)

    def stop_ac_blowing(self, vin_info: VinInfo) -> MessageV2:
        rcv_params = []
        param1 = RvcReqParam()
        param1.param_id = 19
        param1.param_value = b'\x00'
        rcv_params.append(param1)

        param2 = RvcReqParam()
        param2.param_id = 20
        param2.param_value = b'\x00'
        rcv_params.append(param2)

        param3 = RvcReqParam()
        param3.param_id = 22
        param3.param_value = b'\x00'
        rcv_params.append(param3)

        param4 = RvcReqParam()
        param4.param_id = 255
        param4.param_value = b'\x00'
        rcv_params.append(param4)

        return self.send_vehicle_ctrl_cmd_with_retry(vin_info, b'\x06', rcv_params, True)

    def start_front_defrost(self, vin_info: VinInfo) -> MessageV2:
        return self.control_climate(vin_info, fan_speed=5, ac_on=True, temperature_idx=8)

    def stop_front_defrost(self, vin_info: VinInfo) -> MessageV2:
        rcv_params = []
        param1 = RvcReqParam()
        param1.param_id = 19
        param1.param_value = b'\x00'
        rcv_params.append(param1)

        param2 = RvcReqParam()
        param2.param_id = 20
        param2.param_value = b'\x08'
        rcv_params.append(param2)

        param3 = RvcReqParam()
        param3.param_id = 22
        param3.param_value = b'\x00'
        rcv_params.append(param3)

        param4 = RvcReqParam()
        param4.param_id = 255
        param4.param_value = b'\x00'
        rcv_params.append(param4)

        return self.send_vehicle_ctrl_cmd_with_retry(vin_info, b'\x06', rcv_params, True)

    def control_climate(
            self,
            vin_info: VinInfo,
            fan_speed: int = 5,
            ac_on: bool = True,
            temperature_idx: int = 8
    ) -> MessageV2:

        if fan_speed < 0 or fan_speed > 5:
            raise Exception('fan_speed must be between 0 and 5')

        if temperature_idx < 0 or temperature_idx > 14:
            raise Exception('temperature_idx must be between 0 and 14')

        if fan_speed == 0:
            ac_on = False
            temperature_idx = 8

        rcv_params = []
        param1 = RvcReqParam()
        param1.param_id = 19
        param1.param_value = fan_speed.to_bytes(1, 'big')
        rcv_params.append(param1)

        if fan_speed > 0:
            param2 = RvcReqParam()
            param2.param_id = 20
            param2.param_value = temperature_idx.to_bytes(1, 'big')
            rcv_params.append(param2)

        param3 = RvcReqParam()
        param3.param_id = 22
        param3.param_value = bool_to_bit(ac_on)
        rcv_params.append(param3)

        param4 = RvcReqParam()
        param4.param_id = 255
        param4.param_value = b'\x00'
        rcv_params.append(param4)
        return self.send_vehicle_ctrl_cmd_with_retry(vin_info, b'\x06', rcv_params, True)

    def close_driver_window(self, vin_info: VinInfo) -> MessageV2:
        rcv_params = []
        param1 = RvcReqParam()
        param1.param_id = 9
        param1.param_value = b'\x01'
        rcv_params.append(param1)

        for i in [10, 11, 12, 13, 255]:
            param = RvcReqParam()
            param.param_id = i
            param.param_value = b'\x00'
            rcv_params.append(param)

        return self.send_vehicle_ctrl_cmd_with_retry(vin_info, b'\x03', rcv_params, False)

    def control_sunroof(self, should_open: bool, vin_info: VinInfo) -> MessageV2:
        rcv_params = []
        param1 = RvcReqParam()
        param1.param_id = 8
        param1.param_value = b'\x01'
        rcv_params.append(param1)

        for i in [9, 10, 11, 12, 255]:
            param = RvcReqParam()
            param.param_id = i
            param.param_value = b'\x00'
            rcv_params.append(param)

        param = RvcReqParam()
        param.param_id = 13
        param.param_value = b'\x03' if should_open else b'\x00'
        rcv_params.append(param)

        return self.send_vehicle_ctrl_cmd_with_retry(vin_info, b'\x03', rcv_params, True)

    def open_door_locks(self, vin_info: VinInfo) -> MessageV2:
        return self.__open_vehicle_lock(vin_info, 3)

    def open_tailgate(self, vin_info: VinInfo) -> MessageV2:
        return self.__open_vehicle_lock(vin_info, 2)

    def __open_vehicle_lock(self, vin_info: VinInfo, lock_id: int) -> MessageV2:
        rcv_params = []

        for i in [4, 5, 6, 255]:
            param = RvcReqParam()
            param.param_id = i
            param.param_value = b'\x00'
            rcv_params.append(param)

        param1 = RvcReqParam()
        param1.param_id = 7
        param1.param_value = lock_id.to_bytes(1, 'big')
        rcv_params.append(param1)

        return self.send_vehicle_ctrl_cmd_with_retry(vin_info, b'\x02', rcv_params, False)

    def find_my_car(self, vin_info: VinInfo, with_horn: bool = True, with_lights: bool = True) -> MessageV2:
        rcv_params = []

        param = RvcReqParam()
        param.param_id = 1
        param.param_value = b'\x01'
        rcv_params.append(param)

        param = RvcReqParam()
        param.param_id = 2
        param.param_value = bool_to_bit(with_horn)
        rcv_params.append(param)

        param = RvcReqParam()
        param.param_id = 3
        param.param_value = bool_to_bit(with_lights)
        rcv_params.append(param)

        param = RvcReqParam()
        param.param_id = 255
        param.param_value = b'\x00'
        rcv_params.append(param)

        return self.send_vehicle_ctrl_cmd_with_retry(vin_info, b'\x00', rcv_params, True)

    def send_vehicle_ctrl_cmd_with_retry(self, vin_info: VinInfo, rvc_req_type: bytes, rvc_params: list,
                                         has_app_data: bool) -> MessageV2:
        vehicle_control_cmd_rsp_msg = self.send_vehicle_control_command(vin_info, rvc_req_type, rvc_params)

        if has_app_data:
            while vehicle_control_cmd_rsp_msg.application_data is None:
                if vehicle_control_cmd_rsp_msg.body.error_message is not None:
                    self.handle_error(vehicle_control_cmd_rsp_msg.body)
                else:
                    LOG.debug('API request returned no application data and no error message.')
                    time.sleep(float(AVG_SMS_DELIVERY_TIME))

                event_id = vehicle_control_cmd_rsp_msg.body.event_id
                vehicle_control_cmd_rsp_msg = self.send_vehicle_control_command(vin_info, rvc_req_type, rvc_params,
                                                                                event_id)
        else:
            retry = 1
            while (
                    vehicle_control_cmd_rsp_msg.body.error_message is not None
                    and retry <= 3
            ):
                self.handle_error(vehicle_control_cmd_rsp_msg.body)
                event_id = vehicle_control_cmd_rsp_msg.body.event_id
                vehicle_control_cmd_rsp_msg = self.send_vehicle_control_command(vin_info, rvc_req_type, rvc_params,
                                                                                event_id)
                retry += 1
            if vehicle_control_cmd_rsp_msg.body.error_message is not None:
                raise SaicApiException(vehicle_control_cmd_rsp_msg.body.error_message.decode(),
                                       vehicle_control_cmd_rsp_msg.body.result)
        return vehicle_control_cmd_rsp_msg

    def get_message_list_with_retry(self) -> list:
        message_list_rsp_msg = self.handle_retry(self.get_message_list)

        result = []
        if message_list_rsp_msg.application_data is not None:
            message_list_rsp = cast(MessageListResp, message_list_rsp_msg.application_data)
            for message in message_list_rsp.messages:
                result.append(convert(message))
        return result

    def handle_retry(self, func, vin_info: VinInfo = None):
        if vin_info:
            rsp = func(vin_info)
        else:
            rsp = func()
        rsp_msg = cast(AbstractMessage, rsp)
        while rsp_msg.application_data is None:
            if rsp_msg.body.error_message is not None:
                self.handle_error(rsp_msg.body)
            else:
                LOG.debug('API request returned no application data and no error message.')
                time.sleep(float(AVG_SMS_DELIVERY_TIME))

            if vin_info:
                rsp_msg = func(vin_info, rsp_msg.body.event_id)
            else:
                rsp_msg = func(rsp_msg.body.event_id)
        return rsp_msg

    def send_vehicle_control_command(self, vin_info: VinInfo, rvc_req_type: bytes, rvc_params: list,
                                     event_id: str = None) -> MessageV2:
        vehicle_control_req = OtaRvcReq()
        vehicle_control_req.rvc_req_type = rvc_req_type
        for p in rvc_params:
            param = cast(RvcReqParam, p)
            vehicle_control_req.rvc_params.append(param)

        vehicle_control_cmd_req_msg = MessageV2(MessageBodyV2(), vehicle_control_req)
        application_id = '510'
        application_data_protocol_version = 25857
        self.message_V2_1_coder.initialize_message(self.uid, self.get_token(), vin_info.vin, application_id,
                                                   application_data_protocol_version, 1, vehicle_control_cmd_req_msg)
        vehicle_control_cmd_req_msg.body.ack_required = False
        if event_id is not None:
            vehicle_control_cmd_req_msg.body.event_id = event_id
        self.publish_json_request(application_id, application_data_protocol_version,
                                  vehicle_control_cmd_req_msg.get_data())
        vehicle_control_cmd_req_msg_hex = self.message_V2_1_coder.encode_request(vehicle_control_cmd_req_msg)
        self.publish_raw_request(application_id, application_data_protocol_version, vehicle_control_cmd_req_msg_hex)
        vehicle_control_cmd_rsp_msg_hex = self.send_request(vehicle_control_cmd_req_msg_hex,
                                                            urllib.parse.urljoin(self.saic_uri, '/TAP.Web/ota.mpv21'))
        self.publish_raw_response(application_id, application_data_protocol_version, vehicle_control_cmd_rsp_msg_hex)
        vehicle_control_cmd_rsp_msg = MessageV2(MessageBodyV2(), OtaRvcStatus25857())
        self.message_V2_1_coder.decode_response(vehicle_control_cmd_rsp_msg_hex, vehicle_control_cmd_rsp_msg)
        self.publish_json_response(application_id, application_data_protocol_version,
                                   vehicle_control_cmd_rsp_msg.get_data())
        return vehicle_control_cmd_rsp_msg

    # CHARGING MANAGEMENT

    def get_charging_status(self, vin_info: VinInfo, event_id: str = None) -> MessageV30:
        chrg_mgmt_data_req_msg = MessageV30(MessageBodyV30())
        application_id = '516'
        application_data_protocol_version = 768
        self.message_V3_0_coder.initialize_message(self.uid, self.get_token(), vin_info.vin, application_id,
                                                   application_data_protocol_version, 5, chrg_mgmt_data_req_msg)
        chrg_mgmt_data_req_msg.body.ack_required = False
        if event_id is not None:
            chrg_mgmt_data_req_msg.body.event_id = event_id
        self.publish_json_request(application_id, application_data_protocol_version, chrg_mgmt_data_req_msg.get_data())
        chrg_mgmt_data_req_hex = self.message_V3_0_coder.encode_request(chrg_mgmt_data_req_msg)
        self.publish_raw_request(application_id, application_data_protocol_version, chrg_mgmt_data_req_hex)
        chrg_mgmt_data_rsp_hex = self.send_request(chrg_mgmt_data_req_hex,
                                                   urllib.parse.urljoin(self.saic_uri, '/TAP.Web/ota.mpv30'))
        self.publish_raw_response(application_id, application_data_protocol_version, chrg_mgmt_data_rsp_hex)
        chrg_mgmt_data_rsp_msg = MessageV30(MessageBodyV30(), OtaChrgMangDataResp())
        self.message_V3_0_coder.decode_response(chrg_mgmt_data_rsp_hex, chrg_mgmt_data_rsp_msg)
        self.publish_json_response(application_id, application_data_protocol_version, chrg_mgmt_data_rsp_msg.get_data())
        return chrg_mgmt_data_rsp_msg

    def get_charging_status_with_retry(self, vin_info: VinInfo) -> MessageV30:
        return self.handle_retry(self.get_charging_status, vin_info)

    def control_battery_heating(self, enable: bool, vin_info: VinInfo, event_id: str = None) -> MessageV30:
        chrg_heat_req = OtaChrgHeatReq()
        chrg_heat_req.ptcHeatReq = bool_to_int(enable)
        chrg_heat_req_msg = MessageV30(MessageBodyV30(), chrg_heat_req)
        application_id = '516'
        application_data_protocol_version = 768
        self.message_V3_0_coder.initialize_message(self.uid, self.get_token(), vin_info.vin, application_id,
                                                   application_data_protocol_version, 9, chrg_heat_req_msg)
        if event_id is not None:
            chrg_heat_req_msg.body.event_id = event_id
        self.publish_json_request(application_id, application_data_protocol_version, chrg_heat_req_msg.get_data())
        chrg_heat_req_msg_hex = self.message_V3_0_coder.encode_request(chrg_heat_req_msg)
        self.publish_raw_request(application_id, application_data_protocol_version, chrg_heat_req_msg_hex)
        chrg_heat_rsp_msg_hex = self.send_request(chrg_heat_req_msg_hex,
                                                  urllib.parse.urljoin(self.saic_uri, '/TAP.Web/ota.mpv30'))
        self.publish_raw_response(application_id, application_data_protocol_version, chrg_heat_rsp_msg_hex)
        chrg_heat_rsp_msg = MessageV30(MessageBodyV30(), OtaChrgHeatResp())
        self.message_V3_0_coder.decode_response(chrg_heat_rsp_msg_hex, chrg_heat_rsp_msg)
        self.publish_json_response(application_id, application_data_protocol_version, chrg_heat_rsp_msg.get_data())
        return chrg_heat_rsp_msg

    def control_charging_port_lock(self, unlock: bool, vin_info: VinInfo, event_id: str = None):
        chrg_ctrl_req = OtaChrgCtrlReq()
        chrg_ctrl_req.chrgCtrlReq = 0
        chrg_ctrl_req.tboxV2XReq = 0
        chrg_ctrl_req.tboxEleccLckCtrlReq = 2 if unlock else 1
        chrg_ctrl_req_msg = MessageV30(MessageBodyV30(), chrg_ctrl_req)
        application_id = '516'
        application_data_protocol_version = 768
        self.message_V3_0_coder.initialize_message(self.uid, self.get_token(), vin_info.vin, application_id,
                                                   application_data_protocol_version, 7, chrg_ctrl_req_msg)
        if event_id is not None:
            chrg_ctrl_req_msg.body.event_id = event_id
        self.publish_json_request(application_id, application_data_protocol_version, chrg_ctrl_req_msg.get_data())
        chrg_ctrl_req_msg_hex = self.message_V3_0_coder.encode_request(chrg_ctrl_req_msg)
        self.publish_raw_request(application_id, application_data_protocol_version, chrg_ctrl_req_msg_hex)
        chrg_ctrl_rsp_msg_hex = self.send_request(chrg_ctrl_req_msg_hex,
                                                  urllib.parse.urljoin(self.saic_uri, '/TAP.Web/ota.mpv30'))
        self.publish_raw_response(application_id, application_data_protocol_version, chrg_ctrl_rsp_msg_hex)
        chrg_ctrl_rsp_msg = MessageV30(MessageBodyV30(), OtaChrgCtrlStsResp())
        self.message_V3_0_coder.decode_response(chrg_ctrl_rsp_msg_hex, chrg_ctrl_rsp_msg)
        self.publish_json_response(application_id, application_data_protocol_version, chrg_ctrl_rsp_msg.get_data())
        return chrg_ctrl_rsp_msg

    def control_charging(self, stop_charging: bool, vin_info: VinInfo, event_id: str = None) -> MessageV30:
        chrg_ctrl_req = OtaChrgCtrlReq()
        chrg_ctrl_req.chrgCtrlReq = 2 if stop_charging else 1
        chrg_ctrl_req.tboxV2XReq = 0
        chrg_ctrl_req.tboxEleccLckCtrlReq = 0
        chrg_ctrl_req_msg = MessageV30(MessageBodyV30(), chrg_ctrl_req)
        application_id = '516'
        application_data_protocol_version = 768
        self.message_V3_0_coder.initialize_message(self.uid, self.get_token(), vin_info.vin, application_id,
                                                   application_data_protocol_version, 7, chrg_ctrl_req_msg)
        if event_id is not None:
            chrg_ctrl_req_msg.body.event_id = event_id
        self.publish_json_request(application_id, application_data_protocol_version, chrg_ctrl_req_msg.get_data())
        chrg_ctrl_req_msg_hex = self.message_V3_0_coder.encode_request(chrg_ctrl_req_msg)
        self.publish_raw_request(application_id, application_data_protocol_version, chrg_ctrl_req_msg_hex)
        chrg_ctrl_rsp_msg_hex = self.send_request(chrg_ctrl_req_msg_hex,
                                                  urllib.parse.urljoin(self.saic_uri, '/TAP.Web/ota.mpv30'))
        self.publish_raw_response(application_id, application_data_protocol_version, chrg_ctrl_rsp_msg_hex)
        chrg_ctrl_rsp_msg = MessageV30(MessageBodyV30(), OtaChrgCtrlStsResp())
        self.message_V3_0_coder.decode_response(chrg_ctrl_rsp_msg_hex, chrg_ctrl_rsp_msg)
        self.publish_json_response(application_id, application_data_protocol_version, chrg_ctrl_rsp_msg.get_data())
        return chrg_ctrl_rsp_msg

    def start_charging(self, vin_info: VinInfo, event_id: str = None) -> MessageV30:
        return self.control_charging(False, vin_info, event_id)

    def start_charging_with_retry(self, vin_info: VinInfo) -> MessageV30:
        return self.handle_retry(self.start_charging, vin_info)

    def set_target_battery_soc(self, target_soc: TargetBatteryCode, vin_info: VinInfo, event_id: str = None):
        chrg_setng_req = OtaChrgSetngReq()
        chrg_setng_req.onBdChrgTrgtSOCReq = target_soc.value
        chrg_setng_req.altngChrgCrntReq = 4
        chrg_setng_req.tboxV2XSpSOCReq = 0
        chrg_setng_req_msg = MessageV30(MessageBodyV30(), chrg_setng_req)
        application_id = '516'
        application_data_protocol_version = 768
        self.message_V3_0_coder.initialize_message(self.uid, self.get_token(), vin_info.vin, application_id,
                                                   application_data_protocol_version, 3, chrg_setng_req_msg)
        if event_id is not None:
            chrg_setng_req_msg.body.event_id = event_id
        self.publish_json_request(application_id, application_data_protocol_version, chrg_setng_req_msg.get_data())
        chrg_setng_req_msg_hex = self.message_V3_0_coder.encode_request(chrg_setng_req_msg)
        self.publish_raw_request(application_id, application_data_protocol_version, chrg_setng_req_msg_hex)
        chrg_setng_rsp_msg_hex = self.send_request(chrg_setng_req_msg_hex,
                                                   urllib.parse.urljoin(self.saic_uri, '/TAP.Web/ota.mpv30'))
        self.publish_raw_response(application_id, application_data_protocol_version, chrg_setng_rsp_msg_hex)
        chrg_setng_rsp_msg = MessageV30(MessageBodyV30(), OtaChrgSetngResp())
        self.message_V3_0_coder.decode_response(chrg_setng_rsp_msg_hex, chrg_setng_rsp_msg)
        self.publish_json_response(application_id, application_data_protocol_version, chrg_setng_rsp_msg.get_data())
        return chrg_setng_rsp_msg

    def set_schedule_charging(self, start_time: datetime.time, end_time: datetime.time,
                              mode: ScheduledChargingMode,
                              vin_info: VinInfo,
                              event_id: str = None):
        start_hour = start_time.hour
        start_minute = start_time.minute
        end_hour = end_time.hour
        end_minute = end_time.minute
        mode_value = mode.value
        chrg_rsvan_req = OtaChrgRsvanReq()
        chrg_rsvan_req.rsvanStHour = start_hour
        chrg_rsvan_req.rsvanStMintu = start_minute
        chrg_rsvan_req.rsvanSpHour = end_hour
        chrg_rsvan_req.rsvanSpMintu = end_minute
        chrg_rsvan_req.tboxAdpPubChrgSttnReq = 1
        chrg_rsvan_req.tboxReserCtrlReq = mode_value
        chrg_rsvan_msg = MessageV30(MessageBodyV30(), chrg_rsvan_req)
        application_id = '516'
        application_data_protocol_version = 768
        self.message_V3_0_coder.initialize_message(self.uid, self.get_token(), vin_info.vin, application_id,
                                                   application_data_protocol_version, 1, chrg_rsvan_msg)
        if event_id is not None:
            chrg_rsvan_msg.body.event_id = event_id
        self.publish_json_request(application_id, application_data_protocol_version, chrg_rsvan_msg.get_data())
        chrg_rsvan_req_msg_hex = self.message_V3_0_coder.encode_request(chrg_rsvan_msg)
        self.publish_raw_request(application_id, application_data_protocol_version, chrg_rsvan_req_msg_hex)
        chrg_rsvan_rsp_msg_hex = self.send_request(chrg_rsvan_req_msg_hex,
                                                   urllib.parse.urljoin(self.saic_uri, '/TAP.Web/ota.mpv30'))
        self.publish_raw_response(application_id, application_data_protocol_version, chrg_rsvan_rsp_msg_hex)
        chrg_rsvan_rsp_msg = MessageV30(MessageBodyV30(), OtaChrgRsvanResp())
        self.message_V3_0_coder.decode_response(chrg_rsvan_rsp_msg_hex, chrg_rsvan_rsp_msg)
        self.publish_json_response(application_id, application_data_protocol_version, chrg_rsvan_rsp_msg.get_data())
        return chrg_rsvan_rsp_msg

    # Messages
    def get_message_list(self, event_id: str = None) -> MessageV11:
        return self.get_alarm_list(1, 5, event_id)

    def get_alarm_list(self, start: int, end: int, event_id: str = None) -> MessageV11:
        return self.__get_message_list_of_group(start, end, 'ALARM', event_id)

    def get_command_list(self, start: int, end: int, event_id: str = None) -> MessageV11:
        return self.__get_message_list_of_group(start, end, 'COMMAND', event_id)

    def get_news_list(self, start: int, end: int, event_id: str = None) -> MessageV11:
        return self.__get_message_list_of_group(start, end, 'NEWS', event_id)

    def __get_message_list_of_group(self, start: int, end: int, message_group: str, event_id: str = None) -> MessageV11:
        message_list_request = MessageListReq()
        message_list_request.start_end_number = StartEndNumber()
        message_list_request.start_end_number.start_number = start
        message_list_request.start_end_number.end_number = end
        message_list_request.message_group = message_group

        header = Header()
        header.protocol_version = 18
        message_body = MessageBodyV11()
        message_list_req_msg = MessageV11(header, message_body, message_list_request)
        application_id = '531'
        application_data_protocol_version = 513
        self.message_v1_1_coder.initialize_message(self.uid, self.get_token(), application_id,
                                                   application_data_protocol_version, 1, message_list_req_msg)
        if event_id is not None:
            message_body.event_id = event_id
        self.publish_json_request(application_id, application_data_protocol_version, message_list_req_msg.get_data())
        message_list_req_hex = self.message_v1_1_coder.encode_request(message_list_req_msg)
        self.publish_raw_request(application_id, application_data_protocol_version, message_list_req_hex)
        message_list_rsp_hex = self.send_request(message_list_req_hex,
                                                 urllib.parse.urljoin(self.saic_uri, '/TAP.Web/ota.mp'))
        self.publish_raw_response(application_id, application_data_protocol_version, message_list_rsp_hex)
        message_list_rsp_msg = MessageV11(header, MessageBodyV11(), MessageListResp())
        self.message_v1_1_coder.decode_response(message_list_rsp_hex, message_list_rsp_msg)
        self.publish_json_response(application_id, application_data_protocol_version, message_list_rsp_msg.get_data())
        return message_list_rsp_msg

    def delete_all_alarms(self, event_id: str = None):
        self.__change_message_status(None, 'DELETE_ALARM', event_id)

    def delete_all_commands(self, event_id: str = None):
        self.__change_message_status(None, 'DELETE_COMMAND', event_id)

    def delete_all_news(self, event_id: str = None):
        self.__change_message_status(None, 'DELETE_NEWS', event_id)

    def read_message(self, message_id: int, event_id: str = None):
        self.__change_message_status(message_id, 'READ', event_id)

    def delete_message(self, message_id: int, event_id: str = None):
        self.__change_message_status(message_id, 'DELETE', event_id)

    def __change_message_status(self, message_id: int | None, action_type: str, event_id: str = None):
        abort_send_msg_req = AbortSendMessageReq()
        abort_send_msg_req.action_type = action_type
        if message_id is not None:
            abort_send_msg_req.message_id = message_id

        header = Header()
        header.protocol_version = 17
        message_body = MessageBodyV11()
        message_delete_req_msg = MessageV11(header, message_body, abort_send_msg_req)
        application_id = '615'
        application_protocol_version = 513
        self.message_v1_1_coder.initialize_message(self.uid, self.get_token(), application_id,
                                                   application_protocol_version, 1, message_delete_req_msg)
        if event_id is not None:
            message_body.event_id = event_id
        self.publish_json_request(application_id, application_protocol_version, abort_send_msg_req.get_data())
        message_delete_req_hex = self.message_v1_1_coder.encode_request(message_delete_req_msg)
        self.publish_raw_request(application_id, application_protocol_version, message_delete_req_hex)
        message_delete_rsp_hex = self.send_request(message_delete_req_hex,
                                                   urllib.parse.urljoin(self.saic_uri, '/TAP.Web/ota.mp'))
        self.publish_raw_response(application_id, application_protocol_version, message_delete_rsp_hex)
        message_delete_rsp_msg = MessageV11(header, MessageBodyV11())
        self.message_v1_1_coder.decode_response(message_delete_rsp_hex, message_delete_rsp_msg)
        self.publish_json_response(application_id, application_protocol_version, message_delete_rsp_msg.get_data())
        if message_delete_rsp_msg.body.error_message is not None:
            raise SaicApiException(message_delete_rsp_msg.body.error_message.decode(),
                                   message_delete_rsp_msg.body.result)

    def publish_raw_value(self, key: str, raw: str):
        if self.on_publish_raw_value is not None:
            self.on_publish_raw_value(key, raw)
        else:
            LOG.debug(f'{key}: {raw}')

    def publish_raw_request(self, application_id: str, application_data_protocol_version: int, raw: str):
        key = f'{application_id}_{application_data_protocol_version}/raw/request'
        self.publish_raw_value(key, raw)

    def publish_raw_response(self, application_id: str, application_data_protocol_version: int, raw: str):
        key = f'{application_id}_{application_data_protocol_version}/raw/response'
        self.publish_raw_value(key, raw)

    def publish_json_request(self, application_id: str, application_data_protocol_version: int, data: dict):
        key = f'{application_id}_{application_data_protocol_version}/json/request'
        self.publish_json(key, data)

    def publish_json_response(self, application_id: str, application_data_protocol_version: int, data: dict):
        key = f'{application_id}_{application_data_protocol_version}/json/response'
        self.publish_json(key, data)

    def publish_json(self, key: str, data: dict):
        if self.on_publish_json_value is not None:
            self.on_publish_json_value(key, data)
        else:
            LOG.debug(f'{key}: {data}')

    def send_request(self, hex_message: str, endpoint) -> str:
        headers = {
            'Accept': '*/*',
            'Content-Type': 'text/html',
            'Accept-Encoding': 'gzip, deflate, br',
            'User-Agent': 'MG iSMART/1.1.1 (iPhone; iOS 16.3; Scale/3.00)',
            'Accept-Language': 'de-DE;q=1, en-DE;q=0.9, lu-DE;q=0.8, fr-DE;q=0.7',
            'Content-Length': str(len(hex_message))
        }
        try:
            response = requests.post(url=endpoint, data=hex_message, headers=headers, cookies=self.cookies)
            self.cookies = response.cookies
            return response.content.decode()
        except requests.exceptions.ConnectionError as ece:
            raise SaicApiException(f'Connection error: {ece}')
        except requests.exceptions.Timeout as et:
            raise SaicApiException(f'Timeout error: {et}')
        except requests.exceptions.HTTPError as ehttp:
            status_code = ehttp.response.status_code
            raise SaicApiException(f'HTTP error. HTTP status: {status_code}, {ehttp}')
        except requests.exceptions.RequestException as e:
            raise SaicApiException(f'{e}')

    def get_token(self):
        if self.token_expiration is not None:
            token_expiration = cast(Timestamp, self.token_expiration)
            if token_expiration.get_timestamp() < datetime.datetime.now():
                self.login()
        return self.token

    def handle_error(self, message_body: AbstractMessageBody):
        message = f'application ID: {message_body.application_id},' \
                  + f' protocol version: {message_body.application_data_protocol_version},' \
                  + f' message: {message_body.error_message.decode()}' \
                  + f' result code: {message_body.result}'

        if message_body.result == 2:
            # re-login
            LOG.debug(message)
            if self.relogin_delay > 0:
                LOG.warning(f'The SAIC user has been logged out. '
                            + f'Waiting {self.relogin_delay} seconds before attempting another login')
                time.sleep(float(self.relogin_delay))
            self.login()
        elif message_body.result == 4:
            # The remote control instruction failed, please try again later.
            LOG.debug(message)
            time.sleep(float(AVG_SMS_DELIVERY_TIME))
        elif message_body.result == 6:
            # The service is not available,please try again later
            LOG.debug(message)
            time.sleep(float(AVG_SMS_DELIVERY_TIME))
        elif message_body.result == -1:
            LOG.warning(message)
        else:
            LOG.error(message)


def bool_to_bit(flag):
    return b'\x01' if flag else b'\x00'


def bool_to_int(flag):
    return 1 if flag else 0


def hash_md5(password: str) -> str:
    return hashlib.md5(password.encode('utf-8')).hexdigest()


def create_alarm_switch(alarm_setting_type: MpAlarmSettingType) -> AlarmSwitch:
    alarm_switch = AlarmSwitch()
    alarm_switch.alarm_setting_type = alarm_setting_type.value
    alarm_switch.alarm_switch = True
    alarm_switch.function_switch = True
    return alarm_switch
