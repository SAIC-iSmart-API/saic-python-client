import io
import logging
import os
import pathlib
import time
from enum import Enum

import asn1tools
from asn1tools.compiler import Specification

logging.basicConfig(format='%(asctime)s %(message)s')
LOG = logging.getLogger(__name__)
LOG.setLevel(level=os.getenv('LOG_LEVEL', 'INFO').upper())

FIELD_ERROR_MESSAGE = 'errorMessage'
FIELD_RESULT = 'result'
FIELD_TEST_FLAG = 'testFlag'
FIELD_APPLICATION_DATA_ENCODING = 'applicationDataEncoding'
FIELD_ACK_REQUIRED = 'ackRequired'
FIELD_EVENT_ID = 'eventID'
FIELD_VIN = 'vin'
FIELD_TOKEN = 'token'
FIELD_UID = 'uid'
FIELD_APPLICATION_DATA_PROTOCOL_VERSION = 'applicationDataProtocolVersion'
FIELD_APPLICATION_DATA_LENGTH = 'applicationDataLength'
FIELD_MESSAGE_ID = 'messageID'
FIELD_EVENT_CREATION_TIME = 'eventCreationTime'
FIELD_APPLICATION_ID = 'applicationID'
FIELD_ACK_MESSAGE_COUNTER = 'ackMessageCounter'
FIELD_DL_MESSAGE_COUNTER = 'dlMessageCounter'
FIELD_UL_MESSAGE_COUNTER = 'ulMessageCounter'
FIELD_ICC_ID = 'iccID'
FIELD_HMI_LANGUAGE = 'hmiLanguage'
FIELD_NETWORK_INFO = 'networkInfo'
FIELD_BASIC_POSITION = 'basicPosition'
FIELD_CRQM_REQUEST = 'crqmRequest'
FIELD_STATE_LESS_DISPATCHER_MESSAGE = 'statelessDispatcherMessage'
FIELD_SIM_INFO = 'simInfo'
FIELD_MESSAGE_COUNTER = 'messageCounter'
FIELD_DOWNLINK_COUNTER = 'downlinkCounter'
FIELD_UPLINK_COUNTER = 'uplinkCounter'
FIELD_LONGITUDE = 'longitude'
FIELD_LATITUDE = 'latitude'
FIELD_MNC_SIM = 'mncSim'
FIELD_MCC_SIM = 'mccSim'
FIELD_MNC_NETWORK = 'mncNetwork'
FIELD_MCC_NETWORK = 'mccNetwork'
FIELD_SIGNAL_STRENGTH = 'signalStrength'


class ScheduledChargingMode(Enum):
    DISABLED = 2
    UNTIL_CONFIGURED_SOC = 3
    UNTIL_CONFIGURED_TIME = 1


class ChargeCurrentLimitCode(Enum):
    C_IGNORE = 0
    C_6A = 1
    C_8A = 2
    C_16A = 3
    C_MAX = 4

    @staticmethod
    def to_code(limit: str):
        match limit.upper():
            case "6A":
                return ChargeCurrentLimitCode.C_6A
            case "8A":
                return ChargeCurrentLimitCode.C_8A
            case "16A":
                return ChargeCurrentLimitCode.C_16A
            case "MAX":
                return ChargeCurrentLimitCode.C_MAX
            case _:
                raise ValueError(f'Unknown charge current limit: {limit}')

    def get_limit(self) -> str:
        match self:
            case ChargeCurrentLimitCode.C_6A:
                return "6A"
            case ChargeCurrentLimitCode.C_8A:
                return "8A"
            case ChargeCurrentLimitCode.C_16A:
                return "16A"
            case ChargeCurrentLimitCode.C_MAX:
                return "Max"
            case _:
                raise ValueError(f'Unknown charge current limit code: {self}')


class Header:
    def __init__(self):
        self.protocol_version = None
        self.security_context = None
        self.dispatcher_message_length = None
        self.dispatcher_body_encoding = None

    def get_body_encoding_int_value(self) -> int:
        if self.dispatcher_body_encoding == DataEncodingType.PER_UNALIGNED:
            return 0
        elif self.dispatcher_body_encoding == DataEncodingType.DER:
            return 1
        elif self.dispatcher_body_encoding == DataEncodingType.BER:
            return 1
        else:
            return -1

    def get_data(self) -> dict:
        data = {
            'protocolVersion': self.protocol_version,
            'dispatcherMessageLength': self.dispatcher_message_length
        }
        if self.dispatcher_body_encoding is not None:
            data['dispatcherBodyEncoding'] = self.dispatcher_body_encoding
        if self.security_context is not None:
            data['securityContext'] = self.security_context
        return data


