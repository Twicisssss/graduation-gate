# 上位机 / Web 后台（05_web）

技术栈：React 18 + TypeScript + Vite + Supabase（与已上线的 `wtu-debate.top` 同一套工程经验）。

## 计划功能

| 页面 | 内容 |
| --- | --- |
| 登录 | 管理员账号（密码哈希校验，**不提供"查看明文"**） |
| 用户管理 | 用户列表、角色、绑定卡 UID / 指纹 ID，禁用/启用 |
| 通行日志 | 时间、用户、因子序列、结果、耗时、失败原因；异常行高亮 |
| 统计看板 | 今日通行数、失败数、锁定次数、因子耗时分布 |
| 导出 | 按日期/用户导出 CSV，供论文附录 |

## 数据表草案

```sql
users(id, name, card_uid, finger_id, pin_hash, role, enabled, created_at)
access_logs(id, user_id, card_uid, stage, result, elapsed_ms, reason, created_at)
devices(id, name, token, last_seen_at)
```

## 与固件约定

设备侧 `POST /api/logs`，Body：

```json
{ "device": "gate-01", "card_uid": "A1B2C3D4", "user": "U01",
  "stage": "F3", "result": "deny", "reason": "finger_mismatch",
  "elapsed_ms": 2860, "ts": "2027-04-02T10:12:33+08:00" }
```

固件断网时写入本地环形缓冲，联网后按条补传，保证"本地条数 = 后台条数"。
