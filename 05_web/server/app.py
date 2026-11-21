#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多重验证门禁系统 · 审计后台（本地版）

设计目标：不依赖公网、不依赖数据库、不依赖 Node，一条命令跑起来。
    串口/演示数据  ->  内存 + CSV  ->  http://127.0.0.1:8000 实时刷新

用法（Windows 开发机）：
    py app.py --demo            # 演示模式（无硬件，自动生成数据）
    py app.py --port COM3       # 真实串口，设备管理器里看端口号
    py app.py --snapshot out.html   # 导出一张静态快照（写论文/PPT 用）

Mac 上（仅临时验证）：
    python3 app.py --port /dev/tty.usbserial-1420

串口数据格式（一行一条，逗号分隔）：
    2027-04-02T10:12:33,U01,A1B2C3D4,F3,pass,,2860
    字段：时间, 用户, 卡UID, 阶段, 结果(pass/deny/lock), 原因, 耗时ms
"""
import argparse
import csv
import io
import os
import random
import threading
import time
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

STAGES = {"F1": "一级·读卡", "F2": "二级·PIN", "F3": "三级·指纹"}
REASONS = {
    "card_unknown": "未登记卡",
    "pin_wrong": "PIN 错误",
    "finger_mismatch": "指纹不符",
    "window_timeout": "窗口超时",
    "factor_mismatch": "因子与用户不匹配",
    "locked": "终端锁定中",
}
RESULT_TEXT = {"pass": "通过", "deny": "拒绝", "lock": "锁定"}

# ---------------------------------------------------------------- 状态
LOCK = threading.Lock()
STATE = {"events": [], "source": "演示数据", "serial": "未连接", "started": datetime.now()}


def add_event(ts, user, uid, stage, result, reason, elapsed):
    ev = {
        "ts": ts,
        "user": user,
        "uid": uid,
        "stage": stage,
        "result": result,
        "reason": reason,
        "elapsed": elapsed,
    }
    with LOCK:
        STATE["events"].append(ev)
        STATE["events"] = STATE["events"][-500:]


def stats(events):
    today = datetime.now().date()
    todays = [e for e in events if e["ts"].date() == today]
    passed = [e for e in todays if e["result"] == "pass"]
    denied = [e for e in todays if e["result"] == "deny"]
    locked = [e for e in todays if e["result"] == "lock"]
    avg = int(sum(e["elapsed"] for e in passed) / len(passed)) if passed else 0
    return {
        "total": len(todays),
        "pass": len(passed),
        "deny": len(denied),
        "lock": len(locked),
        "avg": avg,
        "rate": (len(denied) / len(todays) * 100) if todays else 0.0,
    }


# ---------------------------------------------------------------- 演示数据
def demo_worker():
    """按真实比例生成：多数通过，少量在各级失败，连续 3 次失败触发锁定。"""
    rnd = random.Random(20270402)
    users = ["U01", "U02", "U03", "U04"]
    uids = {"U01": "A1B2C3D4", "U02": "5E6F7A8B", "U03": "C3D4E5F6", "U04": "9A8B7C6D"}
    fail_streak = 0
    lock_until = None
    while True:
        time.sleep(rnd.uniform(1.8, 3.4))
        now = datetime.now()
        if lock_until and now < lock_until:
            add_event(now, "—", "—", "F1", "deny", "locked", 60)
            continue
        user = rnd.choice(users)
        r = rnd.random()
        if r < 0.62:
            stage, res, why, el = "F3", "pass", "", rnd.randint(2100, 4300)
            fail_streak = 0
        elif r < 0.72:
            stage, res, why, el = "F1", "deny", "card_unknown", rnd.randint(70, 180)
            fail_streak += 1
        elif r < 0.86:
            stage, res, why, el = "F2", "deny", "pin_wrong", rnd.randint(1100, 2700)
            fail_streak += 1
        elif r < 0.96:
            stage, res, why, el = "F3", "deny", "finger_mismatch", rnd.randint(2300, 4200)
            fail_streak += 1
        else:
            stage, res, why, el = "F2", "deny", "window_timeout", 10000
            fail_streak += 1

        add_event(now, user, uids[user], stage, res, why, el)
        if fail_streak >= 3:
            add_event(now + timedelta(seconds=1), user, uids[user], "—", "lock", "locked", 0)
            lock_until = now + timedelta(seconds=45)
            fail_streak = 0


def serial_worker(port, baud=115200):
    try:
        import serial  # pyserial
    except ImportError:
        STATE["serial"] = "缺少 pyserial：pip3 install pyserial"
        print("[!] 未安装 pyserial，无法读取串口。演示模式可加 --demo")
        return
    try:
        ser = serial.Serial(port, baud, timeout=1)
    except Exception as exc:  # noqa: BLE001
        STATE["serial"] = f"打开失败：{exc}"
        print(f"[!] 串口打开失败：{exc}")
        return
    STATE["source"] = f"串口 {port}"
    STATE["serial"] = "已连接"
    print(f"[✓] 已连接 {port} @ {baud}")
    while True:
        try:
            line = ser.readline().decode("utf-8", "ignore").strip()
        except Exception as exc:  # noqa: BLE001
            print(f"[!] 读取异常：{exc}")
            time.sleep(1)
            continue
        if not line or line.count(",") < 5:
            continue
        parts = [p.strip() for p in line.split(",")]
        try:
            ts = datetime.fromisoformat(parts[0])
        except ValueError:
            ts = datetime.now()
        add_event(ts, parts[1], parts[2], parts[3], parts[4], parts[5],
                  int(parts[6]) if len(parts) > 6 and parts[6].isdigit() else 0)


# ---------------------------------------------------------------- 渲染
CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif;
     background:#f4f6fa;color:#16283f;padding:22px 26px 40px}
.top{display:flex;align-items:center;justify-content:space-between;margin-bottom:18px}
.title{font-size:21px;font-weight:700;letter-spacing:.3px}
.title span{color:#2f5d9e}
.sub{font-size:12.5px;color:#7c8b9e;margin-top:5px}
.pill{display:inline-flex;align-items:center;gap:6px;background:#fff;border:1px solid #e2e8f2;
      border-radius:999px;padding:6px 13px;font-size:12.5px;color:#4a5a70;
      box-shadow:0 1px 2px rgba(16,24,40,.04)}
.dot{width:7px;height:7px;border-radius:50%;background:#2e8b57}
.dot.demo{background:#c88a2b}
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:16px}
.kpi{background:#fff;border:1px solid #e6ecf5;border-radius:14px;padding:15px 17px;
     box-shadow:0 1px 3px rgba(16,24,40,.05)}
.kpi .lab{font-size:12.5px;color:#7c8b9e;margin-bottom:8px}
.kpi .val{font-size:27px;font-weight:700;line-height:1}
.kpi .val small{font-size:13px;font-weight:600;color:#7c8b9e;margin-left:3px}
.kpi .note{font-size:11.5px;color:#93a1b5;margin-top:7px}
.grid{display:grid;grid-template-columns:1fr 330px;gap:14px;align-items:start}
.card{background:#fff;border:1px solid #e6ecf5;border-radius:14px;
      box-shadow:0 1px 3px rgba(16,24,40,.05);overflow:hidden}
.card h3{font-size:13.5px;font-weight:600;padding:13px 17px;border-bottom:1px solid #eef2f8;
         color:#31435c;display:flex;justify-content:space-between;align-items:center}
.card h3 em{font-style:normal;font-size:11.5px;color:#93a1b5;font-weight:400}
table{width:100%;border-collapse:collapse;font-size:12.5px}
th{text-align:left;padding:9px 12px;color:#7c8b9e;font-weight:500;background:#fafbfd;
   border-bottom:1px solid #eef2f8;font-size:11.5px;white-space:nowrap}
td{padding:9px 12px;border-bottom:1px solid #f2f5fa;white-space:nowrap}
tr:last-child td{border-bottom:none}
tr.deny td{background:#fef7f6}
tr.lock td{background:#fff6f4;box-shadow:inset 3px 0 0 #c0392b}
.tag{display:inline-block;padding:2px 9px;border-radius:999px;font-size:11.5px;font-weight:600}
.tag.pass{background:#e9f5ec;color:#2e8b57}
.tag.deny{background:#fdecea;color:#c0392b}
.tag.lock{background:#f7e5e2;color:#8e2f26}
.mono{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:11.5px;color:#5a6b80}
.muted{color:#93a1b5}
.side{display:flex;flex-direction:column;gap:14px}
.bars{padding:16px 17px 18px}
.bar-row{display:flex;align-items:center;gap:9px;margin-bottom:9px;font-size:11.5px;color:#5a6b80}
.bar-row .name{width:52px;flex:none}
.bar-track{flex:1;height:9px;background:#eef2f8;border-radius:999px;overflow:hidden}
.bar-fill{height:100%;border-radius:999px}
.bar-row .num{width:22px;text-align:right;color:#93a1b5}
.foot{margin-top:16px;font-size:11.5px;color:#93a1b5;display:flex;justify-content:space-between}
a{color:#2f5d9e;text-decoration:none}
"""


