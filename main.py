import os
import sys
import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
import re

from apdu_extractor import extract_apdu_messages
from apdu_parser import parse_apdu_lines_in_memory

def build_ui():
    def on_closing():
        root.destroy()
        sys.exit(0)

    root = tk.Tk()
    root.title("APDU 解析结果")
    root.geometry("1200x600")
    root.protocol("WM_DELETE_WINDOW", on_closing)

    # =========== 顶部工具条 =============
    top_frame = tk.Frame(root)
    top_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

    # 按钮：让用户点击后选择并解析 APDU 文件
    load_btn = tk.Button(top_frame, text="Load APDU", command=lambda: select_and_parse())
    load_btn.pack(side=tk.LEFT, padx=5)

    tk.Label(top_frame, text="搜索:").pack(side=tk.LEFT, padx=10)
    search_var = tk.StringVar(master=root)
    search_entry = tk.Entry(top_frame, textvariable=search_var, width=40)
    search_entry.pack(side=tk.LEFT, padx=5)

    # 在搜索框里按回车也触发搜索
    search_entry.bind("<Return>", lambda e: do_search())

    search_btn = tk.Button(top_frame, text="Search", command=lambda: do_search())
    search_btn.pack(side=tk.LEFT, padx=5)

    # =========== 主区域，使用 PanedWindow 分割 =============
    paned = tk.PanedWindow(root, orient=tk.HORIZONTAL, sashrelief=tk.RAISED)
    paned.pack(fill=tk.BOTH, expand=True)

    # ---------------- 左侧 Frame ----------------
    left_frame = tk.Frame(paned)
    left_frame.pack(fill=tk.BOTH, expand=True)

    # 在 left_frame 内创建一个滚动条，用于 Listbox 的垂直滚动
    scrollbar_y = tk.Scrollbar(left_frame, orient=tk.VERTICAL)
    scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

    listbox = tk.Listbox(left_frame, yscrollcommand=scrollbar_y.set)
    listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar_y.config(command=listbox.yview)

    paned.add(left_frame, minsize=200)

    # ---------------- 右侧 Frame ----------------
    right_frame = tk.Frame(paned)
    right_frame.pack(fill=tk.BOTH, expand=True)
    paned.add(right_frame, minsize=300)

    # 在右侧 Frame 里分上下布局 (8:2)
    right_frame.rowconfigure(0, weight=8)
    right_frame.rowconfigure(1, weight=2)
    right_frame.columnconfigure(0, weight=1)

    text_details = scrolledtext.ScrolledText(right_frame, wrap=tk.WORD)
    text_details.grid(row=0, column=0, sticky="nsew")

    text_raw = scrolledtext.ScrolledText(right_frame, wrap=tk.WORD)
    text_raw.grid(row=1, column=0, sticky="nsew")

    # ========== 维护全局数据 ==========
    # 起初没有解析任何数据
    all_items = []
    all_items_filtered = []

    # -------- 函数：更新左侧列表 --------
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

    # -------- 列表选中回调 --------
    def on_select(evt):
        nonlocal all_items_filtered
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

    # -------- 搜索函数(正则) --------
    def do_search():
        nonlocal all_items_filtered
        pattern_str = search_var.get().strip()
        if not pattern_str:
            # 无输入就显示全部
            all_items_filtered = all_items[:]
            update_listbox(all_items_filtered)
            if all_items_filtered:
                listbox.select_set(0)
                listbox.event_generate("<<ListboxSelect>>")
            else:
                # 若根本没数据
                text_details.delete(1.0, tk.END)
                text_raw.delete(1.0, tk.END)
            return

        # 编译正则
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

    # -------- 让用户选择并解析 APDU 文件 --------
    def select_and_parse():
        nonlocal all_items, all_items_filtered
        # 弹出文件选择对话框
        file_path = filedialog.askopenfilename(
            title="选择包含raw APDU的日志文件",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if not file_path:
            # 用户取消选择
            return

        # 调用 extract_apdu_messages 从文件解析
        messages = extract_apdu_messages(file_path)
        if not messages:
            messagebox.showwarning("Warning", "没有提取到任何APDU消息！")
            return

        # 将解析后的 APDU 放入内存再进一步解析
        parsed = parse_apdu_lines_in_memory(messages)

        # 用新的数据更新
        all_items = parsed
        all_items_filtered = all_items[:]
        update_listbox(all_items_filtered)
        if all_items_filtered:
            listbox.select_set(0)
            listbox.event_generate("<<ListboxSelect>>")

    root.mainloop()

def main():
    # 不自动调用 select_file_and_extract()
    # 仅创建UI让用户自行点击"Load APDU"加载文件。
    build_ui()

if __name__ == "__main__":
    main()
