import datetime
from enum import Enum

from saic_ismart_client.common_model import Asn1Type, ApplicationData, MessageBodyV1, MessageV1, Header

FIELD_ACTION_TYPE = 'actionType'
FIELD_SECONDS = 'seconds'
FIELD_MESSAGE_TIME = 'messageTime'
FIELD_FUNCTION_SWITCH = 'functionSwitch'
FIELD_ALARM_SWITCH = 'alarmSwitch'
FIELD_ALARM_SETTING_TYPE = 'alarmSettingType'
FIELD_DESCRIPTION = 'description'
FIELD_ALARM_SWITCH_LIST = 'alarmSwitchList'
FIELD_PIN = 'pin'
FIELD_TBOX_SIM_NO = 'tboxSimNo'
FIELD_MODEL_CONF_JSON = 'modelConfigurationJsonStr'
FIELD_COLOR_NAME = 'colorName'
FIELD_MODEL_YEAR = 'modelYear'
FIELD_CURRENT_VEHICLE = 'isCurrentVehicle'
FIELD_VEHICLE_PHOTO = 'vehiclePhoto'
FIELD_BIND_TIME = 'bindTime'
FIELD_ACTIVE = 'isAcivate'
FIELD_MODEL_NAME = 'modelName'
FIELD_BRAND_NAME = 'brandName'
FIELD_SERIES = 'series'
FIELD_NAME = 'name'
FIELD_VIN = 'vin'
FIELD_LANGUAGE_TYPE = 'languageType'
FIELD_USER_NAME = 'userName'
FIELD_USER_PHOTO = 'userPhoto'
FIELD_VIN_LIST = 'vinList'
FIELD_TOKEN_EXPIRATION = 'tokenExpiration'
FIELD_REFRESH_TOKEN = 'refreshToken'
FIELD_TOKEN = 'token'
FIELD_DEVICE_ID = 'deviceId'
FIELD_PASSWORD = 'password'
FIELD_READ_STATUS = 'readStatus'
FIELD_MESSAGE_GROUP = 'messageGroup'
FIELD_CONTENT_ID = 'contentId'
FIELD_END_NUMBER = 'endNumber'
FIELD_START_NUMBER = 'startNumber'
FIELD_CONTENT = 'content'
FIELD_CONTENT_ID_LIST = 'contentIdList'
FIELD_SENDER = 'sender'
FIELD_TITLE = 'title'
FIELD_MESSAGE_TYPE = 'messageType'
FIELD_MESSAGE_ID = 'messageId'
FIELD_MESSAGES = 'messages'
FIELD_RECORDS_NUMBER = 'recordsNumber'
FIELD_START_END_NUMBER = 'startEndNumber'


class MessageBodyV11(MessageBodyV1):
    def __init__(self):
        super().__init__('MPDispatcherBody')

    def get_data(self) -> dict:
        return super().get_data()

    def init_from_dict(self, data: dict):
        super().init_from_dict(data)


class AlarmSwitchReq(ApplicationData):
    def __init__(self):
        super().__init__('AlarmSwitchReq')
        self.pin: str | None = None  # IA5String(SIZE(32))
        self.alarm_switch_list: [AlarmSwitch] = []
        self.description: bytes | None = None  # OCTET STRING(SIZE(0..500)) OPTIONAL

    def get_data(self) -> dict:
        alarm_switch_list = []
        for alarm_switch in self.alarm_switch_list:
            alarm_switch_list.append(alarm_switch.get_data())
        data = {
            FIELD_PIN: self.pin,
            FIELD_ALARM_SWITCH_LIST: alarm_switch_list
        }
        self.add_optional_bytes_field_to_data(data, FIELD_DESCRIPTION, self.description)
        return data

    def init_from_dict(self, data: dict):
        self.pin = data.get(FIELD_PIN)
        alarm_switch_list = data.get(FIELD_ALARM_SWITCH_LIST)
        for item in alarm_switch_list:
            alarm_switch = AlarmSwitch()
            alarm_switch.init_from_dict(item)
            self.alarm_switch_list.append(alarm_switch)
        self.description = data.get(FIELD_DESCRIPTION)