def fmt_ts(ts):
    return ts.strftime("%m-%d %H:%M:%S")


def chart_bars(events):
    """最近 14 次耗时（SVG 柱状，无 JS 也可渲染）"""
    recent = events[-14:]
    if not recent:
        return '<div class="bars muted" style="font-size:12px">暂无数据</div>'
    w, h, gap = 286, 118, 6
    bw = (w - gap * (len(recent) - 1)) / len(recent)
    top = max([e["elapsed"] for e in recent] + [1000])
    rows = []
    for i, e in enumerate(recent):
        bh = max(3, (e["elapsed"] / top) * h)
        x = i * (bw + gap)
        color = {"pass": "#3f8f68", "deny": "#d0645a", "lock": "#8e2f26"}[e["result"]]
        rows.append(
            f'<rect x="{x:.1f}" y="{h - bh:.1f}" width="{bw:.1f}" height="{bh:.1f}" '
            f'rx="2.5" fill="{color}" opacity="{"1" if e["result"]=="pass" else ".92"}"/>'
        )
    return (f'<div class="bars"><svg width="{w}" height="{h+22}" viewBox="0 0 {w} {h+22}">'
            f'<line x1="0" y1="{h}" x2="{w}" y2="{h}" stroke="#e2e8f2"/>'
            + "".join(rows) +
            f'<text x="0" y="{h+16}" font-size="9.5" fill="#93a1b5">最近 14 次</text>'
            f'<text x="{w}" y="{h+16}" font-size="9.5" fill="#93a1b5" text-anchor="end">'
            f'最高 {top} ms</text></svg></div>')


