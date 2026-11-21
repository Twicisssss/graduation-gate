# -*- coding: utf-8 -*-
"""把《任务书》模板填空成黄成意（2303290208）的正式稿。

用法：python3 fill_taskbook.py
输入：_tpl.docx（由 office_convert 从 .doc 模板转换而来）
输出：任务书-黄成意-2303290208.docx
"""
from docx import Document
from docx.shared import Pt

SRC = "_tpl.docx"
DST = "任务书-黄成意-2303290208.docx"

# ---------- 正文内容 ----------
INTRO = (
    "本课题以工程教育专业认证为核心导向，聚焦电子、电气类专业人才培养的“知识、能力、品格”"
    "三维目标，以复杂工程问题解决能力训练为目标，培养学生综合运用通信工程专业知识、技能和方法。"
    "要求学生能够综合运用专业知识和现代工具（如 Keil MDK、STM32CubeMX、Altium Designer/立创EDA、"
    "Python 等），完成多重验证门禁系统的方案论证、硬件设计、软件实现与性能测试，掌握从理论到"
    "实验验证的完整设计流程，提升在嵌入式系统与身份认证安全领域的综合设计与工程实践能力。"
    "具体训练内容如下："
)

KNOWLEDGE = [
    "(1)掌握通信工程专业核心知识: 深入学习射频识别（RFID）的近场耦合与防冲突机制、指纹特征提取与"
    "模板比对原理、密码哈希存储以及多因子认证模型的工作原理，理解多因子认证在智能门禁与楼宇安防"
    "领域的优势和应用前景。",
    "(2)理解器件特性及应用: 掌握 MFRC522 读卡芯片、AS608 指纹模块、SSD1306 显示屏、DS1302 时钟芯片"
    "等器件的特性参数与接口时序，并能够将其应用于门禁终端的分层电路设计中。",
    "(3)熟悉现代工具: 掌握 Keil MDK、STM32CubeMX、逻辑分析仪与示波器的使用方法，能够利用其搭建"
    "嵌入式固件工程，并进行系统设计、在线调试和参数优化。",
    "(4)拓展的行业新技术知识: 掌握基于时间窗约束的级联认证、补偿性多因子架构、异常尝试行为检测等"
    "基本分析方法，理解多因子认证在智能门禁系统中的应用和运行特性。",
]

ABILITY = [
    "(1)复杂工程问题分析能力：能够运用分层信任模型与有限状态机方法对“多个因子如何按序串联、"
    "失败与超时如何处置”这类复杂工程问题进行分析、建模与求解，并利用典型测试用例进行有效验证和优化。",
    "(2)工程设计与实践能力: 能够根据门禁系统的需求，利用 STM32 平台搭建包含读卡、键盘、指纹、显示、"
    "执行与串口通信的完整原型，包括硬件电路、固件状态机和人机交互界面，并进行性能测试分析、"
    "条件（参数）调控和优化。",
    "(3)数据分析与处理能力: 能够对认证耗时、误识率、锁定有效性等系统测试结果进行分析和处理，"
    "得出科学结论，并能够利用 Python 工具进行数据处理和可视化。",
    "(4)文献检索与阅读能力: 能够查阅相关文献资料，了解多因子身份认证技术的研究现状和发展趋势，"
    "并能够规范撰写逻辑清晰、论证充分的文献综述与技术文档的能力。",
]

CHARACTER = [
    None,  # (1) 团队合作精神：沿用模板
    "(2)工程伦理意识: 在进行门禁系统设计和实施时，需要考虑系统的安全性、通行隐私与消防疏散要求"
    "（如生物特征本地存储、密码哈希保存、断电开锁），主动承担工程活动对社会的责任。",
    None,  # (3) 创新性思维：沿用模板
]