class AlarmSwitch(Asn1Type):
    def __init__(self):
        super().__init__('AlarmSwitch')
        self.alarm_setting_type: MpAlarmSettingType | None = None
        self.alarm_switch: bool | None = None
        self.function_switch: bool | None = None

    def get_data(self) -> dict:
        return {
            FIELD_ALARM_SETTING_TYPE: self.alarm_setting_type,
            FIELD_ALARM_SWITCH: self.alarm_switch,
            FIELD_FUNCTION_SWITCH: self.function_switch
        }

    def init_from_dict(self, data: dict):
        self.alarm_setting_type = data.get(FIELD_ALARM_SETTING_TYPE)
        self.alarm_switch = data.get(FIELD_ALARM_SWITCH)
        self.function_switch = data.get(FIELD_FUNCTION_SWITCH)


class MpUserInfoRsp(Asn1Type):
    def __init__(self):
        super().__init__('MPUserInfoResp')
        self.nick_name: str | None = None  # OCTET STRING(SIZE(1..50)) OPTIONAL
        self.address: str | None = None  # OCTET STRING(SIZE(1..50)) OPTIONAL
        self.mobile_phone: str | None = None  # IA5String(SIZE(1..19)) OPTIONAL
        self.emergency_name: str | None = None  # OCTET STRING(SIZE(1..50)) OPTIONAL
        self.emergency_mobile: str | None = None  # IA5String(SIZE(1..19)) OPTIONAL
        self.user_photo: str | None = None  # IA5String(SIZE(1..128)) OPTIONAL
        self.gender: str | None = None  # OCTET STRING(SIZE(1)) OPTIONAL
        self.birthday: str | None = None  # IA5String(SIZE(8)) OPTIONAL
        self.language_type: int | None = None  # LanguageType OPTIONAL
        self.real_name: str | None = None  # OCTET STRING(SIZE(1..150)) OPTIONAL
        self.the_second_level_country_code: str | None = None  # IA5String(SIZE(1..100)) OPTIONAL
        self.the_third_level_country_code: str | None = None  # IA5String(SIZE(1..100)) OPTIONAL
        self.the_second_level_country_name: str | None = None  # IA5String(SIZE(1..200)) OPTIONAL
        self.the_third_level_country_name: str | None = None  # IA5String(SIZE(1..200)) OPTIONAL
        self.email: str | None = None  # IA5String(SIZE(1..50)) OPTIONAL


class MpUserLoggingInReq(ApplicationData):
    def __init__(self):
        super().__init__('MPUserLoggingInReq')
        self.password: str | None = None  # IA5String(SIZE(6..30))
        self.device_id: str | None = None  # IA5String(SIZE(1..200)) OPTIONAL

    def get_data(self) -> dict:
        data = {FIELD_PASSWORD: self.password}
        if self.device_id is not None:
            data[FIELD_DEVICE_ID] = self.device_id
        return data

    def init_from_dict(self, data: dict):
        self.password = data.get(FIELD_PASSWORD)
        self.device_id = data.get(FIELD_DEVICE_ID)


class MpUserLoggingInRsp(ApplicationData):
    def __init__(self):
        super().__init__('MPUserLoggingInResp')
        self.token: str | None = None  # IA5String(SIZE(40)) OPTIONAL
        self.refresh_token: str | None = None  # IA5String(SIZE(40)) OPTIONAL
        self.token_expiration: Timestamp | None = None
        self.vin_list: [VinInfo] = []
        self.user_photo: str | None = None  # IA5String(SIZE(1..128)) OPTIONAL
        self.user_name: str | None = None  # IA5String(SIZE(8..12))
        self.language_type: int | None = None

    def get_data(self) -> dict:
        data = {
            FIELD_USER_NAME: self.user_name
        }
        self.add_optional_field_to_data(data, FIELD_TOKEN, self.token)
        self.add_optional_field_to_data(data, FIELD_REFRESH_TOKEN, self.refresh_token)
        if self.token_expiration is not None:
            data[FIELD_TOKEN_EXPIRATION] = self.token_expiration.get_data()
        if self.vin_list is not None:
            vin_list = []
            for item in self.vin_list:
                vin_list.append(item.get_data())
            data[FIELD_VIN_LIST] = vin_list
        self.add_optional_field_to_data(data, FIELD_USER_PHOTO, self.user_photo)
        if self.language_type is not None:
            data[FIELD_LANGUAGE_TYPE] = self.language_type
        return data

    def init_from_dict(self, data: dict):
        self.token = data.get(FIELD_TOKEN)
        self.refresh_token = data.get(FIELD_REFRESH_TOKEN)
        if FIELD_TOKEN_EXPIRATION in data:
            self.token_expiration = Timestamp()
            self.token_expiration.init_from_dict(data.get(FIELD_TOKEN_EXPIRATION))
        if FIELD_VIN_LIST in data:
            vin_list = data.get(FIELD_VIN_LIST)
            for item in vin_list:
                vin_info = VinInfo()
                vin_info.init_from_dict(item)
                self.vin_list.append(vin_info)
        self.user_photo = data.get(FIELD_USER_PHOTO)
        self.user_name = data.get(FIELD_USER_NAME)
        self.language_type = data.get(FIELD_LANGUAGE_TYPE)