def chart_stage(events):
    """失败阶段构成"""
    denies = [e for e in events if e["result"] == "deny"]
    buckets = [("一级 读卡", sum(1 for e in denies if e["stage"] == "F1"), "#d0645a"),
               ("二级 PIN", sum(1 for e in denies if e["stage"] == "F2"), "#c88a2b"),
               ("三级 指纹", sum(1 for e in denies if e["stage"] == "F3"), "#8e5ab5")]
    total = max(1, sum(b[1] for b in buckets))
    out = []
    for name, n, color in buckets:
        pct = n / total * 100
        out.append(
            f'<div class="bar-row"><span class="name">{name}</span>'
            f'<span class="bar-track"><span class="bar-fill" '
            f'style="width:{pct:.0f}%;background:{color}"></span></span>'
            f'<span class="num">{n}</span></div>')
    if not denies:
        out.append('<div class="muted" style="font-size:12px;padding:4px 0">暂无失败记录</div>')
    return f'<div class="bars">{"".join(out)}</div>'


def render_fragment():
    with LOCK:
        events = list(STATE["events"])
        source = STATE["source"]
        serial_state = STATE["serial"]
    s = stats(events)
    rows = []
    for e in reversed(events[-24:]):
        stage = "全流程" if e["result"] == "pass" else STAGES.get(e["stage"], e["stage"])
        reason = REASONS.get(e["reason"], e["reason"] or "—")
        cls = e["result"] if e["result"] in ("deny", "lock") else ""
        rows.append(
            f'<tr class="{cls}"><td class="mono">{fmt_ts(e["ts"])}</td>'
            f'<td>{e["user"]}</td><td class="mono">{e["uid"]}</td>'
            f'<td>{stage}</td>'
            f'<td><span class="tag {e["result"]}">{RESULT_TEXT[e["result"]]}</span></td>'
            f'<td class="mono">{e["elapsed"]} ms</td>'
            f'<td class="muted">{reason}</td></tr>')
    table = "".join(rows) or '<tr><td colspan="7" class="muted">等待数据…</td></tr>'

    kpis = [
        ("今日通行", s["pass"], "次", f"失败率 {s['rate']:.1f}%", "#2e8b57"),
        ("拒绝次数", s["deny"], "次", "含超时与因子不符", "#c0392b"),
        ("锁定触发", s["lock"], "次", "连续 3 次失败后", "#8e2f26"),
        ("平均认证耗时", s["avg"], "ms", "仅统计通过记录", "#2f5d9e"),
    ]
    kpi_html = "".join(
        f'<div class="kpi"><div class="lab">{lab}</div>'
        f'<div class="val" style="color:{color}">{val}<small>{unit}</small></div>'
        f'<div class="note">{note}</div></div>' for lab, val, unit, note, color in kpis)

    dot_cls = "demo" if "演示" in source else ""
    return f"""
<div class="top">
  <div>
    <div class="title">多重验证门禁系统 · <span>审计后台</span></div>
    <div class="sub">三因子级联认证 · 实时通行日志与异常检测</div>
  </div>
  <div class="pill"><span class="dot {dot_cls}"></span>{source} · {serial_state}</div>
</div>
<div class="kpis">{kpi_html}</div>
<div class="grid">
  <div class="card">
    <h3>最近通行记录 <em>共 {len(events)} 条 · 显示最新 24 条</em></h3>
    <table>
      <thead><tr><th>时间</th><th>用户</th><th>卡 UID</th><th>阶段</th>
      <th>结果</th><th>耗时</th><th>原因</th></tr></thead>
      <tbody>{table}</tbody>
    </table>
  </div>
  <div class="side">
    <div class="card"><h3>认证耗时 <em>ms</em></h3>{chart_bars(events)}</div>
    <div class="card"><h3>失败阶段构成 <em>次</em></h3>{chart_stage(events)}</div>
  </div>
</div>
<div class="foot"><span>数据来源：{source}　|　本地 CSV 同步写入 logs.csv</span>
<span>刷新于 {datetime.now().strftime('%H:%M:%S')}　<a href="/export">导出 CSV</a></span></div>
"""


