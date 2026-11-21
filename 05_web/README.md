# 上位机 / 审计后台（05_web）

## 一、为什么不用公网

门禁终端的价值在于**认证逻辑本身**，网络只是把日志带出来。把设备直接连公网会引入三个不必要的风险：

| 风险 | 具体表现 |
| --- | --- |
| 校园网认证 | 教室/实验室 Wi-Fi 多要网页 Portal 认证，ESP8266 过不去，必须开手机热点 |
| TLS 握手 | Supabase 等云服务强制 HTTPS，ESP-01S 做 TLS 握手吃内存、证书更新就失效 |
| 现场网络 | 答辩时网络一断，演示直接卡住 |

所以采用**本地优先（local-first）**：终端 → USB 串口 → 笔记本上的本地服务 → 浏览器面板。
不联网、不建数据库、不开服务器，答辩零风险。

## 二、当前已实现：`server/`

单文件 Python 服务，标准库实现，只依赖可选的 `pyserial`。

```bash
cd 05_web/server
python3 app.py --demo                          # 演示模式，无硬件也能看
python3 app.py --port /dev/tty.usbserial-1420  # 真实串口
# 浏览器打开 http://127.0.0.1:8000
```

功能：KPI 统计、实时日志表格、失败行高亮、锁定行标红、耗时柱状图、失败阶段构成、CSV 导出（`/export`，同时每 10 s 落盘 `logs.csv`）。

串口数据格式（一行一条，固件按此格式打印）：

```
2027-04-02T10:12:33,U01,A1B2C3D4,F3,pass,,2860
时间,用户,卡UID,阶段,结果(pass/deny/lock),原因,耗时ms
```

**想让老师用手机看**：笔记本开热点，手机连同一热点，浏览器访问 `http://<笔记本局域网IP>:8000` 即可。不需要蓝牙，也不需要公网。

## 三、可选增强：远程上报（时间富余再做）

保持同一套页面，只把数据来源从"串口"换成"网络"：

```
ESP-01S ──HTTP POST──> 局域网内笔记本(或云函数) ──> 同一套 app.py 的 /api/logs
```

要点：
- 演示仍走本地串口，远程模式作为**加分演示**，不做主路径；
- 断网时固件写内部 Flash 环形缓冲，恢复后补传，保证"本地条数 = 后台条数"（这条本身就是论文的测试点 A-10）；
- 若一定要上公网，用 Netlify Functions / Cloudflare Worker 做一层 HTTP→HTTPS 中转，避免在 ESP-01S 上做 TLS。

## 四、数据表（若后续接 Supabase）

```sql
users(id, name, card_uid, finger_id, pin_hash, role, enabled, created_at)
access_logs(id, user_id, card_uid, stage, result, elapsed_ms, reason, created_at)
devices(id, name, token, last_seen_at)
```

原则：**密码只存哈希、不提供"查看明文"**，可写进论文"安全设计"小节。