class Asn1Type:
    def __init__(self, asn_type: str):
        self.asn_type = asn_type

    def get_data(self) -> dict:
        pass

    def init_from_dict(self, data: dict):
        pass

    def add_optional_field_to_data(self, data: dict, key: str, value) -> None:
        if value is not None:
            data[key] = value

    @staticmethod
    def add_optional_bytes_field_to_data(data: dict, key: str, value: bytes | None):
        if value is not None:
            data[key] = value.decode()


class AbstractMessageBody(Asn1Type):
    def __init__(self, asn_type: str):
        super().__init__(asn_type)
        self.message_id = None
        self.event_creation_time = None
        self.application_id = None
        self.application_data_protocol_version = None
        self.test_flag = None
        self.uid = None
        self.token = None
        self.event_id = None
        self.application_data_encoding = None
        self.application_data_length = None
        self.vin = None
        self.ack_required = None
        self.result = None
        self.error_message = None

    def get_data(self) -> dict:
        data = {
            FIELD_APPLICATION_ID: self.application_id,
            FIELD_EVENT_CREATION_TIME: self.event_creation_time,
            FIELD_MESSAGE_ID: self.message_id,
            FIELD_APPLICATION_DATA_LENGTH: self.application_data_length,
            FIELD_APPLICATION_DATA_PROTOCOL_VERSION: self.application_data_protocol_version
        }
        self.add_optional_field_to_data(data, FIELD_UID, self.uid)
        self.add_optional_field_to_data(data, FIELD_TOKEN, self.token)
        self.add_optional_field_to_data(data, FIELD_VIN, self.vin)
        self.add_optional_field_to_data(data, FIELD_EVENT_ID, self.event_id)
        self.add_optional_field_to_data(data, FIELD_ACK_REQUIRED, self.ack_required)
        if self.application_data_encoding is not None:
            data[FIELD_APPLICATION_DATA_ENCODING] = self.application_data_encoding
        self.add_optional_field_to_data(data, FIELD_TEST_FLAG, self.test_flag)
        self.add_optional_field_to_data(data, FIELD_RESULT, self.result)
        if self.error_message:
            data[FIELD_ERROR_MESSAGE] = self.error_message

        return data

    def init_from_dict(self, data: dict):
        if FIELD_UID in data:
            self.uid = data.get(FIELD_UID)
        if FIELD_TOKEN in data:
            self.token = data.get(FIELD_TOKEN)
        self.application_id = data.get(FIELD_APPLICATION_ID)
        if FIELD_VIN in data:
            self.vin = data.get(FIELD_VIN)
        self.event_creation_time = data.get(FIELD_EVENT_CREATION_TIME)
        if FIELD_EVENT_ID in data:
            self.event_id = data.get(FIELD_EVENT_ID)
        self.message_id = data.get(FIELD_MESSAGE_ID)
        if FIELD_ACK_REQUIRED in data:
            self.ack_required = data.get(FIELD_ACK_REQUIRED)
        self.application_data_length = data.get(FIELD_APPLICATION_DATA_LENGTH)
        if FIELD_APPLICATION_DATA_ENCODING in data:
            self.application_data_encoding = data.get(FIELD_APPLICATION_DATA_ENCODING)
        self.application_data_protocol_version = data.get(FIELD_APPLICATION_DATA_PROTOCOL_VERSION)
        if FIELD_TEST_FLAG in data:
            self.test_flag = data.get(FIELD_TEST_FLAG)
        if FIELD_RESULT in data:
            self.result = data.get(FIELD_RESULT)
        if FIELD_ERROR_MESSAGE in data:
            self.error_message = data.get(FIELD_ERROR_MESSAGE).decode()


