import tkinter as tk
from tkinter import ttk
from tkinter import messagebox  # 导入messagebox模块
import re  # 导入正则表达式模块
from command_detail import duration_tag, data_destination_address_tag, address_tag, bearer_description_tag, event_list_info, command_details, device_identities, result_details, location_info, parse_channel_status, access_technology, timer_identifier, parse_imei
from apdu_extractor import select_file_and_extract
import os

def proactivate_uicc_cmd_parse():
    with open("extracted_messages.txt", "r") as file:
        lines = file.readlines()

    parsed_messages = []
    raw_messages = []  # 添加一个列表来存储原始数据

    for input_data in lines:
        input_data = input_data.strip()
        output = ""
        if input_data.startswith("D0"):
            output = "uicc=>terminal: proactive command"
            if input_data[4:6] == "81":
                length = int(input_data[2:4], 16)
                output += cmd_parse(input_data[4:4+length*2], length)
            else:
                length = int(input_data[4:6], 16)
                output += f"\tdata abnormal: {input_data}\n"
                output += cmd_parse(input_data[6:6+length*2], length)

        elif input_data.startswith("80"):
            output = "terminal=>uicc: "
            length = int(input_data[8:10], 16)
            body_data = input_data[10:10+length*2]
            tlv_type = ber_tlv_check(body_data[:2])
            if tlv_type != "COMPREHENSION_TLV":     #如果是ber tlv，将选择不同的body数据
                length = int(input_data[12:14], 16)
                body_data = input_data[14:14+length*2]

            if input_data.startswith("8014"):
                if tlv_type != "COMPREHENSION_TLV":
                    output += f"\tTerminal Response - {tlv_type}\n"
                else:
                    output += "\tTerminal Response\n"
                output += cmd_parse(body_data, length)
            elif input_data.startswith("80C2"):
                if tlv_type != "COMPREHENSION_TLV":
                    output += f"\tEnvelope - {tlv_type}\n"
                else:
                    output += "\tEnvelope\n"
                output += cmd_parse(body_data, length)
            elif input_data.startswith("8010"):
                output += "\tterminal profile\n"
            elif input_data.startswith("80AA"):
                output += "\tTERMINAL CAPABILITY\n"
            elif input_data.startswith("8012"):
                output += "\tFetch command\n"
            elif input_data.startswith("80F2"):
                output += "\tStatus\n"
            else:
                output += f"\tunknown command: {input_data[0:4]}\n"

        else:
            output = "unknown command\n"

        parsed_messages.append(output)  # 将解析后的输出添加到列表中
        raw_messages.append(input_data)  # 将原始数据添加到列表中

    return parsed_messages, raw_messages  # 返回解析后的消息和原始数据

