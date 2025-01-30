def command_details(input_data):
    command_map = {
        "01": "REFRESH",
        "02": "MORE TIME",
        "03": "POLL INTERVAL",
        "04": "POLLING OFF",
        "05": "SET UP EVENT LIST",
        "10": "SET UP CALL",
        "11": "Reserved for GSM/3G (SEND SS)",
        "12": "Reserved for GSM/3G (SEND USSD)",
        "13": "SEND SHORT MESSAGE",
        "14": "SEND DTMF",
        "15": "LAUNCH BROWSER",
        "16": "Reserved for 3GPP (GEOGRAPHICAL LOCATION REQUEST)",
        "20": "PLAY TONE",
        "21": "DISPLAY TEXT",
        "22": "GET INKEY",
        "23": "GET INPUT",
        "24": "SELECT ITEM",
        "25": "SET UP MENU",
        "26": "PROVIDE LOCAL INFORMATION",
        "27": "TIMER MANAGEMENT",
        "28": "SET UP IDLE MODE TEXT",
        "30": "PERFORM CARD APDU",
        "31": "POWER ON CARD",
        "32": "POWER OFF CARD",
        "33": "GET READER STATUS",
        "34": "RUN AT COMMAND",
        "35": "LANGUAGE NOTIFICATION",
        "40": "OPEN CHANNEL",
        "41": "CLOSE CHANNEL",
        "42": "RECEIVE DATA",
        "43": "SEND DATA",
        "44": "GET CHANNEL STATUS",
        "45": "SERVICE SEARCH",
        "46": "GET SERVICE INFORMATION",
        "47": "DECLARE SERVICE",
        "50": "SET FRAMES",
        "51": "GET FRAMES STATUS",
        "60": "(RETRIEVE MULTIMEDIA MESSAGE)",
        "61": "(SUBMIT MULTIMEDIA MESSAGE)",
        "62": "DISPLAY MULTIMEDIA MESSAGE",
        "70": "ACTIVATE",
        "71": "CONTACTLESS STATE CHANGED",
        "73": "ENCAPSULATED SESSION CONTROL",
        "74": "Void",
        "75": "Reserved for 3GPP (for future usage)",
        "76": "Reserved for 3GPP (for future usage)",
        "77": "Reserved for 3GPP (for future usage)",
        "78": "Reserved for 3GPP (for future usage)",
        "79": "LSI COMMAND",
        "81": "End of the proactive UICC session",
    }

    if len(input_data) < 4:
        return "Unknown Command"

    command_value = input_data[2:4]
    command_name = command_map.get(command_value, "Unknown Command")

    # 解析 Command Qualifier
    if len(input_data) != 0:
        qualifier = input_data[4:6]
        qualifier_description = get_qualifier_description(command_value, qualifier)
        return f"{command_name} - {qualifier_description}"

    return command_name