TASKS = {
    37: "(1)查阅相关文献资料，了解多因子身份认证与智能门禁的研究现状和发展趋势，撰写文献综述。",
    38: "(2)毕业课题的系统设计方案的选择和论证：对比单因子、双因子与三因子方案的优缺点，论证"
        "“RFID 卡 + PIN 密码 + 指纹”级联验证的合理性，确定主控、器件选型与通信方案。",
    39: "(3)系统总体设计、硬件设计及制作、软件设计；系统建模、仿真：完成硬件原理图与 PCB 设计"
        "（或模块化搭接）、门禁终端固件（三因子级联状态机、10 s 认证窗口、失败计数与锁定、日志存储）、"
        "PC 端审计后台（日志展示、异常高亮、CSV 导出），并对认证流程进行状态机建模。",
    40: "(4)性能测试，对数据结果或仿真结果进行分析和处理，得出科学结论，并撰写毕业设计论文："
        "完成正常通行、单因子失效、复制卡攻击、暴力试错、窗口超时等测试用例，量化平均认证耗时、"
        "误识率与锁定有效性。",
    41: "(5) 总结分析论文的优势和不足，并提出改进的思路和展望：如指纹活体检测、安全芯片与国密算法、"
        "与校园一卡通系统对接等。",
    43: "(1) 查阅参考近五年与本课题相关的文献不少于 15 篇，其中外文文献不少于 3 篇，并完成文献综述。",
    44: "(2) 确定系统设计方案，同时考虑健康、安全、环境、法律以及经济和社会可持续发展的影响："
        "采用断电开锁方式满足消防疏散要求；生物特征与密码本地存储、不上传网络，符合个人信息保护的"
        "最小必要原则；整机物料成本控制在 300 元以内，并理解应承担的责任。",
    45: "(3) 系统设计、模块设计的功能是全面且正确，方案合理且可行，结论科学有效：三因子必须按序验证"
        "且不可跳过，超时与失败可判定、可追溯。",
}

PARAMS = [
    "(1) 认证因子与指标：RFID（Mifare 1K，13.56 MHz）为持有物因子，4~6 位数字 PIN 为知识因子，"
    "指纹（AS608，模板容量不小于 100 枚）为生物特征因子；",
    "(2) 时序参数：认证窗口 T 可配置（5~15 s，默认 10 s），连续失败 3 次锁定 60~300 s，开锁保持 3 s；",
    "(3) 性能指标：平均认证耗时不超过 5 s；日志存储不少于 60 条且掉电不丢失；整机由 12 V/2 A 适配器"
    "供电，待机功耗不超过 2 W。",
]

REFS = [
    "GB/T 35273-2020, 信息安全技术 个人信息安全规范[S]. 北京: 中国标准出版社, 2020.",
    "GB/T 22239-2019, 信息安全技术 网络安全等级保护基本要求[S]. 北京: 中国标准出版社, 2019.",
    "GB/T 40660-2021, 信息安全技术 生物特征识别信息保护基本要求[S]. 北京: 中国标准出版社, 2021.",
    "王永虹, 徐炜, 郝立平. STM32 系列 ARM Cortex-M3 微控制器原理与实践[M]. 北京: 北京航空航天大学出版社, 2008.",
    "NXP Semiconductors. MFRC522 Standard Performance MIFARE and NTAG Frontend: Product Data Sheet[Z]. 2016.",
]

SCHEDULE = [
    ("2026.12.1-2027.1.1", "查阅文献资料，了解课题应用领域、工作原理及系统组成。"),
    ("2027.1.1-2027.1.31", "学习 Keil MDK、CubeMX、立创EDA 等工具的使用，了解系统设计的结构及工作原理。"),
    ("2027.2.1-2027.2.28", "设计方案的选择和论证，完成开题报告。"),
    ("2027.3.1-2027.3.31", "系统设计、硬件设计和制作（原理图、PCB、结构件）。"),
    ("2027.4.1-2027.4.15", "软件设计、系统调试（三因子状态机、串口后台联调）。"),
    ("2027.4.16-2027.4.30", "性能测试和参数优化（时间窗整定、攻防测试）。"),
    ("2027.5.1-2027.5.10", "撰写毕业设计论文。"),
    ("2027.5.10-2027.5.20", "完成毕业论文修改及其他所需工作，准备答辩。"),
]


def set_text(p, text):
    """保留首个 run 的格式，整段替换文字。"""
    if not p.runs:
        p.add_run(text)
        return
    p.runs[0].text = text
    for r in p.runs[1:]:
        r.text = ""