class Timestamp(Asn1Type):
    def __init__(self):
        super().__init__('Timestamp')
        self.seconds: int = -1  # INTEGER(0..4294967295)

    def get_data(self) -> dict:
        return {
            FIELD_SECONDS: self.seconds
        }

    def init_from_dict(self, data: dict):
        self.seconds = data.get(FIELD_SECONDS)

    def get_timestamp(self) -> datetime:
        return datetime.datetime.fromtimestamp(self.seconds)


class AppUpgradeInfoReq(Asn1Type):
    def __init__(self):
        super().__init__('APPUpgradeInfoReq')
        self.app_type = None  # APPType
        self.app_version: str | None = None  # IA5String(SIZE(1..50))


class AppUpgradeInfoRsp(Asn1Type):
    def __init__(self):
        super().__init__('APPUpgradeInfoResp')
        self.has_new_version: bool | None = None  # BOOLEAN
        self.app_version: str | None = None  # IA5String(SIZE(1..50)) OPTIONAL
        self.force_update: bool | None = None  # BOOLEAN OPTIONAL
        self.update_url: str | None = None  # IA5String(SIZE(1..200)) OPTIONAL
        self.update_info_en: bytes | None = None  # OCTET STRING(SIZE(1..500)) OPTIONAL
        self.update_info_th: bytes | None = None  # OCTET STRING(SIZE(1..500)) OPTIONAL


class MpAppAttributeRsp(Asn1Type):
    def __init__(self):
        super().__init__('MPAppAttributeResp')
        self.data_app_attribute: str | None = None  # IA5String(SIZE(1..65535)) OPTIONAL


class AdvertiseRsp(Asn1Type):
    def __init__(self):
        super().__init__('AdvertiseResp')
        self.advertise_version: int | None = None  # INTEGER(0..281474976710655) OPTIONAL
        self.advertises = []  # SEQUENCE SIZE(0..255) OF Advertise OPTIONAL