def get_qualifier_description(command_value, qualifier):
    qualifier_map = {
        "01": {
            "00": "NAA Initialization and Full File Change Notification",
            "01": "File Change Notification",
            "02": "NAA Initialization and File Change Notification",
            "03": "NAA Initialization",
            "04": "UICC Reset",
            "05": "NAA Application Reset",
            "06": "NAA Session Reset",
            "07": "Reserved by 3GPP",
            "08": "Reserved by 3GPP",
            "09": "eUICC Profile State Change",
            "0A": "Application Update",
            # "0B" to "FF" reserved
        },
        "10": {
            "00": "Set up call, not busy",
            "01": "Set up call, not busy, with redial",
            "02": "Set up call, put others on hold",
            "03": "Set up call, put others on hold, with redial",
            "04": "Set up call, disconnect others",
            "05": "Set up call, disconnect others, with redial",
        },
        "13": {
            "00": "Packing not required",
            "01": "SMS packing required",
        },
        "20": {
            "00": "Use of vibrate alert is up to the terminal",
            "01": "Vibrate alert with the tone",
        },
        "21": {
            "00": "Normal priority",
            "01": "High priority",
            "80": "Clear message after a delay",
            "81": "Wait for user to clear message",
        },
        "22": {
            "00": "Digits only",
            "01": "Alphabet set",
            "02": "SMS default alphabet",
            "03": "UCS2 alphabet",
            "04": "Character sets enabled",
            "05": "Character sets disabled, Yes/No response",
            "08": "No help information",
            "09": "Help information available",
        },
        "23": {
            "00": "Digits only",
            "01": "Alphabet set",
            "02": "SMS default alphabet",
            "03": "UCS2 alphabet",
            "04": "Echo user input",
            "05": "User input not revealed",
            "08": "No help information",
            "09": "Help information available",
        },
        "24": {
            "00": "Presentation type not specified",
            "01": "Presentation type specified",
            "02": "Choice of data values",
            "03": "Choice of navigation options",
            "08": "No help information",
            "09": "Help information available",
        },
        "25": {
            "00": "No selection preference",
            "01": "Selection using soft key preferred",
            "08": "No help information",
            "09": "Help information available",
        },
        "26": {
            "00": "Location Information",
            "01": "IMEI of the terminal",
            "02": "Network Measurement results",
            "03": "Date, time and time zone",
            "04": "Language setting",
            "05": "Reserved for GSM",
            "06": "Access Technology",
            "07": "ESN of the terminal",
            "08": "IMEISV of the terminal",
            "09": "Search Mode",
            "0A": "Charge State of the Battery",
            "0B": "MEID of the terminal",
            "0C": "Reserved for 3GPP",
            "0D": "Broadcast Network information",
            "0E": "Multiple Access Technologies",
            "0F": "Location Information for multiple access",
            "10": "Network Measurement results for multiple access",
            "1A": "Supported Radio Access Technologies",
        },
        "33": {
            "00": "Card reader status",
            "01": "Card reader identifier",
        },
        "27": {
            "00": "Start",
            "01": "Deactivate",
            "10": "Get current value",
        },
        "40": {
            "00": "On demand link establishment",
            "01": "Immediate link establishment",
            "02": "No automatic reconnection",
            "03": "Automatic reconnection",
            "04": "No background mode",
            "05": "Immediate link establishment in background mode",
            "06": "No DNS server address requested",
            "07": "DNS server address requested",
        },
        "41": {
            "00": "No indication",
            "01": "Indication for next CAT command",
        },
        "43": {
            "00": "Store data in Tx buffer",
            "01": "Send data immediately",
        },
        "62": {
            "00": "Normal priority",
            "01": "High priority",
            "80": "Clear message after a delay",
            "81": "Wait for user to clear message",
        },
        "73": {
            "00": "End encapsulated command session",
            "01": "Request Master SA setup",
            "02": "Request Connection SA setup",
            "03": "Request Secure Channel Start",
            "04": "Close Master and Connection SA",
        },
        "79": {
            "00": "Proactive Session Request",
            "01": "UICC Platform Reset",
        },
    }
    return qualifier_map.get(command_value, {}).get(qualifier, "Qualifier not defined: " + qualifier)


def device_identities(input_data):
    device_map = {
        "01": "Keypad",
        "02": "Display",
        "03": "Earpiece",
        "10": "Additional Card Reader 0",
        "11": "Additional Card Reader 1",
        "12": "Additional Card Reader 2",
        "13": "Additional Card Reader 3",
        "14": "Additional Card Reader 4",
        "15": "Additional Card Reader 5",
        "16": "Additional Card Reader 6",
        "17": "Additional Card Reader 7",
        "21": "Channel 1",
        "22": "Channel 2",
        "23": "Channel 3",
        "24": "Channel 4",
        "25": "Channel 5",
        "26": "Channel 6",
        "27": "Channel 7",
        "31": "eCAT client 1",
        "32": "eCAT client 2",
        "33": "eCAT client 3",
        "34": "eCAT client 4",
        "35": "eCAT client 5",
        "36": "eCAT client 6",
        "37": "eCAT client 7",
        "38": "eCAT client 8",
        "39": "eCAT client 9",
        "3A": "eCAT client A",
        "3B": "eCAT client B",
        "3C": "eCAT client C",
        "3D": "eCAT client D",
        "3E": "eCAT client E",
        "3F": "eCAT client F",
        "81": "UICC",
        "82": "Terminal",
        "83": "Network",
    }

    if len(input_data) < 4:
        return "Unknown device identities"

    source_device = input_data[0:2]
    destination_device = input_data[2:4]

    source_description = device_map.get(source_device, "Unknown Source Device")
    destination_description = device_map.get(destination_device, "Unknown Destination Device")

    return f"{source_description} -> {destination_description}"