class MessageBodyV1(AbstractMessageBody):
    def __init__(self, asn_type: str):
        super().__init__(asn_type)
        self.message_counter = None
        self.icc_id = None
        self.sim_info = None
        self.stateless_dispatcher_message = None
        self.crqm_request = None
        self.basic_position = None
        self.network_info = None
        self.hmi_language = None

    def get_data(self) -> dict:
        data = super().get_data()
        data[FIELD_ICC_ID] = self.icc_id
        self.add_optional_field_to_data(data, FIELD_STATE_LESS_DISPATCHER_MESSAGE, self.stateless_dispatcher_message)
        self.add_optional_field_to_data(data, FIELD_CRQM_REQUEST, self.crqm_request)
        if self.basic_position is not None:
            data[FIELD_BASIC_POSITION] = self.basic_position.get_data()
        if self.network_info is not None:
            data[FIELD_NETWORK_INFO] = self.network_info.get_data()
        self.add_optional_field_to_data(data, FIELD_SIM_INFO, self.sim_info)
        if self.hmi_language is not None:
            data[FIELD_HMI_LANGUAGE] = self.hmi_language.get_data()
        if self.message_counter is not None:
            data[FIELD_MESSAGE_COUNTER] = self.message_counter.get_data()
        return data

    def init_from_dict(self, data: dict):
        super().init_from_dict(data)
        if FIELD_MESSAGE_COUNTER in data:
            self.message_counter = MessageCounter()
            self.message_counter.init_from_dict(data.get(FIELD_MESSAGE_COUNTER))
        self.stateless_dispatcher_message = data.get(FIELD_STATE_LESS_DISPATCHER_MESSAGE)
        self.crqm_request = data.get(FIELD_CRQM_REQUEST)
        if FIELD_BASIC_POSITION in data:
            self.basic_position = BasicPosition()
            self.basic_position.init_from_dict(data.get(FIELD_BASIC_POSITION))
        if FIELD_NETWORK_INFO in data:
            self.network_info = NetworkInfo()
            self.network_info.init_from_dict(data.get(FIELD_NETWORK_INFO))
        self.sim_info = data.get(FIELD_SIM_INFO)
        if FIELD_HMI_LANGUAGE in data:
            self.hmi_language = data.get(FIELD_HMI_LANGUAGE)
        self.icc_id = data.get(FIELD_ICC_ID)


class MessageBodyV2(AbstractMessageBody):
    def __init__(self):
        super().__init__('MPDispatcherBody')
        self.ul_message_counter = None
        self.dl_message_counter = None
        self.ack_message_counter = None

    def get_data(self) -> dict:
        data = super().get_data()
        self.add_optional_field_to_data(data, FIELD_UL_MESSAGE_COUNTER, self.ul_message_counter)
        self.add_optional_field_to_data(data, FIELD_DL_MESSAGE_COUNTER, self.dl_message_counter)
        self.add_optional_field_to_data(data, FIELD_ACK_MESSAGE_COUNTER, self.ack_message_counter)
        return data

    def init_from_dict(self, data: dict):
        super().init_from_dict(data)
        self.ul_message_counter = data.get(FIELD_UL_MESSAGE_COUNTER)
        self.dl_message_counter = data.get(FIELD_DL_MESSAGE_COUNTER)
        self.ack_message_counter = data.get(FIELD_ACK_MESSAGE_COUNTER)


class ApplicationData(Asn1Type):
    def __init__(self, asn_type: str):
        super().__init__(asn_type)


class AbstractMessage:
    def __init__(self, header: Header, body: AbstractMessageBody, application_data: ApplicationData):
        self.header = header
        self.body = body
        self.application_data = application_data

    def get_version(self) -> str:
        pass

    def get_data(self) -> dict:
        app_data = None
        if (
                self.application_data is not None
                and self.application_data.get_data()
        ):
            app_data = self.application_data.get_data()
        return {
            'applicationData': app_data,
            'body': self.body.get_data(),
            'header': self.header.get_data()
        }


class MessageV1(AbstractMessage):
    def __init__(self, header: Header, body: MessageBodyV1, application_data: ApplicationData = None):
        super().__init__(header, body, application_data)


class MessageV2(AbstractMessage):
    def __init__(self, body: MessageBodyV2, application_data: ApplicationData = None,
                 reserved: bytes = None):
        super().__init__(Header(), body, application_data)
        self.reserved = reserved