class VinInfo(Asn1Type):
    def __init__(self):
        super().__init__('VinInfo')
        self.vin: str | None = None  # IA5String(SIZE(17))
        self.name: bytes | None = None  # OCTET STRING(SIZE(1..128)) OPTIONAL
        self.series: str | None = None  # IA5String(SIZE(1..10))
        self.brand_name: bytes | None = None  # OCTET STRING(SIZE(1..24))
        self.model_name: bytes | None = None  # OCTET STRING(SIZE(1..100))
        self.vehicle_photo: str | None = None  # IA5String(SIZE(1..128)) OPTIONAL
        self.active: bool | None = None  # BOOLEAN
        self.current_vehicle: int | None = None  # INTEGER(0..10) OPTIONAL
        self.model_year: str | None = None  # IA5String(SIZE(4)) OPTIONAL
        self.color_name: bytes | None = None  # OCTET STRING(SIZE(1..50)) OPTIONAL
        self.model_configuration_json_str: str | None = None  # IA5String(SIZE(1..1024)) OPTIONAL
        self.bind_time: Timestamp | None = None
        self.tbox_sim_no: str | None = None  # IA5String(SIZE(19)) OPTIONAL

    def get_data(self) -> dict:
        data = {
            FIELD_VIN: self.vin,
            FIELD_SERIES: self.series,
            FIELD_BRAND_NAME: self.brand_name,
            FIELD_MODEL_NAME: self.model_name,
            FIELD_ACTIVE: self.active
        }
        VinInfo.add_optional_bytes_field_to_data(data, FIELD_NAME, self.name)
        self.add_optional_field_to_data(data, FIELD_VEHICLE_PHOTO, self.vehicle_photo)
        self.add_optional_field_to_data(data, FIELD_CURRENT_VEHICLE, self.current_vehicle)
        self.add_optional_field_to_data(data, FIELD_MODEL_YEAR, self.model_year)
        VinInfo.add_optional_bytes_field_to_data(data, FIELD_COLOR_NAME, self.color_name)
        self.add_optional_field_to_data(data, FIELD_MODEL_CONF_JSON, self.model_configuration_json_str)
        self.add_optional_field_to_data(data, FIELD_BIND_TIME, self.bind_time)
        self.add_optional_field_to_data(data, FIELD_TBOX_SIM_NO, self.tbox_sim_no)
        return data

    def init_from_dict(self, data: dict):
        self.vin = data.get(FIELD_VIN)
        if FIELD_NAME in data:
            self.name = data.get(FIELD_NAME)
        self.series = data.get(FIELD_SERIES)
        self.brand_name = data.get(FIELD_BRAND_NAME)
        self.model_name = data.get(FIELD_MODEL_NAME)
        self.vehicle_photo = data.get(FIELD_VEHICLE_PHOTO)
        self.active = data.get(FIELD_ACTIVE)
        self.current_vehicle = data.get(FIELD_CURRENT_VEHICLE)
        self.model_year = data.get(FIELD_MODEL_YEAR)
        if FIELD_COLOR_NAME in data:
            self.color_name = data.get(FIELD_COLOR_NAME)
        self.model_configuration_json_str = data.get(FIELD_MODEL_CONF_JSON)
        if FIELD_BIND_TIME in data:
            timestamp = Timestamp()
            timestamp.init_from_dict(data.get(FIELD_BIND_TIME))
            self.bind_time = timestamp
        self.tbox_sim_no = data.get(FIELD_TBOX_SIM_NO)


class MpAlarmSettingType(Enum):
    ABNORMAL = 'abnormal'
    MOVING = 'moving'
    REGION = 'region'
    ENGINE_START = 'engineStart'
    START_VEHICLE_STATUS = 'startVehicleStatus'
    OFF_CAR = 'offCar'
    SPEEDING = 'speeding'


class MessageListReq(ApplicationData):
    def __init__(self):
        super().__init__('MessageListReq')
        self.start_end_number: StartEndNumber | None = None
        self.message_group: str | None = None

    def get_data(self) -> dict:
        data = {
            FIELD_START_END_NUMBER: self.start_end_number.get_data()
        }
        self.add_optional_field_to_data(data, FIELD_MESSAGE_GROUP, self.message_group)
        return data

    def init_from_dict(self, data: dict):
        self.start_end_number = StartEndNumber()
        self.start_end_number.init_from_dict(data.get(FIELD_START_END_NUMBER))


class AbortSendMessageReq(ApplicationData):
    def __init__(self):
        super().__init__('AbortSendMessageReq')
        self.messages: [Message] = []  # SEQUENCE SIZE(1..256) OF Message OPTIONAL
        self.message_id: int = -1  # INTEGER(0..281474976710655) OPTIONAL
        self.action_type: str | None = None  # IA5String(SIZE(1..20)) OPTIONAL

    def get_data(self) -> dict:
        data = {}
        if len(self.messages) > 0:
            message_list = []
            for message in self.messages:
                message_list.append(message.get_data())
            data[FIELD_MESSAGES] = message_list
        if self.message_id != -1:
            data[FIELD_MESSAGE_ID] = self.message_id
        if self.action_type:
            data[FIELD_ACTION_TYPE] = self.action_type
        return data

    def init_from_dict(self, data: dict):
        if FIELD_MESSAGES in data:
            for msg in data[FIELD_MESSAGES]:
                message = Message()
                message.init_from_dict(msg)
                self.messages.append(message)
        if FIELD_MESSAGE_ID in data:
            self.message_id = data[FIELD_MESSAGE_ID]
        if FIELD_ACTION_TYPE in data:
            self.action_type = data[FIELD_ACTION_TYPE]