def result_details(input_data):
    general_result_map = {
        "00": "Command performed successfully",
        "01": "Command performed with partial comprehension",
        "02": "Command performed, with missing information",
        "03": "REFRESH performed with additional EFs read",
        "04": "Command performed successfully, but requested icon could not be displayed",
        "05": "Command performed, but modified by call control by NAA",
        "06": "Command performed successfully, limited service",
        "07": "Command performed with modification",
        "08": "REFRESH performed but indicated NAA was not active",
        "09": "Command performed successfully, tone not played",
        "10": "Proactive UICC session terminated by the user",
        "11": "Backward move in the proactive UICC session requested by the user",
        "12": "No response from user",
        "13": "Help information required by the user",
        "14": "Reserved for GSM/3G",
        "15": "Reserved for 3GPP (for future usage)",
        "16": "Reserved for 3GPP (for future usage)",
        "20": "Terminal currently unable to process command",
        "21": "Network currently unable to process command",
        "22": "User did not accept the proactive command",
        "23": "User cleared down call before connection or network release",
        "24": "Action in contradiction with the current timer state",
        "25": "Interaction with call control by NAA, temporary problem",
        "26": "Launch browser generic error",
        "27": "MMS temporary problem",
        "28": "Reserved for 3GPP (for future usage)",
        "29": "Reserved for 3GPP (for future usage)",
        "30": "Command beyond terminal's capabilities",
        "31": "Command type not understood by terminal",
        "32": "Command data not understood by terminal",
        "33": "Command number not known by terminal",
        "36": "Error, required values are missing",
        "38": "MultipleCard commands error",
        "39": "Interaction with call control by NAA, permanent problem",
        "3A": "Bearer Independent Protocol error",
        "3B": "Access Technology unable to process command",
        "3C": "Frames error",
        "3D": "MMS Error",
    }

    additional_info_map = {
        "20": {
            "00": "No specific cause can be given",
            "01": "Screen is busy",
            "02": "Terminal currently busy on call",
            "04": "No service",
            "05": "Access control class bar",
            "06": "Radio resource not granted",
            "07": "Not in speech call",
            "09": "Terminal currently busy on SEND DTMF command",
            "0A": "No NAA active",
        },
        "21": {
            "00": "No specific cause can be given",
        },
        "38": {
            "00": "No specific cause can be given",
            "01": "Card reader removed or not present",
            "02": "Card removed or not present",
            "03": "Card reader busy",
            "04": "Card powered off",
            "05": "C-APDU format error",
            "06": "Mute card",
            "07": "Transmission error",
            "08": "Protocol not supported",
            "09": "Specified reader not valid",
        },
        "39": {
            "00": "No specific cause can be given",
            "01": "Action not allowed",
            "02": "The type of request has changed",
        },
        "26": {
            "00": "No specific cause can be given",
            "01": "Bearer unavailable",
            "02": "Browser unavailable",
            "03": "Terminal unable to read the provisioning data",
            "04": "Default URL unavailable",
        },
        "3A": {
            "00": "No specific cause can be given",
            "01": "No channel available",
            "02": "Channel closed",
            "03": "Channel identifier not valid",
            "04": "Requested buffer size not available",
            "05": "Security error (unsuccessful authentication)",
            "06": "Requested UICC/terminal interface transport level not available",
            "07": "Remote device is not reachable",
            "08": "Service error (service not available on remote device)",
            "09": "Service identifier unknown",
            "10": "Port not available",
            "11": "Launch parameters missing or incorrect",
            "12": "Application launch failed",
        },
        "3C": {
            "00": "No specific cause can be given",
            "01": "Frame identifier is not valid",
            "02": "Number of frames beyond the terminal's capabilities",
            "03": "No Frame defined",
            "04": "Requested size not supported",
            "05": "Default Active Frame is not valid",
        },
        "3D": {
            "00": "No specific cause can be given",
        },
    }

    if len(input_data) < 2:
        return "Unknown General Result"

    general_result = input_data[:2]
    result_description = general_result_map.get(general_result, "Unknown General Result")

    additional_info = ""
    if len(input_data) > 2:
        additional_info_code = input_data[2:4]
        additional_info_description = additional_info_map.get(general_result, {}).get(
            additional_info_code, "Unknown Additional Info"
        )
        additional_info = f", Additional Info: {additional_info_description}"

    return f"Result: {result_description}{additional_info}"