class AbstractMessageCoder:
    def __init__(self, asn_files_dir: str):
        self.asn_files = []
        self.asn_files_dir = pathlib.Path(__file__).parent / asn_files_dir
        self.load_asn_files()

    def load_asn_files(self):
        for f in os.listdir(self.asn_files_dir):
            if f.endswith('.asn1'):
                self.asn_files.append(str(self.asn_files_dir) + '/' + f)

    def encode_request(self, message: AbstractMessage) -> str:
        pass

    def decode_response(self, message: str, decoded_message: AbstractMessage) -> None:
        pass

    def initialize_message(self, uid: str, token: str, vin: str, application_id: str,
                           application_data_protocol_version: int, message_id: int, message: AbstractMessage) -> None:
        pass

    def get_current_time(self) -> int:
        return int(time.time())

    def get_application_data_bytes(self, application_data: ApplicationData, asn1_tool: Specification) -> bytes:
        if application_data is not None:
            application_data_bytes = asn1_tool.encode(application_data.asn_type, application_data.get_data())
        else:
            application_data_bytes = bytes()
        return application_data_bytes

    @staticmethod
    def validate_dispatcher_message_size(dispatcher_message_size, netto_message_size):
        # The API sometimes provides a wrong dispatcher_message_length value
        # Normally the body size is about 120 bytes
        # A value below 50 is very unlikely.
        if dispatcher_message_size > 50:
            dispatcher_message_bytes_to_read = dispatcher_message_size
        else:
            LOG.debug(f'Calculated message size {int(netto_message_size)} does not match '
                      + f'with header size information {dispatcher_message_size}. Using calculated size.')
            # This will fail if the message contains application data. In this case we cannot tell the body size
            dispatcher_message_bytes_to_read = int(netto_message_size)
        return dispatcher_message_bytes_to_read


class MessageCoderV1(AbstractMessageCoder):
    def __init__(self, asn_files_dir: str):
        super().__init__(asn_files_dir)
        self.asn1_tool_uper = asn1tools.compile_files(self.asn_files, 'uper')
        self.header_length = 4

    def encode_request(self, message: MessageV1) -> str:
        application_data_bytes = self.get_application_data_bytes(message.application_data, self.asn1_tool_uper)

        message_body = message.body
        message_body.application_data_encoding = DataEncodingType.PER_UNALIGNED.value
        message_body.application_data_length = len(application_data_bytes)

        message_body_bytes = self.asn1_tool_uper.encode(message_body.asn_type, message_body.get_data())

        message_header = message.header
        if message_header.protocol_version is None:
            raise ValueError('Protocol version in header missing')
        message_header.security_context = 0
        message_header.dispatcher_message_length = len(message_body_bytes) + self.header_length
        message_header.dispatcher_body_encoding = DataEncodingType.PER_UNALIGNED

        buffered_message_bytes = io.BytesIO()
        buffered_message_bytes.write(message_header.protocol_version.to_bytes(1, "little"))
        buffered_message_bytes.write(message_header.security_context.to_bytes(1, "little"))
        buffered_message_bytes.write(message_header.dispatcher_message_length.to_bytes(1, "little"))
        buffered_message_bytes.write(message_header.get_body_encoding_int_value().to_bytes(1, "little"))

        buffered_message_bytes.write(message_body_bytes)

        buffered_message_bytes.write(application_data_bytes)

        message_bytes = buffered_message_bytes.getvalue()

        length_hex = "{:04x}".format(len(message_bytes) * 2 + 5)
        result = length_hex + "1" + message_bytes.hex()
        return result.upper()

    def decode_response(self, message: str, decoded_message: MessageV1) -> None:
        LOG.debug(f'Message length in bytes: {len(message[5:]) / 2}')
        buffered_message_bytes = io.BytesIO(bytes.fromhex(message[5:]))

        header = decoded_message.header
        header_bytes = buffered_message_bytes.read(self.header_length)
        header.protocol_version = int(header_bytes[0])
        LOG.debug(f'Protocol version: {header.protocol_version}')
        header.security_context = int(header_bytes[1])
        header.dispatcher_message_length = int(header_bytes[2])
        LOG.debug(f'Dispatcher message length: {header.dispatcher_message_length}')
        header.dispatcher_body_encoding = int(header_bytes[3])

        netto_message_size = len(message[5:]) / 2 - self.header_length
        LOG.debug(f'Message size without header: {netto_message_size}')

        dispatcher_message_size = header.dispatcher_message_length - self.header_length
        LOG.debug(f'Dispatcher message bytes: {dispatcher_message_size}')

        dispatcher_message_bytes_to_read = AbstractMessageCoder.validate_dispatcher_message_size(
            dispatcher_message_size, netto_message_size)

        dispatcher_message_bytes = buffered_message_bytes.read(dispatcher_message_bytes_to_read)
        message_body = decoded_message.body
        message_body_dict = self.asn1_tool_uper.decode(message_body.asn_type, dispatcher_message_bytes)
        message_body.init_from_dict(message_body_dict)

        if decoded_message.body.application_data_length > 0:
            application_data_bytes = buffered_message_bytes.read(decoded_message.body.application_data_length)
            application_data_dict = self.asn1_tool_uper.decode(decoded_message.application_data.asn_type,
                                                               application_data_bytes)
            decoded_message.application_data.init_from_dict(application_data_dict)
        else:
            decoded_message.application_data = None

    def initialize_message(self, uid: str, token: str, vin: str, application_id: str,
                           application_data_protocol_version: int, message_id: int, message: MessageV1):
        message_counter = MessageCounter()
        message_counter.downlink_counter = 0
        message_counter.uplink_counter = 1

        body = message.body
        body.message_counter = message_counter
        body.message_id = message_id
        body.icc_id = '12345678901234567890'
        body.sim_info = '1234567890987654321'
        body.event_creation_time = self.get_current_time()
        body.application_id = application_id
        body.application_data_protocol_version = application_data_protocol_version
        body.test_flag = 2
        body.uid = uid
        body.token = token
        body.vin = vin
        body.event_id = 0