def cmd_parse(input_data, length):
    output = ""
    index = 0
    while index < length * 2:
        tag = input_data[index:index+2]
        index += 2  # 跳过tag
        length_byte = int(input_data[index:index+2], 16)
        index += 2  # 跳过长度
        value = input_data[index:index + (length_byte * 2)]
        index += length_byte * 2  # 跳过值

        if tag == "01" or tag == "81":
            command = command_details(value)
            output += f"\t{command}\n"
        elif tag == "02" or tag == "82":
            identities = device_identities(value)
            output += f"\t{identities}\n"
        elif tag == "03" or tag == "83":
            result = result_details(value)
            output += f"\t{result}\n"
        elif tag == "04" or tag == "84":
            duration = duration_tag(value)
            output += f"\tDuration: {duration}\n"
        elif tag == "05" or tag == "85":
            output += f"\tAlpha identifier tag: {value}\n"
        elif tag == "06" or tag == "86":
            address = address_tag(value)
            output += f"\tAddress tag: {address}\n" 
        elif tag == "38" or tag == "B8":
            channel_info = parse_channel_status(value)
            output += f"\tChannel status: {channel_info}\n"
        elif tag == "0B" or tag == "8B":
            output += f"\tSMS TPDU: {value}\n" 
        elif tag == "B9" or tag == "39":
            Buffer_size = int(value,16)
            output += f"\tBuffer size: {Buffer_size}\n" 
        elif tag == "47" or tag == "C7":
            if length_byte < 30:
                network_access_name = bytes.fromhex(value[2:length_byte*2]).decode('ascii')
                output += f"\tNetwork Access Name: {network_access_name}\n" 
            else:
                output += f"\tNetwork Access Name: {value}\n" 
        elif tag == "FC" or tag == "7C":
            output += f"\tEPS PDN connection activation parameters: {value}\n" 
        elif tag == "3C" or tag == "BC":
            type_value = value[0:2]
            port_value = value[2:]
            if type_value == "01":
                protocol_type = "UDP, UICC in client mode, remote connection"
            elif type_value == "02":
                protocol_type = "TCP, UICC in client mode, remote connection"
            elif type_value == "03":
                protocol_type = "TCP, UICC in server mode"
            elif type_value == "04":
                protocol_type = "UDP, UICC in client mode, local connection"
            elif type_value == "05":
                protocol_type = "TCP, UICC in client mode, local connection"
            elif type_value == "06":
                protocol_type = "direct communication channel"
            else:
                protocol_type = f"Unknown protocol type: {type_value}"
            
            port = int(port_value,16)

            output += f"\tTransport protocol type: {protocol_type}, port: {port}\n" 
        elif tag == "FD" or tag == "7D":
            mccmnc_raw = value[0:6]
            mccmnc = f"{mccmnc_raw[1]}{mccmnc_raw[0]}{mccmnc_raw[3]}{mccmnc_raw[5]}{mccmnc_raw[4]}{mccmnc_raw[2]}"
            tac = value[6:]
            output += f"\tMCCMNC: {mccmnc},TAC: {tac}\n"                                   
        elif tag == "B5" or tag == "35":
            Bearer_description = bearer_description_tag(value)
            output += f"\tBearer description tag: {Bearer_description}\n"            
        elif tag == "13" or tag == "93":
            location = location_info(value)
            output += f"\t{location}\n"
        elif tag == "14" or tag == "94":
            imei = parse_imei(value)
            output += f"\tIMEI: {imei}\n"
        elif tag == "62" or tag == "E2":
            imeisv = parse_imei(value)
            output += f"\tIMEISV: {value}\n"
        elif tag == "6F" or tag == "EF":
            output += f"\tMMS Notification: {value}\n"
        elif tag == "33" or tag == "B3":
            output += f"\tProvisioning Reference File: {value}\n"
        elif tag == "19" or tag == "99":
            event = event_list_info(value)
            output += f"\tEvent list tag: {event}\n"
        elif tag == "1B" or tag == "9B":
            if value == "00":
                location_status_tag = "Normal service"
            elif value == "01":
                location_status_tag = "Limited service"
            elif value == "02":
                location_status_tag = "No service"
            else:
                location_status_tag = "unknown status"
            output += f"\tLocation status tag: {location_status_tag}\n"
        elif tag == "2F" or tag == "AF":
            output += f"\tAID: {value}\n"
        elif tag == "3E" or tag == "BE":
            data_destination_address = data_destination_address_tag(value)
            output += f"\tdata destination address: {data_destination_address}\n"
        elif tag == "36" or tag == "B6":
            output += f"\tChannel data: {value}\n"
        elif tag == "37" or tag == "B7":
            output += f"\tChannel data length: {value}\n"
        elif tag == "3F" or tag == "BF":
            technologies = access_technology(value)
            output += f"\tAccess Technology: {technologies}\n"
        elif tag == "F4" or tag == "74":
            output += f"\tAttach Type: {value}\n"
        elif tag == "F5" or tag == "75":
            output += f"\tRejection Cause: {value}\n"
        elif tag == "A2" or tag == "22":
            output += f"\tC-APDU: {value}\n"
        elif tag == "A4" or tag == "24":
            timer_desc = timer_identifier(value)
            output += f"\tTimer identifier: {timer_desc}\n"
        elif tag == "A5" or tag == "25":
            time_value = ":".join([value[0:2], value[2:4], value[4:6]])
            output += f"\tTimer: {time_value}\n"
        elif tag == "21" or tag == "A1":
            output += f"\tCard ATR: {value}\n"
        elif tag == "E0" or tag == "60":
            output += f"\tMAC: {value}\n"
        elif tag == "A6" or tag == "26":
            output += f"\tDate-Time and Time zone: {value}\n"
        elif tag == "6C" or tag == "EC":
            output += f"\tMMS Transfer Status: {value}\n"
        elif tag == "7E" or tag == "FE":
            output += f"\tCSG ID list: {value}\n"
        elif tag == "56" or tag == "D6":
            output += f"\tCSG ID: {value}\n"
        elif tag == "57" or tag == "D7":
            output += f"\tTimer Expiration: {value}\n"
        else:
            print("Unknown tag: ",tag, "length: ",length_byte, "value: ",value)
            # print("Unknown tag: ",tag)
            output += f"Unknown tag: {tag} length: {length_byte} value: {value}\n"

    return output

def ber_tlv_check(input_data):
    # print("ber_tlv_check",input_data)
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

