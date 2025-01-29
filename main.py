import os
import tkinter as tk
from tkinter import scrolledtext, messagebox
import re

from apdu_extractor import select_file_and_extract
from apdu_parser import parse_apdu_lines_in_memory

def build_ui(parsed_items):
    # 1) 创建主窗口
    root = tk.Tk()
    root.title("APDU 解析结果查看 (支持正则搜索)")

    # 2) 顶部搜索区
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

    main_frame = tk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True)

    # 左边列表
    left_frame = tk.Frame(main_frame)
    left_frame.pack(side=tk.LEFT, fill=tk.BOTH)

    listbox = tk.Listbox(left_frame, width=50)
    listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # 右边分上下布局(8:2)
    right_frame = tk.Frame(main_frame)
    right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    right_frame.rowconfigure(0, weight=8)
    right_frame.rowconfigure(1, weight=2)
    right_frame.columnconfigure(0, weight=1)

    text_details = scrolledtext.ScrolledText(right_frame, wrap=tk.WORD)
    text_details.grid(row=0, column=0, sticky="nsew")

    text_raw = scrolledtext.ScrolledText(right_frame, wrap=tk.WORD)
    text_raw.grid(row=1, column=0, sticky="nsew")

    # 所有items（不经过搜索）
    all_items = parsed_items[:]
    # 当前显示（过滤后）的列表
    all_items_filtered = all_items[:]

    def update_listbox(show_items):
        listbox.delete(0, tk.END)
        for it in show_items:
            listbox.insert(tk.END, it["title"])

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
        """
        支持正则表达式搜索。
        - 若用户输入为空，则显示所有
        - 若用户输入非空，则编译为正则表达式，并用 re.search(pattern, title, re.IGNORECASE) 做匹配
        - 若正则无效，弹窗提示
        """
        nonlocal all_items_filtered
        # 取输入框字符串
        pattern_str = search_var.get().strip()
        print(">>> do_search() called, raw input =", repr(pattern_str))

        # 若搜索框为空，显示所有条目
        if not pattern_str:
            all_items_filtered = all_items[:]
            update_listbox(all_items_filtered)
            if all_items_filtered:
                listbox.select_set(0)
                listbox.event_generate("<<ListboxSelect>>")
            return

        # 编译正则表达式（忽略大小写）
        try:
            regex = re.compile(pattern_str, re.IGNORECASE)
        except re.error as e:
            messagebox.showerror("Regex Error", f"无效的正则表达式: {e}")
            return

        # 逐条匹配
        filtered = []
        for it in all_items:
            title_lower = it["title"]
            # 若匹配成功则加入结果
            if regex.search(title_lower):
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

    # 初始化
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