class MessageCoderV2(AbstractMessageCoder):
    def __init__(self, asn_files_dir: str):
        super().__init__(asn_files_dir)
        self.asn1_tool_uper = asn1tools.compile_files(self.asn_files, 'uper')
        self.header_length = 3
        self.reserved_size = 16

    def encode_request(self, message: MessageV2) -> str:
        application_data_bytes = self.get_application_data_bytes(message.application_data, self.asn1_tool_uper)

        message_body = message.body
        message_body.application_data_encoding = DataEncodingType.PER_UNALIGNED.value
        message_body.application_data_length = len(application_data_bytes)

        message_body_bytes = self.asn1_tool_uper.encode(message_body.asn_type, message_body.get_data())

        message_header = message.header
        message_header.protocol_version = self.get_protocol_version()
        message_header.dispatcher_message_length = len(message_body_bytes) + self.header_length
        message_header.dispatcher_body_encoding = DataEncodingType.PER_UNALIGNED

        buffered_message_bytes = io.BytesIO()
        buffered_message_bytes.write(message_header.protocol_version.to_bytes(1, 'little'))
        buffered_message_bytes.write(message_header.dispatcher_message_length.to_bytes(1, 'little'))
        buffered_message_bytes.write(message_header.get_body_encoding_int_value().to_bytes(1, 'little'))

        buffered_message_bytes.write(message.reserved)

        buffered_message_bytes.write(message_body_bytes)

        buffered_message_bytes.write(application_data_bytes)

        message_bytes = buffered_message_bytes.getvalue()

        length_hex = "{:04x}".format(len(message_bytes) + self.header_length)
        result = "1" + length_hex + message_bytes.hex()
        return result.upper()

    def decode_response(self, message: str, decoded_message: MessageV2) -> None:
        LOG.debug(f'Message length in bytes: {len(message[5:])/2}')
        buffered_message_bytes = io.BytesIO(bytes.fromhex(message[5:]))

        header = decoded_message.header
        header_bytes = buffered_message_bytes.read(self.header_length)
        header.protocol_version = int(header_bytes[0])
        LOG.debug(f'Protocol version: {header.protocol_version}')
        header.dispatcher_message_length = int(header_bytes[1])
        LOG.debug(f'Dispatcher message length: {header.dispatcher_message_length}')
        header.dispatcher_body_encoding = int(header_bytes[2])

        decoded_message.reserved = buffered_message_bytes.read(self.reserved_size)
        netto_message_size = len(message[5:])/2 - self.header_length - self.reserved_size
        LOG.debug(f'Message size without header and reserved bytes: {netto_message_size}')
        dispatcher_message_size = header.dispatcher_message_length - self.header_length
        LOG.debug(f'Dispatcher message bytes: {dispatcher_message_size}')

        dispatcher_message_bytes_to_read = AbstractMessageCoder.validate_dispatcher_message_size(
            dispatcher_message_size, netto_message_size)

        dispatcher_message_bytes = buffered_message_bytes.read(dispatcher_message_bytes_to_read)
        message_body_dict = self.asn1_tool_uper.decode('MPDispatcherBody', dispatcher_message_bytes)
        message_body = decoded_message.body
        message_body.init_from_dict(message_body_dict)
        if (
            message_body.application_data_length > 0
            and decoded_message.application_data is not None
        ):
            application_data_bytes = buffered_message_bytes.read(message_body.application_data_length)
            application_data_dict = self.asn1_tool_uper.decode(decoded_message.application_data.asn_type,
                                                               application_data_bytes)
            decoded_message.application_data.init_from_dict(application_data_dict)
        else:
            decoded_message.application_data = None

    def initialize_message(self, uid: str, token: str, vin: str, application_id: str,
                           application_data_protocol_version: int, message_id: int, message: MessageV2) -> None:
        message.body.message_id = message_id
        message.body.ul_message_counter = 0
        message.body.dl_message_counter = 0
        message.body.ack_message_counter = 0
        message.body.event_creation_time = self.get_current_time()
        message.body.application_id = application_id
        message.body.application_data_protocol_version = application_data_protocol_version
        message.body.test_flag = 2
        message.body.uid = uid
        message.body.token = token
        message.body.vin = vin
        message.body.event_id = 0
        message.body.result = 0

        message.reserved = bytes(self.reserved_size)

    def get_protocol_version(self) -> int:
        pass