def create_ui(parsed_messages, raw_messages):
    root = tk.Tk()
    root.title("解析结果显示")
    root.geometry("700x700")  # 减少窗口初始宽度约30%

    # 上部搜索框
    search_frame = ttk.Frame(root)
    search_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

    search_label = ttk.Label(search_frame, text="搜索 (支持正则表达式):")
    search_label.pack(side=tk.LEFT, padx=(0,5))

    search_var = tk.StringVar()
    search_entry = ttk.Entry(search_frame, textvariable=search_var)
    search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

    search_button = ttk.Button(search_frame, text="搜索")
    search_button.pack(side=tk.LEFT, padx=5)

    # 在搜索框旁边添加"重置"按钮
    reset_button = ttk.Button(search_frame, text="重置")
    reset_button.pack(side=tk.LEFT, padx=5)

    # 左侧列表框，添加水平滚动条
    list_frame = ttk.Frame(root)
    list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

    # 创建一个子帧用于 Listbox 和垂直滚动条
    listbox_frame = ttk.Frame(list_frame)
    listbox_frame.pack(fill=tk.BOTH, expand=True)

    # 创建 Listbox 首先
    listbox = tk.Listbox(listbox_frame, selectmode=tk.SINGLE, width=70)  # 减少宽度约30%
    listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # 创建垂直滚动条
    scrollbar_y = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=listbox.yview)
    scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
    listbox.config(yscrollcommand=scrollbar_y.set)

    # 创建水平滚动条
    scrollbar_x = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=listbox.xview)
    scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
    listbox.config(xscrollcommand=scrollbar_x.set)

    # 右侧详细信息显示
    detail_frame = ttk.Frame(root)
    detail_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

    detail_text = tk.Text(detail_frame, wrap=tk.WORD, height=15)
    detail_text.pack(fill=tk.BOTH, expand=True)

    # 底部原始数据显示
    raw_frame = ttk.Frame(root)
    raw_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=5, pady=5)

    raw_label = ttk.Label(raw_frame, text="原始数据:")
    raw_label.pack(side=tk.TOP, anchor=tk.W)

    raw_text = tk.Text(raw_frame, wrap=tk.WORD, height=10, bg="#f0f0f0")
    raw_text.pack(fill=tk.BOTH, expand=True)

    # 将解析后的消息添加到列表框
    for idx, msg in enumerate(parsed_messages):
        first_line = msg.split('\n')[0].strip()
        if first_line.startswith("terminal=>uicc:"):
            listbox.insert(tk.END, first_line)
            listbox.itemconfig(tk.END, {'fg': 'blue'})  # 使用tk.END而不是idx
        elif first_line.startswith("uicc=>terminal:"):
            listbox.insert(tk.END, first_line)
            listbox.itemconfig(tk.END, {'fg': 'red'})
        else:
            listbox.insert(tk.END, first_line)

    # 绑定选中事件
    def on_select(event):
        selected_indices = listbox.curselection()
        if selected_indices:
            index = selected_indices[0]
            msg = parsed_messages[index]
            raw_msg = raw_messages[index]
            detail_text.delete(1.0, tk.END)
            detail_text.insert(tk.END, msg)
            raw_text.delete(1.0, tk.END)
            raw_text.insert(tk.END, raw_msg)

    listbox.bind('<<ListboxSelect>>', on_select)

    # 搜索功能
    def search():
        pattern = search_var.get()
        try:
            regex = re.compile(pattern, re.IGNORECASE)  # 添加忽略大小写标志
        except re.error:
            messagebox.showerror("错误", "无效的正则表达式")
            return

        listbox.delete(0, tk.END)
        for idx, msg in enumerate(parsed_messages):
            first_line = msg.split('\n')[0].strip()
            if regex.search(first_line):
                if first_line.startswith("terminal=>uicc:"):
                    listbox.insert(tk.END, first_line)
                    listbox.itemconfig(tk.END, {'fg': 'blue'})
                elif first_line.startswith("uicc=>terminal:"):
                    listbox.insert(tk.END, first_line)
                    listbox.itemconfig(tk.END, {'fg': 'red'})
                else:
                    listbox.insert(tk.END, first_line)

    search_button.config(command=search)

    # 重置搜索功能
    def reset_search():
        search_var.set("")
        listbox.delete(0, tk.END)
        for idx, msg in enumerate(parsed_messages):
            first_line = msg.split('\n')[0].strip()
            if first_line.startswith("terminal=>uicc:"):
                listbox.insert(tk.END, first_line)
                listbox.itemconfig(tk.END, {'fg': 'blue'})
            elif first_line.startswith("uicc=>terminal:"):
                listbox.insert(tk.END, first_line)
                listbox.itemconfig(tk.END, {'fg': 'red'})
            else:
                listbox.insert(tk.END, first_line)

    reset_button.config(command=reset_search)

    root.mainloop()

def main():
    select_file_and_extract()
    parsed_messages, raw_messages = proactivate_uicc_cmd_parse()
    create_ui(parsed_messages, raw_messages)

if __name__ == "__main__":
    main()