def append_to_cell(cell, text):
    """在单元格已有文字（含空格）后追加内容，保留字体。"""
    p = cell.paragraphs[0]
    if p.runs:
        p.runs[-1].text = p.runs[-1].text.rstrip() + text
    else:
        p.add_run(text)


def main():
    d = Document(SRC)
    ps = d.paragraphs

    # ---- 封面 ----
    ps[6].runs[1].text = "课题名称：多重验证门禁系统研究与设计"
    for r in ps[6].runs[2:]:
        r.text = ""
    ps[9].runs[1].text = "完成期限：2026年12月1日至 2027年5月20日"
    for r in ps[9].runs[2:]:
        r.text = ""

    t0 = d.tables[0]
    append_to_cell(t0.rows[0].cells[1], "通信12302")
    append_to_cell(t0.rows[1].cells[0], "黄成意")
    append_to_cell(t0.rows[1].cells[1], "2303290208")
    append_to_cell(t0.rows[2].cells[0], "刘文琮")

    # ---- 一、课题训练内容 ----
    set_text(ps[19], INTRO)
    for i, txt in zip((21, 22, 23, 24), KNOWLEDGE):
        set_text(ps[i], txt)
    for i, txt in zip((26, 27, 28, 29), ABILITY):
        set_text(ps[i], txt)
    for i, txt in zip((31, 32, 33), CHARACTER):
        if txt:
            set_text(ps[i], txt)

    # ---- 二、任务和要求 ----
    # P35 自带自动编号（渲染为“二、”），因此不要再写前缀
    set_text(ps[35], "设计（论文）任务和要求")
    for i, txt in TASKS.items():
        set_text(ps[i], txt)

    # ---- 三、参数与参考资料 ----
    for i, txt in zip((50, 51, 52), PARAMS):
        set_text(ps[i], txt)
    ref_paras = list(range(54, 64))  # 10 个「列出段落」
    for k, txt in enumerate(REFS):
        set_text(ps[ref_paras[k]], txt)

    # ---- 四、进度表 ----
    t1 = d.tables[1]
    for idx, (date, content) in enumerate(SCHEDULE, start=1):
        row = t1.rows[idx]
        row.cells[1].paragraphs[0].runs[0].text = date
        for r in row.cells[1].paragraphs[0].runs[1:]:
            r.text = ""
        set_text(row.cells[2].paragraphs[0], content)

    # 进度表另起一页，避免表头与表体分离
    for para in d.paragraphs:
        if para.text.strip().startswith("四、毕业设计"):
            para.paragraph_format.page_break_before = True

    # ---- 收尾：删掉多余的书目空行与表格空行，表格禁止跨页断行 ----
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement

    for p in list(d.paragraphs[59:64]):
        p._p.getparent().remove(p._p)

    for row in list(t1.rows[9:11]):
        row._tr.getparent().remove(row._tr)

    for row in t1.rows:
        for cell in row.cells:
            for para in cell.paragraphs:
                # 关闭“对齐到网格”，否则单倍行距也会被文档网格撑大
                pPr = para._p.get_or_add_pPr()
                if pPr.find(qn("w:snapToGrid")) is None:
                    el = OxmlElement("w:snapToGrid")
                    el.set(qn("w:val"), "0")
                    rpr = pPr.find(qn("w:rPr"))
                    if rpr is not None:
                        rpr.addprevious(el)
                    else:
                        pPr.append(el)
                para.paragraph_format.line_spacing = 1.0
                para.paragraph_format.space_before = Pt(0)
                para.paragraph_format.space_after = Pt(0)
        trPr = row._tr.get_or_add_trPr()
        h = trPr.find(qn("w:trHeight"))
        if h is not None and row is not t1.rows[0]:
            h.set(qn("w:val"), "900")
        if trPr.find(qn("w:cantSplit")) is None:
            trPr.append(OxmlElement("w:cantSplit"))

    # 表下的两条注：单倍行距，确保与表格同页
    for para in d.paragraphs:
        t = para.text.strip()
        if t.startswith("注：") or t.startswith("2.\u201c"):
            para.paragraph_format.line_spacing = 1.0
            para.paragraph_format.space_before = Pt(0)
            para.paragraph_format.space_after = Pt(0)

    d.save(DST)
    print("saved", DST)


if __name__ == "__main__":
    main()
