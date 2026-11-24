import csv
import json
import os
import tkinter as tk
from tkinter import ttk, messagebox


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "gateway_params.csv")


def load_params():
    """Load the editable parameter table every time the dialog opens."""
    rows = []
    with open(CONFIG_FILE, "r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            if row.get("tag", "").strip():
                rows.append(row)
    return rows


def value_hint(row):
    kind = row.get("type", "string")
    scope = row.get("range", "")
    return f"类型: {kind}    合法范围提示: {scope or '无'}"


class WriteGatewayDialog(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("写网关参数")
        self.geometry("1350x728")
        self.resizable(True, True)
        self.rows = []
        self.param_defs = load_params()
        self.build()

    def build(self):
        top = ttk.Frame(self, padding=10)
        top.pack(fill="x")
        ttk.Label(top, text="网关 SN:").grid(row=0, column=0, sticky="w")
        self.sn = ttk.Entry(top, width=28)
        self.sn.grid(row=0, column=1, padx=(6, 20), sticky="w")
        ttk.Label(top, text="消息 ID mid:").grid(row=0, column=2, sticky="w")
        self.mid = ttk.Entry(top, width=12)
        self.mid.insert(0, "1")
        self.mid.grid(row=0, column=3, padx=6, sticky="w")
        ttk.Button(top, text="重新读取参数表", command=self.reload_params).grid(row=0, column=4, padx=8)

        bar = ttk.Frame(self, padding=(10, 0))
        bar.pack(fill="x")
        ttk.Button(bar, text="＋ 添加字段", command=self.add_row).pack(side="left")
        ttk.Label(bar, text="提示仅用于提醒，超出范围仍允许生成").pack(side="left", padx=12)

        content = ttk.Frame(self)
        content.pack(fill="both", expand=True)
        self.table = ttk.Frame(content, padding=10)
        self.table.pack(side="left", fill="both", expand=True)
        self.draw_header()
        self.add_row()

        bottom = ttk.Frame(content, padding=10, width=430)
        bottom.pack(side="right", fill="both", expand=True)
        bottom.pack_propagate(False)
        ttk.Label(bottom, text="生成 JSON:").pack(anchor="w")
        self.output = tk.Text(bottom, height=8, wrap="none")
        self.output.pack(fill="both", expand=True, pady=(4, 8))
        actions = ttk.Frame(bottom)
        actions.pack(fill="x")
        ttk.Button(actions, text="生成 JSON", command=self.generate).pack(side="left")
        ttk.Button(actions, text="复制到剪贴板", command=self.copy_json).pack(side="left", padx=8)

    def draw_header(self):
        for col, text in enumerate(("参数", "值", "范围提示", "")):
            ttk.Label(self.table, text=text).grid(row=0, column=col, padx=4, pady=4, sticky="w")

    def reload_params(self):
        try:
            self.param_defs = load_params()
            messagebox.showinfo("已更新", "参数表已重新读取，下拉列表已更新。", parent=self)
        except Exception as e:
            messagebox.showerror("读取失败", str(e), parent=self)

    def add_row(self):
        row_no = len(self.rows) + 1
        tag_var = tk.StringVar()
        value_var = tk.StringVar()
        combo = ttk.Combobox(self.table, textvariable=tag_var, width=50, state="readonly")
        combo["values"] = [f"{x['name']} ({x['tag']})" for x in self.param_defs]
        combo.grid(row=row_no, column=0, padx=4, pady=4, sticky="ew")
        value = ttk.Entry(self.table, textvariable=value_var, width=12)
        value.grid(row=row_no, column=1, padx=4, pady=4, sticky="ew")
        hint = ttk.Label(self.table, text="请选择参数")
        hint.grid(row=row_no, column=2, padx=4, pady=4, sticky="w")
        remove = ttk.Button(self.table, text="删除", command=lambda: self.remove_row(item))
        remove.grid(row=row_no, column=3, padx=4, pady=4)
        item = (combo, value, hint, tag_var, value_var)
        self.rows.append(item)

        def changed(_=None):
            selected = combo.get()
            match = next((x for x in self.param_defs if f"{x['name']} ({x['tag']})" == selected), None)
            hint.config(text=value_hint(match) if match else "请选择参数")
        combo.bind("<<ComboboxSelected>>", changed)

    def remove_row(self, item):
        if len(self.rows) == 1:
            return
        for widget in item[:3]:
            widget.destroy()
        self.rows.remove(item)

    def collect(self):
        payload = {}
        for combo, _, _, _, value_var in self.rows:
            selected = combo.get()
            if not selected:
                continue
            tag = selected.rsplit(" (", 1)[-1].rstrip(")")
            payload[tag] = value_var.get()
        return payload

    def generate(self):
        sn = self.sn.get().strip().upper()
        mid = self.mid.get().strip()
        if not sn:
            messagebox.showwarning("缺少 SN", "请输入网关 SN。", parent=self)
            return
        if not mid.isdigit():
            messagebox.showwarning("mid 无效", "消息 ID 请输入整数。", parent=self)
            return
        payload = self.collect()
        if not payload:
            messagebox.showwarning("缺少字段", "至少添加一个要写入的字段。", parent=self)
            return
        payload["mid"] = int(mid)
        result = {"t": "set", "d": {sn: payload}}
        self.output.delete("1.0", "end")
        self.output.insert("1.0", json.dumps(result, ensure_ascii=False, indent=2))

    def copy_json(self):
        text = self.output.get("1.0", "end").strip()
        if not text:
            self.generate()
            text = self.output.get("1.0", "end").strip()
        if text:
            self.clipboard_clear()
            self.clipboard_append(text)
            messagebox.showinfo("已复制", "JSON 已复制到剪贴板。", parent=self)


class ReadGatewayDialog(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("读网关参数")
        self.geometry("1066x728")
        self.resizable(True, True)
        self.param_defs = load_params()
        self.build()

    def build(self):
        top = ttk.Frame(self, padding=10)
        top.pack(fill="x")
        ttk.Label(top, text="网关 SN:").grid(row=0, column=0, sticky="w")
        self.sn = ttk.Entry(top, width=32)
        self.sn.grid(row=0, column=1, padx=(6, 20), sticky="w")
        ttk.Label(top, text="消息 ID mid:").grid(row=0, column=2, sticky="w")
        self.mid = ttk.Entry(top, width=14)
        self.mid.insert(0, "1")
        self.mid.grid(row=0, column=3, padx=6, sticky="w")
        ttk.Button(top, text="重新读取参数表", command=self.reload_params).grid(row=0, column=4, padx=8)

        content = ttk.Frame(self)
        content.pack(fill="both", expand=True)
        select = ttk.LabelFrame(content, text="读取范围", padding=12)
        select.pack(side="left", fill="both", expand=True, padx=(10, 5), pady=(0, 8))
        self.all_params = tk.BooleanVar(value=True)
        ttk.Checkbutton(select, text="读取全部网关参数（包含状态和只读字段）",
                        variable=self.all_params, command=self.toggle_list).pack(anchor="w")
        ttk.Label(select, text="取消勾选后，可在下方选择一个或多个参数：").pack(anchor="w", pady=(12, 4))
        list_frame = ttk.Frame(select)
        list_frame.pack(fill="both", expand=True)
        self.listbox = tk.Listbox(list_frame, selectmode=tk.MULTIPLE, exportselection=False,
                                  height=14, width=55)
        scroll = ttk.Scrollbar(list_frame, orient="vertical", command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scroll.set)
        self.listbox.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        self.reload_params(False)

        bottom = ttk.Frame(content, padding=10, width=430)
        bottom.pack(side="right", fill="both", expand=True)
        bottom.pack_propagate(False)
        ttk.Label(bottom, text="生成 JSON:").pack(anchor="w")
        self.output = tk.Text(bottom, height=9, wrap="none")
        self.output.pack(fill="both", expand=True, pady=(4, 8))
        actions = ttk.Frame(bottom)
        actions.pack(fill="x")
        ttk.Button(actions, text="生成 JSON", command=self.generate).pack(side="left")
        ttk.Button(actions, text="复制到剪贴板", command=self.copy_json).pack(side="left", padx=8)

    def toggle_list(self):
        self.listbox.configure(state="disabled" if self.all_params.get() else "normal")

    def reload_params(self, show_message=True):
        try:
            self.param_defs = load_params()
            self.listbox.delete(0, "end")
            for row in self.param_defs:
                self.listbox.insert("end", f"{row['name']} ({row['tag']})")
            self.toggle_list()
            if show_message:
                messagebox.showinfo("已更新", "参数表已重新读取。", parent=self)
        except Exception as e:
            messagebox.showerror("读取失败", str(e), parent=self)

    def generate(self):
        sn = self.sn.get().strip().upper()
        mid = self.mid.get().strip()
        if not sn:
            messagebox.showwarning("缺少 SN", "请输入网关 SN。", parent=self)
            return
        if not mid.isdigit():
            messagebox.showwarning("mid 无效", "消息 ID 请输入整数。", parent=self)
            return
        if self.all_params.get():
            tags = []
        else:
            tags = [self.param_defs[i]["tag"] for i in self.listbox.curselection()]
            if not tags:
                messagebox.showwarning("缺少字段", "请至少选择一个参数，或勾选读取全部。", parent=self)
                return
        result = {"t": "call", "d": {sn: {"ts": tags, "mid": int(mid)}}}
        self.output.delete("1.0", "end")
        self.output.insert("1.0", json.dumps(result, ensure_ascii=False, indent=2))

    def copy_json(self):
        text = self.output.get("1.0", "end").strip()
        if not text:
            self.generate()
            text = self.output.get("1.0", "end").strip()
        if text:
            self.clipboard_clear()
            self.clipboard_append(text)
            messagebox.showinfo("已复制", "JSON 已复制到剪贴板。", parent=self)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MQTT JSON 快速生成器")
        self.geometry("650x390")
        ttk.Label(self, text="MQTT JSON 快速生成器", font=("Microsoft YaHei", 18)).pack(pady=(35, 10))
        ttk.Label(self, text="根据协议生成可直接复制到 MQTT 客户端的 JSON").pack(pady=5)
        ttk.Button(self, text="写网关参数", command=lambda: WriteGatewayDialog(self)).pack(pady=15, ipadx=25, ipady=8)
        ttk.Button(self, text="读网关参数", command=lambda: ReadGatewayDialog(self)).pack(pady=8, ipadx=25, ipady=8)
        ttk.Label(self, text="后续可扩展：读/写设备、网关操作、OTA").pack(pady=8)


if __name__ == "__main__":
    App().mainloop()