def location_info(input_data):
    # Decode MCCMNC
    if len(input_data) < 6:
        return "Location info length error"

    mccmnc_bytes = input_data[:6]
    mccmnc = f"{mccmnc_bytes[1]}{mccmnc_bytes[0]}{mccmnc_bytes[3]}{mccmnc_bytes[5]}{mccmnc_bytes[4]}{mccmnc_bytes[2]}"

    # 判断长度确定 4G / 5G
    if len(input_data) == 22:  # 11 bytes => 5G
        tac = input_data[6:12]
        cell_id = input_data[12:]
    elif len(input_data) == 18:  # 9 bytes => 4G
        tac = input_data[6:10]
        cell_id = input_data[10:]
    else:
        return f"Invalid location info length: {len(input_data)//2} bytes"

    return f"MCCMNC: {mccmnc}, TAC: {tac}, CELL ID: {cell_id}"


def event_list_info(value):
    event_map = {
        '00': 'MT call',
        '01': 'Call connected',
        '02': 'Call disconnected',
        '03': 'Location status',
        '04': 'User activity',
        '05': 'Idle screen available',
        '06': 'Card reader status',
        '07': 'Language selection',
        '08': 'Browser termination',
        '09': 'Data available',
        '0A': 'Channel status',
        '0B': 'Access Technology Change (single access technology)',
        '0C': 'Display parameters changed',
        '0D': 'Local connection',
        '0E': 'Network Search Mode Change',
        '0F': 'Browsing status',
        '10': 'Frames Information Change',
        '11': '(I-)WLAN Access Status',
        '12': 'Network Rejection',
        '13': 'HCI connectivity event',
        '14': 'Access Technology Change (multiple access technologies)',
        '15': 'CSG cell selection',
        '16': 'Contactless state request',
        '17': 'IMS Registration',
        '18': 'Incoming IMS data',
        '19': 'Profile Container',
        '1B': 'Secured Profile Container',
        '1C': 'Poll Interval Negotiation',
        '1D': 'Data Connection Status Change',
        '1E': 'CAG cell selection',
    }

    events = []
    for i in range(0, len(value), 2):
        event_code = value[i:i+2]
        event_name = event_map.get(event_code, f"Unknown Event ({event_code})")
        events.append(event_name)
    return ', '.join(events)


def bearer_description_tag(value):
    bearer_type_map = {
        '01': 'CSD',
        '02': 'GPRS / UTRAN packet service / E-UTRAN / Satellite E-UTRAN / NG-RAN / Satellite NG-RAN',
        '03': 'Default bearer for requested transport layer',
        '04': 'Local link technology independent',
        '05': 'Bluetooth®',
        '06': 'IrDA',
        '07': 'RS232',
        '08': 'cdma2000 packet data service',
        '09': 'UTRAN packet service with extended parameters / HSDPA / E-UTRAN / Satellite E-UTRAN / NG-RAN / Satellite NG-RAN',
        '0A': '(I-)WLAN',
        '0B': 'E-UTRAN / Satellite E-UTRAN / NG-RAN / Satellite NG-RAN / mapped UTRAN packet service',
        '0C': 'NG-RAN / Satellite NG-RAN',
    }

    if len(value) < 2:
        return "Invalid bearer description"

    bearer_type = value[:2]
    bearer_parameters = value[2:]
    bearer_type_description = bearer_type_map.get(bearer_type, 'Unknown Bearer Type')

    return f"Bearer type: {bearer_type_description}, Bearer parameters: {bearer_parameters}"


def address_tag(value):
    if len(value) < 2:
        return "Invalid address tag"

    ton_npi_byte = bin(int(value[:2], 16))[2:].zfill(8)
    ton_bits = ton_npi_byte[1:4]  # b7-b5
    npi_bits = ton_npi_byte[4:]   # b4-b1

    ton_dict = {
        '000': 'Unknown',
        '001': 'International Number',
        '010': 'National Number',
        '011': 'Network Specific Number',
    }
    npi_dict = {
        '0000': 'Unknown',
        '0001': 'ISDN/telephony numbering plan (E.164/E.163)',
        '0011': 'Data numbering plan (X.121)',
        '0100': 'Telex numbering plan (F.69)',
        '1001': 'Private numbering plan',
        '1111': 'Reserved for extension',
    }

    ton_value = ton_dict.get(ton_bits, 'Reserved/Access Technology Specific')
    npi_value = npi_dict.get(npi_bits, 'Reserved/Access Technology Specific')

    dialling_number_raw = value[2:]
    dialling_number = ''
    for i in range(0, len(dialling_number_raw), 2):
        byte = dialling_number_raw[i:i+2]
        if len(byte) == 2:
            dialling_number += byte[1] + byte[0]

    return f"TON: {ton_value}, NPI: {npi_value}, Dialling Number: {dialling_number}"