def render_page():
    return f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<title>门禁审计后台</title><style>{CSS}</style>
<noscript><meta http-equiv="refresh" content="3"></noscript>
</head><body>
<div id="app">{render_fragment()}</div>
<script>
// 有 JS 时局部刷新（无 JS 时靠 meta refresh 兜底）
var app = document.getElementById('app');
setInterval(function () {{
  fetch('/api/fragment').then(function (r) {{ return r.text(); }}).then(function (t) {{
    if (t && t !== app.innerHTML) app.innerHTML = t;
  }}).catch(function () {{}});
}}, 1500);
</script>
</body></html>"""


# ---------------------------------------------------------------- HTTP
class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):  # 静音访问日志
        pass

    def _send(self, code, body, ctype="text/html; charset=utf-8"):
        data = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = urlparse(self.path).path
        if path in ("/", "/index.html"):
            self._send(200, render_page())
        elif path == "/api/fragment":
            self._send(200, render_fragment())
        elif path == "/api/state":
            import json
            with LOCK:
                events = [
                    {**e, "ts": e["ts"].isoformat(timespec="seconds")}
                    for e in STATE["events"]
                ]
            self._send(200, json.dumps({"events": events, "stats": stats(STATE["events"])},
                                       ensure_ascii=False),
                       "application/json; charset=utf-8")
        elif path == "/export":
            buf = io.StringIO()
            w = csv.writer(buf)
            w.writerow(["时间", "用户", "卡UID", "阶段", "结果", "原因", "耗时ms"])
            with LOCK:
                for e in STATE["events"]:
                    w.writerow([e["ts"].isoformat(timespec="seconds"), e["user"], e["uid"],
                                e["stage"], e["result"], e["reason"], e["elapsed"]])
            self._send(200, "\ufeff" + buf.getvalue(), "text/csv; charset=utf-8")
        else:
            self._send(404, "not found")


def save_csv(path="logs.csv"):
    with LOCK:
        events = list(STATE["events"])
    if not events:
        return
    with open(path, "w", newline="", encoding="utf-8-sig") as fp:
        w = csv.writer(fp)
        w.writerow(["时间", "用户", "卡UID", "阶段", "结果", "原因", "耗时ms"])
        for e in events:
            w.writerow([e["ts"].isoformat(timespec="seconds"), e["user"], e["uid"],
                        e["stage"], e["result"], e["reason"], e["elapsed"]])


def main():
    ap = argparse.ArgumentParser(description="门禁审计后台（本地版）")
    ap.add_argument("--demo", action="store_true", help="演示模式，自动生成数据")
    ap.add_argument("--port", default=None, help="串口设备，如 /dev/tty.usbserial-1420")
    ap.add_argument("--baud", type=int, default=115200)
    ap.add_argument("--http-port", type=int, default=8000)
    ap.add_argument("--snapshot", default=None, help="导出静态 HTML 快照后退出")
    args = ap.parse_args()

    if args.snapshot:
        if args.demo or not args.port:
            rnd = random.Random(7)
            base = datetime.now() - timedelta(minutes=26)
            uid_of = {"U01": "A1B2C3D4", "U02": "5E6F7A8B",
                      "U03": "C3D4E5F6", "U04": "9A8B7C6D"}
            for i in range(26):
                t = base + timedelta(minutes=i, seconds=rnd.randint(0, 50))
                r = rnd.random()
                if r < 0.62:
                    u = rnd.choice(["U01", "U02", "U03"])
                    add_event(t, u, uid_of[u], "F3", "pass", "", rnd.randint(2100, 4300))
                elif r < 0.76:
                    add_event(t, "U02", "5E6F7A8B", "F2", "deny", "pin_wrong", rnd.randint(1100, 2700))
                elif r < 0.86:
                    add_event(t, "U03", "C3D4E5F6", "F3", "deny", "finger_mismatch", rnd.randint(2300, 4200))
                elif r < 0.93:
                    add_event(t, "U04", "9A8B7C6D", "F1", "deny", "card_unknown", rnd.randint(70, 180))
                elif r < 0.98:
                    add_event(t, "U01", "A1B2C3D4", "F2", "deny", "window_timeout", 10000)
                else:
                    add_event(t, "U02", "5E6F7A8B", "—", "lock", "locked", 0)
            STATE["source"] = "演示数据"
            STATE["serial"] = "已就绪"
        with open(args.snapshot, "w", encoding="utf-8") as fp:
            fp.write(render_page())
        print(f"[✓] 快照已写入 {args.snapshot}")
        return

    if args.demo:
        STATE["source"] = "演示数据"
        STATE["serial"] = "模拟中"
        threading.Thread(target=demo_worker, daemon=True).start()
        print("[i] 演示模式：每 2–3 秒生成一条记录")
    elif args.port:
        threading.Thread(target=serial_worker, args=(args.port, args.baud), daemon=True).start()
    else:
        print("[!] 未指定 --demo 或 --port，页面将为空。示例：python3 app.py --demo")

    def autosave():
        while True:
            time.sleep(10)
            try:
                save_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs.csv"))
            except OSError:
                pass

    threading.Thread(target=autosave, daemon=True).start()

    url = f"http://127.0.0.1:{args.http_port}"
    print(f"[✓] 后台已启动：{url}   （Ctrl+C 退出）")
    ThreadingHTTPServer(("127.0.0.1", args.http_port), Handler).serve_forever()


if __name__ == "__main__":
    main()
