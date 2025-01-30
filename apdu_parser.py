from command_detail import (
    command_details,
    device_identities,
    result_details,
    duration_tag,
    address_tag,
    parse_channel_status,
    data_destination_address_tag,
    bearer_description_tag,
    event_list_info,
    location_info,
    parse_imei,
    access_technology,
    timer_identifier,
)

def ber_tlv_check(input_data):
    """
    用于检测输入数据是否是 BER-TLV。
    """
    tag_map = {
        'CF': 'Reserved for proprietary use (direction terminal to UICC)',
        'D0': 'Proactive Command',
        'D1': 'GSM/3GPP/3GPP2 - SMS-PP Download',
        'D2': 'GSM/3GPP/3GPP2 - Cell Broadcast Download',
        'D3': 'Menu Selection',
        'D4': 'Call Control',
        'D5': 'GSM/3GPP/3GPP2 - MO Short Message control',
        'D6': 'Event Download',
        'D7': 'Timer Expiration',
        'D8': 'Reserved for intra-UICC communication and not visible on the card interface',
        'D9': '3GPP/3GPP2 - USSD Download',
        'DA': 'MMS Transfer status',
        'DB': 'MMS notification download',
        'DC': 'Terminal application tag',
        'DD': '3GPP - Geographical Location Reporting tag',
        'DE': 'Envelope Container',
        'DF': '3GPP - ProSe Report tag',
        'E0': '3GPP – 5G ProSe Report tag',
        'E1': 'Reserved for 3GPP (for future usage)',
        'E2': 'Reserved for 3GPP (for future usage)',
        'E3': 'Reserved for 3GPP (for future usage)',
        'E4': 'Reserved for GSMA (direction terminal to UICC)',
    }
    return tag_map.get(input_data, "COMPREHENSION_TLV")


