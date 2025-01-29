import os
import sys
import tkinter as tk
from tkinter import scrolledtext, messagebox
import re

from apdu_extractor import select_file_and_extract
from apdu_parser import parse_apdu_lines_in_memory

def build_ui(parsed_items):
    def on_closing():
        root.destroy()
        sys.exit(0)

    root = tk.Tk()
    root.title("APDU 解析结果 - Listbox带滚动条")
    root.geometry("1200x600")
    root.protocol("WM_DELETE_WINDOW", on_closing)

    # =========== 顶部搜索区 =============
    top_frame = tk.Frame(root)
    top_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

    tk.Label(top_frame, text="搜索(正则):").pack(side=tk.LEFT)
    search_var = tk.StringVar(master=root)
    search_entry = tk.Entry(top_frame, textvariable=search_var, width=40)
    search_entry.pack(side=tk.LEFT, padx=5)

    # 在搜索框里按回车也触发搜索
    search_entry.bind("<Return>", lambda e: do_search())

    search_btn = tk.Button(top_frame, text="Search", command=lambda: do_search())
    search_btn.pack(side=tk.LEFT, padx=5)

    # =========== 下面主区域，用 PanedWindow 来分割 =============
    paned = tk.PanedWindow(root, orient=tk.HORIZONTAL, sashrelief=tk.RAISED)
    paned.pack(fill=tk.BOTH, expand=True)

    # --- 左侧 Frame ---
    left_frame = tk.Frame(paned)
    left_frame.pack(fill=tk.BOTH, expand=True)

    # 在 left_frame 内创建一个滚动条，用于 Listbox 的垂直滚动
    scrollbar_y = tk.Scrollbar(left_frame, orient=tk.VERTICAL)
    scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

    # 创建 Listbox，并关联滚动条
    listbox = tk.Listbox(left_frame, yscrollcommand=scrollbar_y.set)
    listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # 设置滚动条命令，让它控制 Listbox
    scrollbar_y.config(command=listbox.yview)

    # 将左侧 Frame 添加到 PanedWindow
    paned.add(left_frame, minsize=200)

    # --- 右侧 Frame ---
    right_frame = tk.Frame(paned)
    right_frame.pack(fill=tk.BOTH, expand=True)
    paned.add(right_frame, minsize=300)

    # 在右侧 Frame 里再分上下布局 (8:2)
    right_frame.rowconfigure(0, weight=8)
    right_frame.rowconfigure(1, weight=2)
    right_frame.columnconfigure(0, weight=1)

    text_details = scrolledtext.ScrolledText(right_frame, wrap=tk.WORD)
    text_details.grid(row=0, column=0, sticky="nsew")

    text_raw = scrolledtext.ScrolledText(right_frame, wrap=tk.WORD)
    text_raw.grid(row=1, column=0, sticky="nsew")

    # 全部 items（未过滤）
    all_items = parsed_items[:]
    # 当前显示（过滤后）
    all_items_filtered = all_items[:]

    def update_listbox(show_items):
        listbox.delete(0, tk.END)
        for it in show_items:
            index = listbox.size()
            listbox.insert(tk.END, it["title"])
            title = it["title"]
            if "TERMINAL=>UICC" in title.upper():
                listbox.itemconfig(index, foreground="blue")
            elif "UICC=>TERMINAL" in title.upper():
                listbox.itemconfig(index, foreground="red")

    def on_select(evt):
        if not all_items_filtered:
            return
        idx = listbox.curselection()
        if not idx:
            return
        sel_index = idx[0]
        item = all_items_filtered[sel_index]

        text_details.delete(1.0, tk.END)
        text_details.insert(tk.END, item["details"])

        text_raw.delete(1.0, tk.END)
        text_raw.insert(tk.END, item["raw"])

    listbox.bind("<<ListboxSelect>>", on_select)

    def do_search():
        nonlocal all_items_filtered
        pattern_str = search_var.get().strip()
        if not pattern_str:
            all_items_filtered = all_items[:]
            update_listbox(all_items_filtered)
            if all_items_filtered:
                listbox.select_set(0)
                listbox.event_generate("<<ListboxSelect>>")
            return

        try:
            regex = re.compile(pattern_str, re.IGNORECASE)
        except re.error as e:
            messagebox.showerror("Regex Error", f"无效的正则表达式: {e}")
            return

        filtered = []
        for it in all_items:
            title_text = it["title"]
            if regex.search(title_text):
                filtered.append(it)

        all_items_filtered = filtered
        update_listbox(all_items_filtered)
        if all_items_filtered:
            listbox.select_set(0)
            listbox.event_generate("<<ListboxSelect>>")
        else:
            text_details.delete(1.0, tk.END)
            text_raw.delete(1.0, tk.END)
            messagebox.showinfo("提示", f"未搜索到匹配正则 '{pattern_str}' 的项")

    # 初始化列表
    update_listbox(all_items_filtered)
    if all_items_filtered:
        listbox.select_set(0)
        listbox.event_generate("<<ListboxSelect>>")

    root.mainloop()

def main():
    # 第一步：选择文件并提取 APDU
    select_file_and_extract()

    # 提取好的数据保存在 extracted_messages.txt
    if not os.path.exists("extracted_messages.txt"):
        print("未找到 extracted_messages.txt，可能未成功选择文件或无解析结果。")
        return

    with open("extracted_messages.txt", "r") as f:
        lines = f.readlines()

    # 第二步：解析为结构化数据
    parsed_items = parse_apdu_lines_in_memory(lines)

    # 第三步：构建 UI
    build_ui(parsed_items)

if __name__ == "__main__":
    main()