def data_destination_address_tag(value):
    if len(value) < 2:
        return "Unknown IP type"

    ip_type_byte = value[0:2]
    ip_address = []

    if ip_type_byte == "21":  # IPv4
        for i in range(2, len(value), 2):
            byte = int(value[i:i+2], 16)
            ip_address.append(str(byte))
        return f"IPV4: {'.'.join(ip_address)}"
    elif ip_type_byte == "57":  # IPv6
        for i in range(2, len(value), 4):
            byte_pair = value[i:i+4]
            ip_address.append(byte_pair)
        return f"IPV6: {':'.join(ip_address)}"
    else:
        return "Unknown IP type"


def parse_channel_status(value):
    if len(value) < 4:
        return "Invalid channel status"

    channel_status_byte3 = int(value[0:2], 16)
    channel_id = channel_status_byte3 & 0b00000111
    bip_established_flag = (channel_status_byte3 >> 7) & 0b00000001
    bip_channel_established = "BIP channel established" if bip_established_flag == 1 else "BIP channel not established"

    further_info = ""
    if len(value) >= 4:
        channel_status_byte4 = value[2:6]
        if channel_status_byte4 == '00':
            further_info = "No further info can be given"
        elif channel_status_byte4 == '05':
            further_info = "Link dropped (network failure or user cancellation)"

    return f"Channel ID: {channel_id}, {bip_channel_established}, {further_info}"


def access_technology(value):
    technology_map = {
        '00': 'GSM',
        '01': 'TIA/EIA-553',
        '02': 'TIA/EIA-136-270',
        '03': 'UTRAN',
        '04': 'TETRA',
        '05': 'TIA/EIA-95-B',
        '06': 'cdma2000 1x (TIA-2000.2)',
        '07': 'cdma2000 HRPD (TIA-856)',
        '08': 'E-UTRAN',
        '09': 'eHRPD',
        '0A': '3GPP NG-RAN',
        '0B': '3GPP Satellite NG-RAN',
        '0C': '3GPP Satellite E-UTRAN',
    }

    technologies = []
    for i in range(0, len(value), 2):
        tech_code = value[i:i+2]
        tech_description = technology_map.get(tech_code, 'Unknown Technology')
        technologies.append(tech_description)
    return ', '.join(technologies)


def timer_identifier(value):
    if len(value) != 2:
        return f"Raw value: {value}"

    timer_map = {
        '01': 'Timer 1',
        '02': 'Timer 2',
        '03': 'Timer 3',
        '04': 'Timer 4',
        '05': 'Timer 5',
        '06': 'Timer 6',
        '07': 'Timer 7',
        '08': 'Timer 8',
    }
    return timer_map.get(value, "Reserved")


def duration_tag(value):
    if len(value) != 4:
        return f"Invalid duration value: {value}"

    time_unit_map = {
        '00': 'minutes',
        '01': 'seconds',
        '02': 'tenths of seconds',
    }
    time_unit_code = value[:2]
    time_interval_code = value[2:]

    time_unit = time_unit_map.get(time_unit_code, 'reserved')
    time_interval = int(time_interval_code, 16)

    if time_unit == 'reserved' or time_interval == 0:
        return f"Invalid duration: {value}"

    if time_unit == 'tenths of seconds':
        duration = time_interval / 10.0
        unit = 'seconds'
    else:
        duration = time_interval
        unit = time_unit

    return f"{duration} {unit}"


def parse_imei(value):
    if len(value) % 2 != 0:
        return "Invalid IMEI length"

    imei = []
    for i in range(0, len(value), 2):
        byte = value[i:i+2]
        swapped_byte = byte[1] + byte[0]
        imei.append(swapped_byte)

    return ''.join(imei)