def cmd_parse_in_memory(input_data, length):
    """
    解析一个 Proactive/Terminal Response/Envelope APDU (Comprehension TLV等)。
    返回 (first_cmd_name, full_parsed_str):
      - first_cmd_name: 第一次解析到的 CommandDetail，用于在左侧列表显示
      - full_parsed_str: 完整解析文本
    """
    output_lines = []
    index = 0
    first_cmd_name = None

    while index < length * 2:
        tag = input_data[index:index+2]
        index += 2
        if index + 2 > len(input_data):
            output_lines.append(f"Parsing error: not enough length for tag {tag}")
            break
        length_byte = int(input_data[index:index+2], 16)
        index += 2
        value_start = index
        value_end = index + (length_byte * 2)
        if value_end > len(input_data):
            output_lines.append(f"Parsing error: not enough length for tag {tag} value")
            break

        value = input_data[value_start:value_end]
        index = value_end

        # 根据tag解析
        if tag in ["01", "81"]:
            command = command_details(value)
            if first_cmd_name is None:
                first_cmd_name = command
            output_lines.append(f"\t{command}")
        elif tag in ["02", "82"]:
            identities = device_identities(value)
            output_lines.append(f"\t{identities}")
        elif tag in ["03", "83"]:
            result = result_details(value)
            output_lines.append(f"\t{result}")
        elif tag in ["04", "84"]:
            duration = duration_tag(value)
            output_lines.append(f"\tDuration: {duration}")
        elif tag in ["05", "85"]:
            output_lines.append(f"\tAlpha identifier tag: {value}")
        elif tag in ["06", "86"]:
            address = address_tag(value)
            output_lines.append(f"\tAddress tag: {address}")
        elif tag in ["38", "B8"]:
            channel_info = parse_channel_status(value)
            output_lines.append(f"\tChannel status: {channel_info}")
        elif tag in ["0B", "8B"]:
            output_lines.append(f"\tSMS TPDU: {value}")
        elif tag in ["39", "B9"]:
            Buffer_size = int(value, 16)
            output_lines.append(f"\tBuffer size: {Buffer_size}")
        elif tag in ["47", "C7"]:
            if length_byte < 30:
                try:
                    network_access_name = bytes.fromhex(value[2:length_byte * 2]).decode('ascii', errors='replace')
                    output_lines.append(f"\tNetwork Access Name: {network_access_name}")
                except Exception:
                    output_lines.append(f"\tNetwork Access Name(hex): {value}")
            else:
                output_lines.append(f"\tNetwork Access Name(hex): {value}")
        elif tag in ["FC", "7C"]:
            output_lines.append(f"\tEPS PDN connection activation parameters: {value}")
        elif tag in ["3C", "BC"]:
            type_value = value[0:2]
            port_value = value[2:]
            protocol_map = {
                "01": "UDP, UICC in client mode, remote connection",
                "02": "TCP, UICC in client mode, remote connection",
                "03": "TCP, UICC in server mode",
                "04": "UDP, UICC in client mode, local connection",
                "05": "TCP, UICC in client mode, local connection",
                "06": "direct communication channel",
            }
            protocol_type = protocol_map.get(type_value, f"Unknown protocol type: {type_value}")
            port = int(port_value, 16) if port_value else 0
            output_lines.append(f"\tTransport protocol type: {protocol_type}, port: {port}")
        elif tag in ["FD", "7D"]:
            # MCCMNC + TAC
            if len(value) >= 6:
                mccmnc_raw = value[0:6]
                mccmnc = f"{mccmnc_raw[1]}{mccmnc_raw[0]}{mccmnc_raw[3]}{mccmnc_raw[5]}{mccmnc_raw[4]}{mccmnc_raw[2]}"
                tac = value[6:]
                output_lines.append(f"\tMCCMNC: {mccmnc},TAC: {tac}")
            else:
                output_lines.append(f"\tInvalid FD/7D: {value}")
        elif tag in ["B5", "35"]:
            bearer = bearer_description_tag(value)
            output_lines.append(f"\tBearer description tag: {bearer}")
        elif tag in ["13", "93"]:
            location = location_info(value)
            output_lines.append(f"\t{location}")
        elif tag in ["14", "94"]:
            imei = parse_imei(value)
            output_lines.append(f"\tIMEI: {imei}")
        elif tag in ["62", "E2"]:
            output_lines.append(f"\tIMEISV: {value}")
        elif tag in ["6F", "EF"]:
            output_lines.append(f"\tMMS Notification: {value}")
        elif tag in ["33", "B3"]:
            output_lines.append(f"\tProvisioning Reference File: {value}")
        elif tag in ["19", "99"]:
            event = event_list_info(value)
            output_lines.append(f"\tEvent list tag: {event}")
        elif tag in ["1B", "9B"]:
            if value == "00":
                ls = "Normal service"
            elif value == "01":
                ls = "Limited service"
            elif value == "02":
                ls = "No service"
            else:
                ls = "unknown status"
            output_lines.append(f"\tLocation status tag: {ls}")
        elif tag in ["2F", "AF"]:
            output_lines.append(f"\tAID: {value}")
        elif tag in ["3E", "BE"]:
            data_dest = data_destination_address_tag(value)
            output_lines.append(f"\tdata destination address: {data_dest}")
        elif tag in ["36", "B6"]:
            output_lines.append(f"\tChannel data: {value}")
        elif tag in ["37", "B7"]:
            output_lines.append(f"\tChannel data length: {value}")
        elif tag in ["3F", "BF"]:
            techs = access_technology(value)
            output_lines.append(f"\tAccess Technology: {techs}")
        elif tag in ["F4", "74"]:
            output_lines.append(f"\tAttach Type: {value}")
        elif tag in ["F5", "75"]:
            output_lines.append(f"\tRejection Cause: {value}")
        elif tag in ["A2", "22"]:
            output_lines.append(f"\tC-APDU: {value}")
        elif tag in ["A4", "24"]:
            t_desc = timer_identifier(value)
            output_lines.append(f"\tTimer identifier: {t_desc}")
        elif tag in ["A5", "25"]:
            if len(value) >= 6:
                time_value = ":".join([value[0:2], value[2:4], value[4:6]])
                output_lines.append(f"\tTimer: {time_value}")
            else:
                output_lines.append(f"\tTimer: {value}")
        elif tag in ["21", "A1"]:
            output_lines.append(f"\tCard ATR: {value}")
        elif tag in ["E0", "60"]:
            output_lines.append(f"\tMAC: {value}")
        elif tag in ["A6", "26"]:
            output_lines.append(f"\tDate-Time and Time zone: {value}")
        elif tag in ["6C", "EC"]:
            output_lines.append(f"\tMMS Transfer Status: {value}")
        elif tag in ["7E", "FE"]:
            output_lines.append(f"\tCSG ID list: {value}")
        elif tag in ["56", "D6"]:
            output_lines.append(f"\tCSG ID: {value}")
        elif tag in ["57", "D7"]:
            output_lines.append(f"\tTimer Expiration: {value}")
        else:
            print(f"Unknown tag: {tag} length: {length_byte} value: {value}")
            output_lines.append(f"Unknown tag: {tag} length: {length_byte} value: {value}")

    return first_cmd_name, "\n".join(output_lines)


