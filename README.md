# MQTT JSON 快速生成器

## 运行

```powershell
python app.py
```

当前版本实现“写网关参数”：输入网关 SN 和消息 ID，添加一个或多个参数，填写值后生成并复制：

```json
{"t":"set","d":{"<SN>":{"<tag>":"<value>","mid":1}}}
```

## 修改参数

直接编辑 `gateway_params.csv`（网关参数）或 `slave_params.csv`（设备点位参数）。它们都可以用 Excel 打开、编辑和保存。字段含义如下：

- `name`：下拉列表显示名称
- `tag`：协议中真正发送的字段名
- `type`：类型提示
- `range`：合法范围提示，不做强制拦截
- `reboot`、`EPM`、`EHV`、`default`：协议说明信息

编辑后点击“重新读取参数表”，下拉列表即可更新；重新打开窗口也会自动读取最新内容。
