# MQTT JSON 快速生成器

这是一个基于 Python Tkinter 的 MQTT 协议 JSON 生成工具。它不直接连接 MQTT 服务器，只负责根据协议填写参数、生成 JSON，并将结果复制到剪贴板，方便粘贴到 MQTT 客户端发送。

## 当前功能

主界面目前提供以下功能：

1. 写网关参数
2. 读网关参数
3. 读设备参数
4. 写设备参数
5. OTA 升级网关

每个功能都有独立窗口。生成 JSON 后，窗口右侧会同时显示生成内容、发送 topic 和订阅 topic。topic 提示区域可以用鼠标选中，并使用 `Ctrl+C` 复制。

## 运行环境

- Windows
- Python 3.8 或更高版本
- 仅使用 Python 标准库 Tkinter、CSV 和 JSON，不需要额外安装第三方依赖

启动：

```powershell
python app.py
```

## 功能说明

### 写网关参数

填写网关 SN 和消息 ID `mid`，点击“添加字段”，选择参数并填写值。参数范围只作为提示，不会阻止输入超范围值。

```json
{
  "t": "set",
  "d": {
    "03230619179356C9": {
      "upload_interval_min": "10",
      "change_check_sec": "3",
      "mid": 301
    }
  }
}
```

```text
发送：/s2/<SN>
订阅：/d2/<SN>
```

### 读网关参数

填写网关 SN 和 `mid`，可以读取全部参数，也可以取消“读取全部”后多选指定参数。

读取全部：

```json
{"t":"call","d":{"03230619179356C9":{"ts":[],"mid":101}}}
```

读取指定参数：

```json
{"t":"call","d":{"03230619179356C9":{"ts":["model","fw","sys_last_error"],"mid":102}}}
```

```text
发送：/s2/<SN>
订阅：/d2/<SN>
```

### 读设备参数

填写设备 ID 和 `mid`，可以读取全部设备点位，也可以取消“读取全部设备点位”后多选指定点位。

```json
{"t":"call","d":{"1":{"ts":["aaa","bbb"],"mid":202}}}
```

```text
发送：/s/<设备ID>
订阅：/d/<设备ID>
```

### 写设备参数

填写设备 ID 和 `mid`，点击“添加字段”，选择点位并填写值。写入值按输入内容作为字符串发送。

```json
{
  "t": "set",
  "d": {
    "1": {
      "aaa": "5",
      "bbb": "500",
      "mid": 203
    }
  }
}
```

```text
发送：/s/<设备ID>
订阅：/d2/<设备ID>
```

### OTA 升级网关

填写网关 SN、固件 HTTP/HTTPS 地址、CRC32、固件大小（字节）和 `mid`。CRC32 支持十进制或 `0x` 开头的十六进制格式。

```json
{
  "t": "ota",
  "d": {
    "03230619179356C9": {
      "url": "http://example.com/firmware.bin",
      "crc": "0xED88320",
      "size": "524288",
      "mid": 501
    }
  }
}
```

```text
发送：/s2/<SN>
订阅：/d2/<SN>
```

OTA 结果需要查看订阅到的 OTA ack。升级成功后网关会自动重启；升级期间重复发送可能返回 `busy`。

## 参数配置表

当前使用两个 CSV 参数表。CSV 可以直接使用 Excel 打开、编辑和保存；请保留文件名和表头结构。

### gateway_params.csv

网关参数表，用于读写网关参数。

| 字段 | 用途 |
|---|---|
| `name` | 界面下拉列表显示名称 |
| `tag` | 协议中实际发送的参数名 |
| `type` | 类型提示，例如 `number`、`string`、`bool` |
| `range` | 合法取值范围提示，不做强制拦截 |
| `reboot` | 修改后是否需要重启的说明 |
| `EPM` | 是否适用于 EPM |
| `EHV` | 是否适用于 EHV |
| `default` | 默认值说明 |

示例：

```csv
name,tag,type,range,reboot,EPM,EHV,default
上报周期（分钟）,upload_interval_min,number,1~60,否,是,是,5
```

### slave_params.csv

设备点位参数表，用于读写设备参数。目前放置的是占位字段，后续可以替换为实际设备点表。

```csv
name,tag,type,range,default
占位参数 AAA,aaa,number,0~10,0
占位参数 BBB,bbb,number,100~1000,100
占位参数 CCC,ccc,string,ON / OFF,OFF
占位参数 DDD,ddd,number,1~255,1
```

字段含义：

| 字段 | 用途 |
|---|---|
| `name` | 界面显示名称 |
| `tag` | 设备点表中的实际标签名 |
| `type` | 类型提示 |
| `range` | 合法范围提示，不做强制拦截 |
| `default` | 默认值说明 |

修改参数表后，在对应窗口点击“重新读取参数表”，新字段会出现在下拉列表或多选列表中。重新打开窗口也会自动读取最新文件。

## 输入规则

- 网关 SN 会自动转换为大写。
- `mid` 必须是整数。
- 设备 ID 必须填写，协议中通常是 Modbus 设备地址。
- 写入值不会被强制转换，按输入内容作为字符串生成。
- 参数范围目前只用于提示，超范围值仍然可以生成。
- 读操作中 `ts: []` 表示读取全部；指定标签数组表示仅读取选定参数。

## 文件结构

```text
jsonQuickGenerate/
├─ app.py
├─ gateway_params.csv
├─ slave_params.csv
├─ README.md
├─ .gitignore
└─ extra/                 # 协议原始文件，已被 Git 忽略
```

`extra` 文件夹用于保存协议原始 Word/PDF 文件，已经通过 `.gitignore` 忽略，不会提交到 Git。

## 当前未实现内容

当前程序只生成 JSON，不直接连接或发送 MQTT。后续可以继续扩展：

- MQTT Broker 地址、端口、用户名和密码配置
- 直接发布 JSON
- 自动订阅并显示回复
- 设备点表按设备型号区分
- 参数类型和范围的可选强校验
- 网关操作，例如 `reboot` 和 `factoryReset`
- OTA 地址、CRC 和文件大小自动校验