def parse_apdu_lines_in_memory(lines):
    """
    解析一批 APDU 字符串，每条解析为:
      {
          "title": 用于列表展示的简要信息(方向+命令),
          "details": 解析出来的详细文本,
          "raw": 原始数据
      }
    """
    items = []
    for line in lines:
        input_data = line.strip()
        if not input_data:
            continue

        # 预设
        direction_str = ""
        cmd_type_str = ""
        full_parse_output = ""
        command_name_for_list = "unknown"

        if input_data.startswith("D0"):
            direction_str = "UICC=>TERMINAL: proactive command"
            # 解析长度
            if len(input_data) >= 6 and input_data[4:6] == "81":
                length = int(input_data[2:4], 16)
                first_cmd_name, parse_text = cmd_parse_in_memory(input_data[4:4 + length * 2], length)
                full_parse_output = f"{direction_str}\n{parse_text}"
                if first_cmd_name:
                    command_name_for_list = first_cmd_name
            else:
                if len(input_data) >= 6:
                    length = int(input_data[4:6], 16)
                    abnormal_str = f"\tdata abnormal: {input_data}\n"
                    first_cmd_name, parse_text = cmd_parse_in_memory(input_data[6:6 + length * 2], length)
                    full_parse_output = f"{direction_str}\n{abnormal_str}{parse_text}"
                    if first_cmd_name:
                        command_name_for_list = first_cmd_name
                else:
                    full_parse_output = f"{direction_str}\n数据长度不足: {input_data}"

            items.append({
                "title": f"{direction_str}: {command_name_for_list}",
                "details": full_parse_output,
                "raw": input_data
            })

        elif input_data.startswith("80"):
            direction_str = "TERMINAL=>UICC"
            # 通常结构: 80xx..., 先取 8:10 这两位做 length
            if len(input_data) < 10:
                items.append({
                    "title": f"{direction_str}: unknown (len error)",
                    "details": f"{direction_str}\n数据过短，无法解析: {input_data}",
                    "raw": input_data
                })
                continue

            length = int(input_data[8:10], 16)
            body_data = input_data[10:10 + length * 2]
            tlv_type = ber_tlv_check(body_data[:2])

            if tlv_type != "COMPREHENSION_TLV":
                # 说明是 BER-TLV
                if len(input_data) >= 14:
                    length2 = int(input_data[12:14], 16)
                    body_data = input_data[14:14 + length2 * 2]
                    length = length2

            # 判断具体指令
            if input_data.startswith("8014"):
                cmd_type_str = "Terminal Response"
                first_cmd_name, parse_text = cmd_parse_in_memory(body_data, length)
            elif input_data.startswith("80C2"):
                cmd_type_str = "Envelope"
                first_cmd_name, parse_text = cmd_parse_in_memory(body_data, length)
            elif input_data.startswith("8010"):
                cmd_type_str = "terminal profile"
                parse_text = "<No Comprehension TLV parse for terminal profile>"
                first_cmd_name = ""
            elif input_data.startswith("80AA"):
                cmd_type_str = "TERMINAL CAPABILITY"
                parse_text = "<No Comprehension TLV parse for TERMINAL CAPABILITY>"
                first_cmd_name = ""
            elif input_data.startswith("8012"):
                cmd_type_str = "Fetch command"
                parse_text = "<No Comprehension TLV parse for Fetch command>"
                first_cmd_name = ""
            elif input_data.startswith("80F2"):
                cmd_type_str = "Status"
                parse_text = "<No Comprehension TLV parse for Status>"
                first_cmd_name = ""
            else:
                # unknown
                cmd_type_str = f"unknown command: {input_data[0:4]}"
                parse_text = ""

            full_parse_output = f"{direction_str} - {cmd_type_str}\n"
            if parse_text:
                full_parse_output += parse_text

            if first_cmd_name:
                command_name_for_list = first_cmd_name

            items.append({
                "title": f"{direction_str}: {cmd_type_str}" + (f" - {first_cmd_name}" if first_cmd_name else ""),
                "details": full_parse_output,
                "raw": input_data
            })

        else:
            # unknown
            items.append({
                "title": "unknown command",
                "details": f"unknown command\n{input_data}",
                "raw": input_data
            })

    return items
