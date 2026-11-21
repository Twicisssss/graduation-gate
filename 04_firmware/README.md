# 固件目录说明（STM32F103C8T6）

## 规划结构

```
04_firmware/
├── BSP/                  # 板级驱动：直接操作寄存器/HAL，不含业务逻辑
│   ├── Inc/
│   │   ├── bsp_rc522.h       读卡：寻卡 / 防冲突 / 读写块
│   │   ├── bsp_as608.h       指纹：握手 / 录入 / 搜索 / 删除
│   │   ├── bsp_key.h         4×4 键盘扫描与事件
│   │   ├── bsp_oled.h        OLED 显示
│   │   ├── bsp_lock.h        电磁锁时序
│   │   ├── bsp_flash.h       内部 Flash 模拟 EEPROM
│   │   ├── bsp_rtc.h         DS1302
│   │   └── bsp_uart.h        串口收发 / 日志帧 / printf 重定向
│   └── Src/
├── Services/             # 业务服务：可复用、可单测
│   ├── auth_fsm.c/.h         三因子级联状态机（核心）
│   ├── user_mgr.c/.h         用户与权限
│   └── log_ring.c/.h         日志环形缓冲
├── App/                  # 应用层
│   ├── app_main.c            1 ms 节拍调度
│   ├── ui_menu.c             管理员菜单
│   └── main.c
└── releases/             # 打好的 hex/bin，按版本归档
```

CubeMX 生成的 `Core/`、`Drivers/` 后续加入，**不要手改生成文件**，改动写在 `BSP/` 与 `Services/`。

## 编码约定

1. **主循环不阻塞**：禁止 `HAL_Delay()` 出现在 `App/`，统一用 1 ms 节拍 + 状态机。
2. **驱动不打印**：BSP 层通过返回值报错，日志由上层决定是否输出。
3. **命名**：`模块_动作()`，如 `RC522_ReadUID()`、`AS608_Search()`；静态函数加 `static`。
4. **魔数**：窗口时长、锁定次数、开锁时长统一放 `config.h`，方便做参数实验。
5. **每个驱动配一个自测函数**（`BSP_XXX_SelfTest()`），调试期先用它验证硬件。

## 关键参数（待整定）

| 参数 | 初值 | 说明 |
| --- | --- | --- |
| `AUTH_WINDOW_MS` | 10000 | 三因子时间窗，做 5/10/15 s 对比实验 |
| `LOCKOUT_THRESHOLD` | 3 | 连续失败触发锁定的次数 |
| `LOCKOUT_MS` | 180000 | 锁定 60–300 s，取中值 |
| `UNLOCK_MS` | 3000 | 开锁保持时间 |
| `MAX_USERS` | 20 | 用户表容量 |

## 串口日志协议（与 PC 后台的契约，先定死再写代码）

- 物理层：USART1（PA9/PA10）→ CH340 → USB，**115200 8N1**
- 帧格式：一行一条，字段用英文逗号分隔，`\r\n` 结尾，字段内不得出现逗号

```
时间,用户,卡UID,阶段,结果,原因,耗时ms
```

| 字段 | 取值 | 说明 |
| --- | --- | --- |
| 时间 | `YYYY-MM-DDThh:mm:ss` | DS1302 提供，PC 可下发校时 |
| 用户 | `U01`…`U20` / `-` | 未识别用户填 `-` |
| 卡UID | 8 位十六进制 / `-` | 大写，无空格 |
| 阶段 | `F1` `F2` `F3` `-` | 一级读卡 / 二级 PIN / 三级指纹 |
| 结果 | `pass` `deny` `lock` | lock 表示本次触发锁定 |
| 原因 | 见下表 / 空 | pass 时留空 |
| 耗时 | 整数毫秒 | 从刷卡到出结果 |

原因枚举：`card_unknown`、`card_disabled`、`pin_wrong`、`finger_mismatch`、`window_timeout`、`factor_mismatch`、`locked`

示例：

```
2027-04-02T10:12:33,U01,A1B2C3D4,F3,pass,,2860
2027-04-02T10:13:02,U03,C3D4E5F6,F2,deny,pin_wrong,1689
2027-04-02T10:13:40,U02,5E6F7A8B,F1,deny,card_unknown,116
2027-04-02T10:14:05,U02,5E6F7A8B,-,lock,locked,0
```

**约定**：只有一条记录完整产生后整行输出，不跨行拼接；串口发送用非阻塞，主循环不得等待 `.hex` 发送完成。

## 开发环境

- 编译：Windows + Keil MDK 5（CubeMX 生成工程后打开 `MDK-ARM/*.uvprojx`）。
- 烧录：ST-Link V2；调试口只保留 SWD（`SWDIO` PA13 / `SWCLK` PA14）。
- 串口：CH340 在 Windows 上系统自带驱动，设备管理器里是 `COM3`/`COM4` 之类；Mac 上若认不到，装一次 WCH 驱动即可。

## 编译

Keil MDK 5 打开 `MDK-ARM/*.uvprojx`（CubeMX 生成后）。产物 `*.hex` / `*.bin` 放 `releases/`，命名 `gate-v1.0-20270301.hex`。

```bat
:: Windows 下打开发布目录
explorer 04_firmware\releases
```

> 注意：Keil 工程路径与文件名请保持 ASCII（当前目录结构已满足），中文路径会导致部分版本编译异常。
