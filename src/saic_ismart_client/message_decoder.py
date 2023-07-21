import argparse
import json

from common_model import MessageV2, MessageBodyV2, Header
from ota_v1_1.Message import MessageCoderV11
from ota_v1_1.data_model import MessageV11, MessageBodyV11
from ota_v2_1.Message import MessageCoderV21
from ota_v2_1.data_model import OtaRvmVehicleStatusReq, OtaRvmVehicleStatusResp25857
from ota_v3_0.Message import MessageV30, MessageBodyV30, MessageCoderV30
from ota_v3_0.data_model import OtaChrgMangDataResp


def process_arguments():
    parser = argparse.ArgumentParser(description='Decode your SAIC ASN.1 messages')
    parser.add_argument('-m', '--message', help='ASN.1 message to decode', dest='message', required=True)
    parser.add_argument('-t', '--type', help='Message type', choices=['request', 'response'], dest='message_type',
                        required=True)
    parser.add_argument('-v', '--message-version', help='Message version', choices=['V1', 'V2', 'V3'],
                        dest='message_version', required=True)
    return parser.parse_args()


def handle_message_v1(message_coder: MessageCoderV11, message: str, message_type: str,
                      decoded_message: MessageV11) -> None:
    application_id = decoded_message.body.application_id
    application_data_protocol_version = decoded_message.body.application_data_protocol_version


def handle_message_v2(message_coder: MessageCoderV21, message: str, message_type: str,
                      decoded_message: MessageV2) -> None:
    application_id = decoded_message.body.application_id
    application_data_protocol_version = decoded_message.body.application_data_protocol_version

    if (
            application_id == '511'
            and application_data_protocol_version == 25857
    ):
        if message_type == 'request':
            decoded_message.application_data = OtaRvmVehicleStatusReq()
            message_coder.decode_response(message, decoded_message)
        else:
            decoded_message.application_data = OtaRvmVehicleStatusResp25857()
            message_coder.decode_response(message, decoded_message)


def handle_message_v3(message_coder: MessageCoderV30, message: str, message_type: str,
                      decoded_message: MessageV30) -> None:
    application_id = decoded_message.body.application_id
    application_data_protocol_version = decoded_message.body.application_data_protocol_version

    if (
            application_id == '516'
            and application_data_protocol_version == 768
    ):
        if message_type == 'request':
            message_coder.decode_response(message, decoded_message)
        else:
            decoded_message.application_data = OtaChrgMangDataResp()
            message_coder.decode_response(message, decoded_message)


def main():
    args = process_arguments()
    message = args.message
    message_type = args.message_type
    message_version = args.message_version.upper()
    decoded_message = None

    if message_version == 'V1':
        message_v1_1_coder = MessageCoderV11()
        decoded_message = MessageV11(Header(), MessageBodyV11())
        message_v1_1_coder.decode_response(message, decoded_message)
        handle_message_v1(message_v1_1_coder, message, message_type, decoded_message)
    elif message_version == 'V2':
        message_v2_1_coder = MessageCoderV21()
        decoded_message = MessageV2(MessageBodyV2())
        message_v2_1_coder.decode_response(message, decoded_message)
        handle_message_v2(message_v2_1_coder, message, message_type, decoded_message)
    elif message_version == 'V3':
        message_v3_0_coder = MessageCoderV30()
        decoded_message = MessageV30(MessageBodyV30())
        message_v3_0_coder.decode_response(message, decoded_message)
        handle_message_v3(message_v3_0_coder, message, message_type, decoded_message)

    if decoded_message:
        json_object = json.dumps(decoded_message.get_data(), indent=4)
        print(json_object)
    else:
        print('No decoded message')


if __name__ == '__main__':
    main()