class DataEncodingType(Enum):
    PER_UNALIGNED = 'perUnaligned'
    DER = 'der'
    BER = 'ber'


class MessageCounter(Asn1Type):
    def __init__(self):
        super().__init__('MessageCounter')
        self.downlink_counter = None
        self.uplink_counter = None

    def get_data(self) -> dict:
        return {
            FIELD_UPLINK_COUNTER: self.uplink_counter,
            FIELD_DOWNLINK_COUNTER: self.downlink_counter
        }

    def init_from_dict(self, data: dict):
        self.uplink_counter = data.get(FIELD_UPLINK_COUNTER)
        self.downlink_counter = data.get(FIELD_DOWNLINK_COUNTER)


class BasicPosition(Asn1Type):
    def __init__(self):
        super().__init__('BasicPosition')
        self.latitude = None
        self.longitude = None

    def get_data(self) -> dict:
        return {
            FIELD_LATITUDE: self.latitude,
            FIELD_LONGITUDE: self.longitude
        }

    def init_from_dict(self, data: dict):
        self.latitude = data.get(FIELD_LATITUDE)
        self.longitude = data.get(FIELD_LONGITUDE)


class NetworkInfo(Asn1Type):
    def __init__(self):
        super().__init__('NetworkInfo')
        self.mcc_network = None
        self.mnc_network = None
        self.mcc_sim = None
        self.mnc_sim = None
        self.signal_strength = None

    def get_data(self) -> dict:
        return {
            FIELD_MCC_NETWORK: self.mcc_network,
            FIELD_MNC_NETWORK: self.mnc_network,
            FIELD_MCC_SIM: self.mcc_sim,
            FIELD_MNC_SIM: self.mnc_sim,
            FIELD_SIGNAL_STRENGTH: self.signal_strength
        }

    def init_from_dict(self, data: dict):
        self.mcc_network = data.get(FIELD_MCC_NETWORK)
        self.mnc_network = data.get(FIELD_MNC_NETWORK)
        self.mcc_sim = data.get(FIELD_MCC_SIM)
        self.mnc_sim = data.get(FIELD_MNC_SIM)
        self.signal_strength = data.get(FIELD_SIGNAL_STRENGTH)


class TargetBatteryCode(Enum):
    P_40 = 1
    P_50 = 2
    P_60 = 3
    P_70 = 4
    P_80 = 5
    P_90 = 6
    P_100 = 7

    def get_percentage(self) -> int:
        match self:
            case TargetBatteryCode.P_40:
                return 40
            case TargetBatteryCode.P_50:
                return 50
            case TargetBatteryCode.P_60:
                return 60
            case TargetBatteryCode.P_70:
                return 70
            case TargetBatteryCode.P_80:
                return 80
            case TargetBatteryCode.P_90:
                return 90
            case TargetBatteryCode.P_100:
                return 100
            case _:
                raise ValueError(f'Unknown target battery code: {self}')

    @staticmethod
    def from_percentage(percentage: int):
        match percentage:
            case 40:
                return TargetBatteryCode.P_40
            case 50:
                return TargetBatteryCode.P_50
            case 60:
                return TargetBatteryCode.P_60
            case 70:
                return TargetBatteryCode.P_70
            case 80:
                return TargetBatteryCode.P_80
            case 90:
                return TargetBatteryCode.P_90
            case 100:
                return TargetBatteryCode.P_100
            case _:  # default
                raise ValueError(f'Unknown target battery percentage: {percentage}')
