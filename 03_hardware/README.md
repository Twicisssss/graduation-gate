# 硬件资料（03_hardware）

| 子目录 | 放什么 |
| --- | --- |
| `01_schematic/` | 原理图源工程（立创 EDA `.epro` / AD `.SchDoc`）＋ **PDF 导出**（答辩与论文用 PDF） |
| `02_pcb/` | PCB 源工程 ＋ 3D 预览图 ＋ 打板 Gerber（打包成 zip 放这里） |
| `03_bom/` | 采购清单（xlsx）、下单截图、到货记录 |
| `04_datasheets/` | 器件手册 PDF：STM32F103C8T6、RC522(MFRC522)、AS608、SSD1306、DS1302、SRD-05VDC 继电器 |

## 约定

1. **源工程与导出件都要存**：老师要 PDF 看，你自己要源文件改。
2. 打板前把 Gerber 打包 `gate-pcb-v1.0-20270210.zip` 放 `02_pcb/`，方便重打。
3. 手册按型号命名：`MFRC522-datasheet.pdf`、`AS608-手册.pdf`。

## 供电要点（易翻车）

- 12 V 电磁锁独立供电，继电器隔离；锁线圈两端反并 1N4007 续流。
- 5 V 给继电器 / 键盘 / OLED，3.3 V 给主控 / RC522 / DS1302，**单点共地**。
- RC522 只能 3.3 V 供电，5 V 会烧。