class Message(Asn1Type):
    def __init__(self):
        super().__init__('Message')
        self.message_id: int | None = None  # INTEGER(0..281474976710655)
        self.message_type: str | None = None  # IA5String(SIZE(3))
        self.title: str | None = None  # OCTET STRING(SIZE(1..128))
        self.message_time: Timestamp | None = None
        self.sender: str | None = None  # OCTET STRING(SIZE(1..64))
        self.content_id_list: [ContentId] = []
        self.content: str | None = None  # OCTET STRING(SIZE(1..2048)) OPTIONAL
        self.read_status: int | None = None  # INTEGER(-128..128) OPTIONAL
        self.vin: str | None = None  # IA5String(SIZE(17)) OPTIONAL

    def get_data(self) -> dict:
        data = {
            FIELD_MESSAGE_ID: self.message_id,
            FIELD_MESSAGE_TYPE: self.message_type,
            FIELD_TITLE: self.title,
            FIELD_MESSAGE_TIME: self.message_time.get_data(),
            FIELD_SENDER: self.sender
        }
        if self.content_id_list is not None:
            content_id_list = []
            for item in self.content_id_list:
                content_id_list.append(item.get_data())
            data[FIELD_CONTENT_ID] = content_id_list
        self.add_optional_field_to_data(data, FIELD_CONTENT, self.content)
        self.add_optional_field_to_data(data, FIELD_READ_STATUS, self.read_status)
        self.add_optional_field_to_data(data, FIELD_VIN, self.vin)
        return data

    def init_from_dict(self, data: dict):
        self.message_id = data.get(FIELD_MESSAGE_ID)
        self.message_type = data.get(FIELD_MESSAGE_TYPE)
        self.title = data.get(FIELD_TITLE).decode()
        self.message_time = Timestamp()
        self.message_time.init_from_dict(data.get(FIELD_MESSAGE_TIME))
        self.sender = data.get(FIELD_SENDER).decode()
        if FIELD_CONTENT_ID in data:
            for item in data.get(FIELD_CONTENT_ID):
                content_id = ContentId()
                content_id.init_from_dict(item)
                self.content_id_list.append(content_id)
        if FIELD_CONTENT in data:
            self.content = data[FIELD_CONTENT].decode()
        self.read_status = data.get(FIELD_READ_STATUS)
        self.vin = data.get(FIELD_VIN)


class MessageListResp(ApplicationData):
    def __init__(self):
        super().__init__('MessageListResp')
        self.records_number: int = 0  # INTEGER(0..281474976710655)
        self.messages: [Message] = []

    def get_data(self) -> dict:
        messages = []
        for item in self.messages:
            messages.append(item.get_data())
        return {
            FIELD_RECORDS_NUMBER: self.records_number,
            FIELD_MESSAGES: messages
        }

    def init_from_dict(self, data: dict):
        records_number = data.get(FIELD_RECORDS_NUMBER)
        if records_number > 0:
            messages = data.get(FIELD_MESSAGES)
            for item in messages:
                message = Message()
                message.init_from_dict(item)
                self.add_message(message)

    def add_message(self, message: Message):
        self.messages.append(message)
        self.records_number += 1


class StartEndNumber(Asn1Type):
    def __init__(self):
        super().__init__('StartEndNumber')
        self.start_number: int = -1  # INTEGER(0..281474976710655)
        self.end_number: int = -1  # INTEGER(0..281474976710655)

    def get_data(self) -> dict:
        return {
            FIELD_START_NUMBER: self.start_number,
            FIELD_END_NUMBER: self.end_number
        }

    def init_from_dict(self, data: dict):
        self.start_number = data.get(FIELD_START_NUMBER)
        self.end_number = data.get(FIELD_END_NUMBER)


class ContentId(Asn1Type):
    def __init__(self):
        super().__init__('ContentId')
        self.content_id = None  # INTEGER(0..281474976710655)
        self.description: str | None = None  # OCTET STRING(SIZE(1..255)) OPTIONAL

    def get_data(self) -> dict:
        data = {
            FIELD_CONTENT_ID: self.content_id
        }
        self.add_optional_field_to_data(data, FIELD_DESCRIPTION, self.description)
        return data

    def init_from_dict(self, data: dict):
        self.content_id = data.get(FIELD_CONTENT_ID)
        if FIELD_DESCRIPTION in data:
            self.description = data.get(FIELD_DESCRIPTION).decode()


class MessageV11(MessageV1):
    def __init__(self, header: Header, body: MessageBodyV11, application_data: ApplicationData = None):
        super().__init__(header, body, application_data)
