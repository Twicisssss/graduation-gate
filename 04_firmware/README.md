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
│   │   └── bsp_esp.h         ESP-01S AT 指令
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

## 编译

Keil MDK 5 打开 `MDK-ARM/*.uvprojx`（CubeMX 生成后）。命令行编译（有 ARM GCC 时）：

```bash
make -C 04_firmware -j
```

产物 `*.hex` / `*.bin` 放 `releases/`，命名 `gate-v1.0-20270301.hex`。
