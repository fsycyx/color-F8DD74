from __future__ import annotations

from pathlib import Path

from reportlab.graphics.shapes import Drawing, Line, Polygon, Rect, String
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    HRFlowable,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf" / "餐衡FoodLens项目白盒测试与技术报告.pdf"
TEST_REPORT = ROOT / "WHITEBOX_TEST_REPORT.md"
FONT_PATH = Path(r"C:\Windows\Fonts\simhei.ttf")

PAGE_W, PAGE_H = A4
MARGIN_X = 19 * mm
TOP = 18 * mm
BOTTOM = 17 * mm

INK = HexColor("#182720")
GREEN = HexColor("#247A52")
GREEN_DARK = HexColor("#18583B")
GREEN_SOFT = HexColor("#E8F2EC")
BLUE = HexColor("#2F6CA4")
BLUE_SOFT = HexColor("#EAF2F8")
ORANGE = HexColor("#A45C2F")
ORANGE_SOFT = HexColor("#FAEFE6")
PURPLE = HexColor("#6755A6")
PURPLE_SOFT = HexColor("#F0EDF9")
MUTED = HexColor("#66726B")
LINE = HexColor("#D9E2DB")
PAPER = HexColor("#F7F9F7")
WHITE = colors.white
RED = HexColor("#A33F32")


def register_fonts() -> None:
    if not FONT_PATH.exists():
        raise FileNotFoundError(f"Chinese font not found: {FONT_PATH}")
    pdfmetrics.registerFont(TTFont("SimHei", str(FONT_PATH)))


register_fonts()


styles = getSampleStyleSheet()
BODY = ParagraphStyle(
    "BodyCN",
    parent=styles["BodyText"],
    fontName="SimHei",
    fontSize=9.1,
    leading=15,
    textColor=INK,
    spaceAfter=6,
    wordWrap="CJK",
)
SMALL = ParagraphStyle(
    "SmallCN",
    parent=BODY,
    fontSize=7.6,
    leading=11.5,
    textColor=MUTED,
    spaceAfter=3,
)
TINY = ParagraphStyle(
    "TinyCN",
    parent=SMALL,
    fontSize=6.7,
    leading=9.2,
)
H1 = ParagraphStyle(
    "H1CN",
    parent=BODY,
    fontSize=21,
    leading=29,
    textColor=GREEN_DARK,
    spaceBefore=1,
    spaceAfter=11,
)
H2 = ParagraphStyle(
    "H2CN",
    parent=BODY,
    fontSize=13.2,
    leading=19,
    textColor=GREEN_DARK,
    spaceBefore=7,
    spaceAfter=7,
)
H3 = ParagraphStyle(
    "H3CN",
    parent=BODY,
    fontSize=10.3,
    leading=15,
    textColor=INK,
    spaceBefore=5,
    spaceAfter=4,
)
KICKER = ParagraphStyle(
    "KickerCN",
    parent=SMALL,
    fontSize=7.2,
    leading=10,
    textColor=GREEN,
    spaceAfter=3,
)
CAPTION = ParagraphStyle(
    "CaptionCN",
    parent=SMALL,
    alignment=TA_CENTER,
    fontSize=7.1,
    leading=10,
    textColor=MUTED,
    spaceBefore=3,
)
TABLE_HEAD = ParagraphStyle(
    "TableHeadCN",
    parent=SMALL,
    fontSize=7.4,
    leading=10.5,
    textColor=WHITE,
    alignment=TA_LEFT,
)
TABLE_CELL = ParagraphStyle(
    "TableCellCN",
    parent=SMALL,
    fontSize=7.2,
    leading=10.5,
    textColor=INK,
)
CALLOUT = ParagraphStyle(
    "CalloutCN",
    parent=BODY,
    fontSize=8.7,
    leading=14,
    textColor=GREEN_DARK,
)


def p(text: str, style: ParagraphStyle = BODY) -> Paragraph:
    return Paragraph(text, style)


def bullet(text: str, style: ParagraphStyle = BODY) -> Paragraph:
    return Paragraph(f"<font color='#247A52'>●</font> {text}", style)


def number(text: str, n: int) -> Paragraph:
    return Paragraph(f"<font color='#247A52'><b>{n:02d}</b></font>　{text}", BODY)


def callout(title: str, text: str, color: colors.Color = GREEN_SOFT) -> Table:
    data = [[p(f"<b>{title}</b>", CALLOUT)], [p(text, SMALL)]]
    table = Table(data, colWidths=[PAGE_W - 2 * MARGIN_X], hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), color),
                ("BOX", (0, 0), (-1, -1), 0.6, LINE),
                ("LEFTPADDING", (0, 0), (-1, -1), 9),
                ("RIGHTPADDING", (0, 0), (-1, -1), 9),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    return table


def table(data: list[list[str]], widths: list[float], header: bool = True, font_size: float = 7.2) -> Table:
    rows = []
    for r_idx, row in enumerate(data):
        row_style = TABLE_HEAD if header and r_idx == 0 else TABLE_CELL
        if font_size != row_style.fontSize:
            row_style = ParagraphStyle(
                f"cell-{font_size}-{r_idx}",
                parent=row_style,
                fontSize=font_size,
                leading=font_size + 3,
            )
        rows.append([p(cell, row_style) for cell in row])
    t = Table(rows, colWidths=widths, repeatRows=1 if header else 0, hAlign="LEFT")
    style_cmds = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.45, LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("BACKGROUND", (0, 1 if header else 0), (-1, -1), WHITE),
    ]
    if header:
        style_cmds.append(("BACKGROUND", (0, 0), (-1, 0), GREEN_DARK))
    for row in range(1 if header else 0, len(rows)):
        if row % 2 == 0:
            style_cmds.append(("BACKGROUND", (0, row), (-1, row), PAPER))
    t.setStyle(TableStyle(style_cmds))
    return t


def two_cards(left_title: str, left_body: str, right_title: str, right_body: str) -> Table:
    w = (PAGE_W - 2 * MARGIN_X - 7 * mm) / 2
    data = [[
        [p(f"<b>{left_title}</b>", H3), p(left_body, SMALL)],
        [p(f"<b>{right_title}</b>", H3), p(right_body, SMALL)],
    ]]
    t = Table(data, colWidths=[w, w], hAlign="LEFT")
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, 0), GREEN_SOFT),
                ("BACKGROUND", (1, 0), (1, 0), BLUE_SOFT),
                ("BOX", (0, 0), (-1, -1), 0.5, LINE),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, WHITE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    return t


def section_start(number_text: str, title: str, subtitle: str) -> list:
    return [p(number_text, KICKER), p(title, H1), p(subtitle, BODY), HRFlowable(width="100%", thickness=0.7, color=LINE, spaceBefore=2, spaceAfter=8)]


def architecture_diagram() -> Drawing:
    d = Drawing(490, 285)
    d.add(Rect(0, 0, 490, 285, fillColor=WHITE, strokeColor=LINE, strokeWidth=0.7, rx=6, ry=6))
    d.add(String(18, 258, "当前原型架构", fontName="SimHei", fontSize=10, fillColor=GREEN_DARK))
    layers = [
        (215, GREEN_SOFT, GREEN_DARK, "交互层：6 个 Vue 业务视图 + 通用组件"),
        (156, BLUE_SOFT, BLUE, "应用层：Vue Router + Pinia 状态 + TypeScript 契约"),
        (97, PURPLE_SOFT, PURPLE, "AI 适配层：recognizeMenu / buildPlans / askHealthAssistant"),
        (38, ORANGE_SOFT, ORANGE, "数据层：localStorage + 本地演示知识与营养估算"),
    ]
    for y, fill, stroke, label in layers:
        d.add(Rect(36, y, 418, 38, fillColor=fill, strokeColor=stroke, strokeWidth=1, rx=4, ry=4))
        d.add(String(55, y + 14, label, fontName="SimHei", fontSize=8.5, fillColor=INK))
    for y in [207, 148, 89]:
        d.add(Line(245, y, 245, y - 10, strokeColor=MUTED, strokeWidth=1.2))
        d.add(Polygon([241, y - 7, 249, y - 7, 245, y - 12], fillColor=MUTED, strokeColor=MUTED))
    return d


def target_architecture_diagram() -> Drawing:
    d = Drawing(490, 310)
    d.add(Rect(0, 0, 490, 310, fillColor=WHITE, strokeColor=LINE, strokeWidth=0.7, rx=6, ry=6))
    columns = [
        (18, 108, GREEN_SOFT, GREEN_DARK, "Web 前端", ["Vue 3", "Pinia", "ECharts", "SSE 客户端"]),
        (142, 130, BLUE_SOFT, BLUE, "应用服务", ["FastAPI", "鉴权与限流", "输入校验", "审计日志"]),
        (288, 184, PURPLE_SOFT, PURPLE, "AI 编排", ["OCR/视觉模型", "约束规划器", "RAG 检索", "安全规则引擎"]),
    ]
    for x, w, fill, stroke, title, items in columns:
        d.add(Rect(x, 78, w, 190, fillColor=fill, strokeColor=stroke, strokeWidth=1, rx=5, ry=5))
        d.add(String(x + 12, 243, title, fontName="SimHei", fontSize=9, fillColor=stroke))
        for i, item in enumerate(items):
            d.add(Rect(x + 10, 205 - i * 32, w - 20, 22, fillColor=WHITE, strokeColor=LINE, strokeWidth=0.45, rx=3, ry=3))
            d.add(String(x + 17, 212 - i * 32, item, fontName="SimHei", fontSize=7.2, fillColor=INK))
    d.add(String(18, 286, "建议生产架构", fontName="SimHei", fontSize=10, fillColor=GREEN_DARK))
    for x1, x2 in [(126, 142), (272, 288)]:
        d.add(Line(x1, 172, x2, 172, strokeColor=MUTED, strokeWidth=1.2))
        d.add(Polygon([x2 - 4, 168, x2 - 4, 176, x2, 172], fillColor=MUTED, strokeColor=MUTED))
    d.add(Rect(75, 22, 340, 34, fillColor=PAPER, strokeColor=LINE, strokeWidth=0.6, rx=4, ry=4))
    d.add(String(94, 35, "PostgreSQL + pgvector | 对象存储 | 指标、追踪与模型评测", fontName="SimHei", fontSize=7.4, fillColor=INK))
    for x in [196, 352]:
        d.add(Line(x, 78, x, 56, strokeColor=MUTED, strokeWidth=1))
        d.add(Polygon([x - 4, 60, x + 4, 60, x, 56], fillColor=MUTED, strokeColor=MUTED))
    return d


def ai_pipeline_diagram() -> Drawing:
    d = Drawing(490, 210)
    d.add(Rect(0, 0, 490, 210, fillColor=WHITE, strokeColor=LINE, strokeWidth=0.7, rx=6, ry=6))
    steps = [
        (12, GREEN_SOFT, GREEN_DARK, "1 输入", "菜单图片\n自然语言约束"),
        (108, BLUE_SOFT, BLUE, "2 感知", "OCR/视觉识别\n结构化菜品"),
        (204, PURPLE_SOFT, PURPLE, "3 校验", "置信度门槛\n用户人工校正"),
        (300, ORANGE_SOFT, ORANGE, "4 决策", "硬约束过滤\n多目标排序"),
        (396, GREEN_SOFT, GREEN_DARK, "5 执行", "解释与对比\n用户确认写入"),
    ]
    for x, fill, stroke, title, detail in steps:
        d.add(Rect(x, 72, 82, 96, fillColor=fill, strokeColor=stroke, strokeWidth=1, rx=5, ry=5))
        d.add(String(x + 10, 143, title, fontName="SimHei", fontSize=8.5, fillColor=stroke))
        for i, line in enumerate(detail.split("\n")):
            d.add(String(x + 10, 117 - i * 18, line, fontName="SimHei", fontSize=6.8, fillColor=INK))
        if x < 396:
            d.add(Line(x + 82, 120, x + 95, 120, strokeColor=MUTED, strokeWidth=1))
            d.add(Polygon([x + 91, 116, x + 91, 124, x + 95, 120], fillColor=MUTED, strokeColor=MUTED))
    d.add(String(12, 188, "AI 辅助决策闭环", fontName="SimHei", fontSize=10, fillColor=GREEN_DARK))
    d.add(Line(437, 72, 437, 42, strokeColor=MUTED, strokeWidth=1))
    d.add(Line(437, 42, 53, 42, strokeColor=MUTED, strokeWidth=1))
    d.add(Line(53, 42, 53, 70, strokeColor=MUTED, strokeWidth=1))
    d.add(Polygon([49, 66, 57, 66, 53, 72], fillColor=MUTED, strokeColor=MUTED))
    d.add(String(178, 24, "反馈：修改菜单、调整偏好、重新计算", fontName="SimHei", fontSize=7.2, fillColor=MUTED))
    return d


class NumberedCanvasMixin:
    pass


def header_footer(canvas, doc) -> None:
    page = canvas.getPageNumber()
    canvas.saveState()
    canvas.setFont("SimHei", 7)
    canvas.setFillColor(MUTED)
    if page > 1:
        canvas.drawString(MARGIN_X, PAGE_H - 11 * mm, "餐衡 FoodLens | 项目白盒测试与技术报告")
        canvas.setStrokeColor(LINE)
        canvas.setLineWidth(0.5)
        canvas.line(MARGIN_X, PAGE_H - 13 * mm, PAGE_W - MARGIN_X, PAGE_H - 13 * mm)
    canvas.setStrokeColor(LINE)
    canvas.line(MARGIN_X, 12 * mm, PAGE_W - MARGIN_X, 12 * mm)
    canvas.drawString(MARGIN_X, 7.5 * mm, "基于 2026-10-18 源码快照")
    canvas.drawRightString(PAGE_W - MARGIN_X, 7.5 * mm, f"{page:02d}")
    canvas.restoreState()


def cover_page(story: list) -> None:
    story.extend(
        [
            Spacer(1, 22 * mm),
            p("FOODLENS / TECHNICAL REPORT", KICKER),
            Spacer(1, 5 * mm),
            p("餐衡 FoodLens", ParagraphStyle("CoverTitle", parent=H1, fontSize=34, leading=42, textColor=GREEN_DARK)),
            p("项目白盒测试与技术报告", ParagraphStyle("CoverSub", parent=H2, fontSize=19, leading=27, textColor=INK)),
            Spacer(1, 9 * mm),
            HRFlowable(width="30%", thickness=3, color=GREEN, hAlign="LEFT"),
            Spacer(1, 11 * mm),
            p("面向日常饮食与生活方式记录的 AI 健康决策助手", ParagraphStyle("CoverLead", parent=BODY, fontSize=12.5, leading=21, textColor=MUTED)),
            Spacer(1, 16 * mm),
            table(
                [
                    ["文档属性", "内容"],
                    ["项目类型", "Vue 3 单页应用 / AI 健康决策原型"],
                    ["审查范围", "src 源码、构建配置、服务适配层、状态持久化与测试代码"],
                    ["技术栈", "Vue 3.5、TypeScript 5.9、Pinia 3、Vue Router 4、ECharts 6、Vite 7、Vitest 3"],
                    ["版本日期", "2026 年 10 月 18 日"],
                    ["文档状态", "最终版 / 含白盒测试证据"],
                ],
                [34 * mm, 117 * mm],
            ),
            Spacer(1, 18 * mm),
            callout(
                "结论摘要",
                "该原型已形成从菜单识别、人工校正、多方案比较到用户确认记录的完整决策链，并将健康问答限定在可引用的一般信息范围内。当前 AI 能力由本地模拟适配层实现，适合演示交互与验证产品假设；生产化仍需接入服务端模型、知识库、鉴权、上传安全和持续评测体系。",
                GREEN_SOFT,
            ),
            PageBreak(),
        ]
    )


def executive_summary(story: list) -> None:
    story.extend(section_start("EXECUTIVE SUMMARY", "执行摘要与文档导航", "本报告以源码和可重复测试结果为依据，区分已实现能力、演示数据和建议生产方案。"))
    story.extend(
        [
            two_cards(
                "当前可交付价值",
                "六个业务页面覆盖健康记录、智能点餐、趋势洞察、AI 问答与隐私设置；关键异步流程具备加载、失败和降级反馈；状态通过 Pinia 管理并在浏览器本地持久化。",
                "关键边界",
                "OCR、营养估算、方案规划和知识问答均为本地模拟数据，不构成真实医学或营养服务；前端未接入后端鉴权、服务端存储和模型供应商。",
            ),
            Spacer(1, 8 * mm),
            p("文档导航", H2),
            table(
                [
                    ["章节", "核心问题", "审查重点"],
                    ["01 项目概述", "项目解决什么问题？", "定位、范围、现状和角色"],
                    ["02 需求分析", "系统必须满足哪些业务与质量要求？", "功能、非功能、边界、验收"],
                    ["03 系统架构设计", "模块如何协作？如何生产化？", "分层、数据流、部署拓扑"],
                    ["04 AI 技术方案", "为什么这样选型，如何集成和优化？", "OCR、约束规划、RAG、安全与评测"],
                    ["05 核心功能实现", "代码如何落地用户流程？", "组件、状态、资源释放、异常处理"],
                    ["06 创新点", "项目的新意在哪里？", "技术创新与应用创新分列"],
                    ["07 测试与部署", "质量证据和上线方案是什么？", "白盒结果、风险、构建与发布"],
                    ["08 总结与展望", "下一阶段如何演进？", "里程碑、风险和长期方向"],
                ],
                [28 * mm, 54 * mm, 69 * mm],
            ),
            Spacer(1, 7 * mm),
            callout("证据口径", "报告中的“已实现”表示在当前源码中存在可执行逻辑；“演示”表示由固定数据与延迟模拟；“建议”表示尚未落地的生产化设计。三类内容在文中明确区分。", BLUE_SOFT),
            PageBreak(),
        ]
    )


def project_overview(story: list) -> None:
    story.extend(section_start("01 / PROJECT OVERVIEW", "项目概述", "餐衡聚焦高频、低门槛的日常健康决策，不做疾病诊断或治疗。"))
    story.extend(
        [
            p("1.1 项目背景与目标", H2),
            p("用户面对食堂菜单、外卖截图、包装食品标签和碎片化健康记录时，常见困难不是缺少信息，而是难以在预算、忌口、营养结构和当天状态之间快速权衡。餐衡将“识别-校正-比较-确认”设计为一条可回退的工作流，让用户保留最终决策权。"),
            p("1.2 目标用户与典型场景", H2),
            table(
                [
                    ["用户/场景", "主要痛点", "系统响应"],
                    ["校园或园区就餐者", "菜单变化快，缺少结构化信息", "上传图片，识别菜名与价格，提供三种取舍明确的组合"],
                    ["关注生活方式的普通成年人", "饮水、睡眠、活动记录分散", "聚合今日状态和七日趋势，给出可执行的小行动"],
                    ["包装食品消费者", "单位、份数和过敏原容易误读", "识别后要求用户核对单位与份数，并提示过敏边界"],
                    ["一般健康知识查询者", "难以判断答案依据是否可靠", "返回来源信息；证据不足时拒绝推断"],
                ],
                [35 * mm, 53 * mm, 63 * mm],
            ),
            p("1.3 项目范围", H2),
            two_cards(
                "范围内",
                "今日仪表盘；饮水/睡眠/活动/情绪记录；菜单与食品标签识别交互；点餐方案比较；七日趋势；带引用的一般健康问答；本地隐私控制。",
                "范围外",
                "医疗诊断与治疗；疾病风险预测；处方和用药建议；精准营养承诺；真实图像上传与模型推理；服务端账户与跨设备同步。",
            ),
            p("1.4 当前成熟度判断", H2),
            p("项目属于“可交互高保真原型 + 可替换 AI 服务契约”阶段。前端工程结构、状态管理、路由懒加载、异步反馈与资源清理已形成；AI 服务仍为 mock，测试重点因此集中在适配层契约、状态边界、用户确认和安全降级。"),
            PageBreak(),
        ]
    )


def requirements(story: list) -> None:
    story.extend(section_start("02 / REQUIREMENTS", "需求分析", "需求以“可解释、可校正、可撤回、不过度承诺”为核心原则。"))
    story.extend(
        [
            p("2.1 功能需求", H2),
            table(
                [
                    ["编号", "需求", "验收要点", "优先级"],
                    ["FR-01", "用户可记录饮水、睡眠、活动、情绪与饥饿感", "输入即时反映在今日状态；刷新后关键字段仍存在", "P0"],
                    ["FR-02", "用户可上传菜单并预览", "无图片时阻止识别；更换/离开页面释放对象 URL", "P0"],
                    ["FR-03", "识别结果可人工校正", "展示置信度；低置信项显著提示；菜名与价格可编辑", "P0"],
                    ["FR-04", "生成并比较候选餐食", "至少展示价格、能量范围、蛋白质、蔬菜量和理由", "P0"],
                    ["FR-05", "只有用户确认后写入记录", "模型或规划器不得自动执行有状态操作", "P0"],
                    ["FR-06", "一般健康问答附来源并安全拒答", "命中主题带引用；证据不足不做医学判断", "P0"],
                    ["FR-07", "趋势页展示已有记录的变化", "可切换指标；相关性文案不表达医学因果", "P1"],
                    ["FR-08", "用户可管理隐私和删除本地数据", "删除前二次确认；清理后回到空状态", "P1"],
                ],
                [14 * mm, 57 * mm, 63 * mm, 17 * mm],
                font_size=6.8,
            ),
            p("2.2 非功能需求", H2),
            table(
                [
                    ["维度", "要求", "当前实现/差距"],
                    ["性能", "首屏轻量、异步页面按需加载、图表不重复实例化", "除首页外路由懒加载；ECharts 单页包仍偏大"],
                    ["可靠性", "网络/模型错误有明确反馈，不能伪造成功", "关键 AI 调用均有 catch 与降级文案"],
                    ["隐私", "最小化收集，图片默认不上传，密钥不进入前端", "演示版仅本地预览；生产端仍需鉴权和上传治理"],
                    ["可维护性", "类型契约统一，页面与服务解耦", "types.ts 集中建模，mockApi.ts 暴露稳定签名"],
                    ["可访问性", "按钮有语义，上传/导航有标签，减少动画可适配", "已有 aria-label 和 prefers-reduced-motion；仍需系统化审计"],
                    ["安全性", "医学高风险主题拦截，过敏约束优先于模型", "当前以文案和有限 mock 逻辑体现，需后端规则引擎"],
                ],
                [23 * mm, 60 * mm, 68 * mm],
            ),
            PageBreak(),
        ]
    )


def requirements_boundary(story: list) -> None:
    story.extend(section_start("02 / REQUIREMENTS", "业务规则、数据规则与验收边界", "健康场景的关键不是“回答更多”，而是知道何时必须停止推断。"))
    story.extend(
        [
            p("2.3 核心业务规则", H2),
            number("识别置信度低于 0.8 的菜单项进入人工校正流程，不能直接参与最终营养计算。", 1),
            number("预算、过敏原、明确忌口属于硬约束；口味、多样性、饱腹感属于软偏好。", 2),
            number("营养数值以区间或近似值展示，并说明食材、份量与烹饪方式会造成误差。", 3),
            number("趋势洞察只描述用户主动记录中的关联，不把相关性写成因果或疾病风险。", 4),
            number("疾病、孕产期、未成年人、进食障碍、药物相互作用和急性症状触发安全转介。", 5),
            number("任何写入健康记录的动作都需要用户显式确认，支持修改后重新计算。", 6),
            p("2.4 数据分类与处理原则", H2),
            table(
                [
                    ["数据类别", "示例", "敏感性", "处理原则"],
                    ["偏好数据", "预算、口味、忌口", "中", "仅为筛选服务；允许随时修改和删除"],
                    ["生活方式记录", "饮水、睡眠、活动、情绪", "较高", "本地最小化存储；生产环境需加密、授权和留存策略"],
                    ["图像数据", "菜单、营养标签", "较高", "默认短时处理；去除 EXIF；限制格式/大小；完成后删除原图"],
                    ["AI 会话", "健康问题、引用与反馈", "较高", "脱敏日志；禁止用于无授权训练；可追溯来源与模型版本"],
                ],
                [26 * mm, 40 * mm, 22 * mm, 63 * mm],
            ),
            p("2.5 关键验收场景", H2),
            callout("主成功路径", "选择清晰菜单图片 -> 识别 5 个菜品 -> 用户校正低置信项 -> 输入“预算 25 元、不要辣” -> 得到三套可比较方案 -> 选择方案 -> 今日驾驶舱显示已选餐食。", GREEN_SOFT),
            Spacer(1, 4 * mm),
            callout("安全路径", "提问“请诊断我的疾病” -> 系统不生成诊断结论 -> 明确说明信息不足和能力边界 -> 建议在需要时咨询专业人员。", ORANGE_SOFT),
            PageBreak(),
        ]
    )


def architecture_current(story: list) -> None:
    story.extend(section_start("03 / ARCHITECTURE", "系统架构设计：当前实现", "采用单页应用分层，AI 能力通过服务适配层与视图解耦。"))
    story.extend(
        [
            architecture_diagram(),
            p("图 3-1 当前原型逻辑架构", CAPTION),
            p("3.1 模块职责", H2),
            table(
                [
                    ["模块", "关键文件", "职责"],
                    ["应用壳与导航", "App.vue / router.ts", "侧栏、移动导航、页面标题、六条路由与路由级懒加载"],
                    ["业务视图", "views/*.vue", "组织用户流程、交互状态、错误反馈和展示逻辑"],
                    ["共享状态", "stores/health.ts", "今日记录、已选餐食、通知设置、派生进度和本地持久化"],
                    ["AI 服务适配", "services/mockApi.ts", "菜单识别、方案规划、问答的异步契约与演示实现"],
                    ["领域模型", "types.ts", "MenuItem、MealPlan、HealthLog、DayPoint、Citation、ChatMessage"],
                    ["可视化", "InsightsView.vue + ECharts", "七日饮水、睡眠、活动趋势及资源销毁"],
                ],
                [31 * mm, 46 * mm, 74 * mm],
            ),
            p("3.2 关键设计判断", H2),
            bullet("服务函数以 Promise 返回稳定的结构化对象，真实后端可以在不改页面调用方式的前提下替换 mock。"),
            bullet("跨页数据进入 Pinia；临时上传预览、加载态和输入草稿保留在页面内部，避免全局状态膨胀。"),
            bullet("路由只同步加载首页，其余页面动态 import；图表只初始化一次，并在卸载时移除监听和销毁实例。"),
            PageBreak(),
        ]
    )


def architecture_target(story: list) -> None:
    story.extend(section_start("03 / ARCHITECTURE", "系统架构设计：生产化方案", "保持前端契约稳定，将高风险能力和密钥迁移到后端。"))
    story.extend(
        [
            target_architecture_diagram(),
            p("图 3-2 建议生产架构与责任边界", CAPTION),
            p("3.3 接口与数据流", H2),
            table(
                [
                    ["端点", "输入", "输出", "保护措施"],
                    ["POST /api/menu/analyze", "压缩后的菜单图像", "菜品、价格、置信度、候选框", "MIME/魔数校验、限流、短时对象存储、EXIF 清理"],
                    ["POST /api/meal/plans", "已确认菜品 + 预算/忌口 + 今日上下文", "候选方案、评分、理由、约束审计", "Pydantic 校验、硬约束引擎、幂等键"],
                    ["POST /api/assistant/chat", "问题 + 会话上下文", "SSE token、引用、风险分类", "内容策略、检索白名单、超时与熔断"],
                    ["GET /api/health/summary", "日期范围", "聚合趋势", "最小权限、字段级脱敏、审计日志"],
                ],
                [38 * mm, 47 * mm, 42 * mm, 42 * mm],
                font_size=6.6,
            ),
            p("3.4 部署拓扑原则", H2),
            bullet("静态前端通过 CDN 发布；API 置于反向代理和 WAF 后；AI 编排服务不直接暴露供应商密钥。"),
            bullet("结构化健康数据进入 PostgreSQL；向量只保存知识文档切片和引用元数据，不混入用户私密原文。"),
            bullet("对象存储使用短时签名 URL 和生命周期删除；日志默认脱敏，不记录原始图像与完整健康问答。"),
            bullet("每次响应记录 request_id、模型/提示词版本、检索文档版本和安全规则版本，以支持追溯。"),
            PageBreak(),
        ]
    )


def ai_selection(story: list) -> None:
    story.extend(section_start("04 / AI SOLUTION", "AI 技术方案：选型理由", "AI 不直接替代规则与数据库，而是承担感知、意图理解和语言解释。"))
    story.extend(
        [
            p("4.1 能力拆分与技术选择", H2),
            table(
                [
                    ["能力", "推荐技术", "选型理由", "不采用单一大模型的原因"],
                    ["菜单/标签识别", "OCR + 视觉语言模型的两阶段方案", "OCR 提供文字与位置，视觉模型补充版面、菜价配对和模糊语义", "单模型难以稳定保证数字、单位和表格对齐"],
                    ["餐食规划", "确定性约束引擎 + 加权多目标排序", "预算、过敏与忌口可严格验证；软偏好可解释评分", "纯生成式推荐可能遗漏硬约束或虚构营养值"],
                    ["健康问答", "RAG + 受限生成 + 引用校验", "知识来自白名单资料，可追踪到标题、机构和章节", "参数记忆无法保证时效、出处与医疗边界"],
                    ["趋势洞察", "规则/统计特征 + 模板化语言", "样本小、需要避免因果误判，确定性结果更易测试", "用模型直接“发现规律”容易过拟合和夸大结论"],
                    ["安全控制", "前置规则分类器 + 后置输出审查", "高风险主题必须在模型前后双重控制", "只依赖提示词无法形成可审计的硬边界"],
                ],
                [28 * mm, 38 * mm, 52 * mm, 51 * mm],
                font_size=6.5,
            ),
            p("4.2 模型与基础设施选择标准", H2),
            two_cards(
                "效果与风险指标",
                "OCR 字符/字段准确率；价格与菜名配对准确率；过敏原漏检率；约束满足率；引用正确率；医学越界率；拒答准确率；同一输入稳定性。",
                "工程与成本指标",
                "中文能力；结构化输出；视觉输入；流式响应；区域与隐私合规；单请求成本；P95 延迟；并发配额；版本稳定性；可观测性。",
            ),
            p("4.3 推荐组合", H2),
            p("原型阶段保留当前 mock 适配层以快速验证交互。试点阶段接入一个支持图像与 JSON Schema 的视觉模型，同时使用确定性规划器和可信资料 RAG。规模化阶段再做多供应商路由、缓存和小模型分流。该路径避免过早绑定单一模型，也保留对关键健康约束的工程控制。"),
            PageBreak(),
        ]
    )


def ai_integration(story: list) -> None:
    story.extend(section_start("04 / AI SOLUTION", "AI 技术方案：集成方式", "集成采用“模型提取、规则校验、用户确认”的人机协同闭环。"))
    story.extend(
        [
            ai_pipeline_diagram(),
            p("图 4-1 智能点餐 AI 集成闭环", CAPTION),
            p("4.4 菜单识别集成", H2),
            bullet("客户端压缩图片并清除 EXIF；后端校验文件类型、分辨率和大小后写入短时对象存储。"),
            bullet("OCR 输出文本块与坐标；视觉模型只完成字段归一化和菜名-价格配对，按 JSON Schema 返回。"),
            bullet("服务端把模型输出映射为 MenuItem，并用价格范围、字符集、重复项和置信度规则二次校验。"),
            bullet("低置信项在前端进入人工校正；只有确认后的菜单才能调用方案规划接口。"),
            p("4.5 方案规划集成", H2),
            table(
                [
                    ["阶段", "处理", "结果"],
                    ["硬约束过滤", "预算上限、过敏原、明确忌口、不可用菜品", "不满足即淘汰，并记录原因"],
                    ["营养计算", "从标准食物数据库按份量计算区间", "能量、蛋白质、蔬菜量等可追溯数据"],
                    ["多目标排序", "营养结构、价格、偏好匹配、菜品多样性", "均衡/轻负担/饱腹等差异化方案"],
                    ["语言解释", "模型把计算结果转为简短理由", "不得修改数值，不得新增未计算的健康结论"],
                    ["用户确认", "选择方案后提交记录", "幂等写入并返回审计标识"],
                ],
                [28 * mm, 77 * mm, 64 * mm],
            ),
            p("4.6 健康问答集成", H2),
            p("先用风险分类器识别医疗诊断、急症、药物和特殊人群，再对一般问题执行检索。只从审核过的指南切片生成回答，引用必须能回指文档、机构和章节。若检索分数低或引用核验失败，则返回“资料不足”的保守响应。"),
            PageBreak(),
        ]
    )


def ai_optimization(story: list) -> None:
    story.extend(section_start("04 / AI SOLUTION", "AI 技术方案：优化策略与安全评测", "优化目标按正确性、安全性、延迟、成本四个维度共同约束。"))
    story.extend(
        [
            p("4.7 分层优化策略", H2),
            table(
                [
                    ["层级", "优化动作", "预期收益", "验证指标"],
                    ["输入层", "图片压缩、透视校正、去噪；问题分类与标准化", "减少 OCR 错误和无效 token", "字段准确率、输入体积、预处理耗时"],
                    ["模型层", "结构化输出、少样本示例、温度收敛、模型路由", "稳定 JSON、降低幻觉与成本", "Schema 通过率、一致性、单次成本"],
                    ["检索层", "权威来源白名单、混合检索、元数据过滤、重排", "提高引用相关性与时效性", "Recall@k、引用支持率、过期资料命中率"],
                    ["规则层", "硬约束前置、数值复算、引用回查、敏感主题拦截", "将高风险错误转为可检测失败", "过敏原漏检率、约束满足率、越界率"],
                    ["服务层", "请求去重、结果缓存、SSE、超时/重试/熔断", "改善 P95 延迟与可用性", "缓存命中率、超时率、P95、错误预算"],
                    ["反馈层", "收集校正、采纳、撤回和引用点击", "形成真实任务评测集", "校正率、方案采纳率、用户撤回率"],
                ],
                [24 * mm, 59 * mm, 46 * mm, 40 * mm],
                font_size=6.5,
            ),
            p("4.8 评测矩阵", H2),
            table(
                [
                    ["测试集", "覆盖", "上线门槛建议"],
                    ["菜单识别集", "清晰/倾斜/反光/手写/多列/低分辨率菜单", "关键字段准确率 >= 95%，价格错配率 <= 1%"],
                    ["约束对抗集", "多重过敏、同义忌口、预算冲突、无可行解", "硬约束满足率 100%，无解时不强行推荐"],
                    ["健康安全集", "疾病、药物、急症、孕产、未成年人、进食障碍", "高风险召回率 >= 99%，不输出诊断/处方"],
                    ["引用忠实集", "答案句子与来源片段逐项对齐", "关键主张引用支持率 >= 98%"],
                    ["稳定性集", "同输入多次调用、模型升级回归", "结构化输出成功率 >= 99.5%，关键结论无漂移"],
                ],
                [29 * mm, 76 * mm, 64 * mm],
            ),
            p("4.9 运行时护栏", H2),
            callout("必须服务端执行", "API 密钥、内容安全、速率限制、上传校验、过敏与医疗规则、模型输出数值复算、引用校验和审计日志都不能仅放在浏览器或提示词中。", ORANGE_SOFT),
            PageBreak(),
        ]
    )


def implementation_flow(story: list) -> None:
    story.extend(section_start("05 / IMPLEMENTATION", "核心功能实现：智能点餐", "SmartMealView 以显式状态机组织上传、校正、决策三个阶段。"))
    story.extend(
        [
            p("5.1 状态与流程", H2),
            table(
                [
                    ["状态", "触发动作", "主要数据", "异常/回退"],
                    ["upload", "选择图片、点击识别", "imageUrl、fileName、request", "无图片时提示；可重置"],
                    ["review", "recognizeMenu 成功", "menuItems、averageConfidence", "识别失败保留上传状态；可更换图片"],
                    ["plans", "用户确认菜单并生成方案", "plans、reviseText、savedId", "生成失败保留识别结果；可返回校正"],
                ],
                [25 * mm, 45 * mm, 47 * mm, 52 * mm],
            ),
            p("5.2 关键实现细节", H2),
            bullet("handleFile 使用 URL.createObjectURL 生成浏览器本地预览；更换图片、重置和组件卸载时调用 revokeObjectURL，避免内存泄漏。"),
            bullet("averageConfidence 对识别项置信度求平均；小于 0.8 的项目在表格中以 uncertain 样式提示人工复核。"),
            bullet("generatePlans 将原始偏好与追加修改合并后调用服务适配层；用户可用自然语言重新计算，而不丢失识别结果。"),
            bullet("choosePlan 只在按钮点击后调用 health.savePlan；AI 不自动修改今日记录。"),
            p("5.3 服务适配契约", H2),
            table(
                [
                    ["函数", "当前行为", "替换为真实服务时保持不变"],
                    ["recognizeMenu()", "等待 1100 ms 后返回 5 个演示菜品", "Promise<MenuItem[]>；置信度范围 0-1；字段完整"],
                    ["buildPlans(items, request)", "解析便宜/不吃牛/不要辣等关键词，返回三方案", "Promise<MealPlan[]>；硬约束不违背；理由非空"],
                    ["askHealthAssistant(question)", "从三类本地知识匹配并提供引用；未知问题拒答", "Promise<ChatMessage>；来源结构化；失败可降级"],
                ],
                [43 * mm, 59 * mm, 67 * mm],
            ),
            p("5.4 可测试性", H2),
            p("视图层只消费服务返回的领域对象，避免直接依赖某个模型 SDK。服务契约已有单元测试，后端接入后可继续作为消费者驱动契约测试，并为网络超时、无效 Schema、空结果和约束冲突补充测试。"),
            PageBreak(),
        ]
    )


def implementation_state(story: list) -> None:
    story.extend(section_start("05 / IMPLEMENTATION", "核心功能实现：状态、趋势与问答", "跨页面状态集中管理，页面级资源在生命周期结束时释放。"))
    story.extend(
        [
            p("5.5 Pinia 健康状态", H2),
            table(
                [
                    ["元素", "实现", "设计意义"],
                    ["持久化键", "foodlens-health-v1", "为数据结构升级预留版本号"],
                    ["容错读取", "JSON.parse 置于 try/catch；失败删除损坏值", "避免手工篡改 localStorage 导致应用崩溃"],
                    ["派生指标", "waterPercent / activityPercent 使用 computed 且上限 100", "统一进度计算并防止视觉溢出"],
                    ["深度监听", "watch(today, selectedPlan, notifications), deep: true", "嵌套字段变化即时写入本地"],
                    ["删除数据", "移除存储键，并把今日状态重置为空记录", "用户有明确的数据控制入口"],
                ],
                [31 * mm, 65 * mm, 73 * mm],
            ),
            p("5.6 趋势可视化", H2),
            p("InsightsView 仅注册 LineChart、BarChart、Grid、Legend、Tooltip 和 CanvasRenderer，避免引入完整 ECharts。图表实例通过 chart ??= echarts.init 只创建一次，指标切换使用 setOption；页面卸载时移除 resize 监听并 dispose。当前构建仍显示该异步块偏大，说明还需进一步按需拆包或替换轻量图库。"),
            p("5.7 AI 健康问答", H2),
            bullet("发送前 trim，并通过 loading 阻止重复提交；消息先入队，再等待异步服务。"),
            bullet("回答成功后带 Citation 列表；异常时明确说明当前无法核对资料，不伪造建议。"),
            bullet("首条消息、侧栏策略和异常文案三处持续声明医疗边界，降低误解风险。"),
            p("5.8 响应式与可用性", H2),
            p("全局 CSS 在 1100 px、760 px、480 px 三个断点重排仪表盘、点餐、问答与设置；移动端侧栏变为抽屉，密集表格隐藏低优先信息。系统尊重 prefers-reduced-motion，按钮和输入大多使用语义元素与可访问标签。"),
            PageBreak(),
        ]
    )


def innovation(story: list) -> None:
    story.extend(section_start("06 / INNOVATION", "技术创新点与应用创新点", "创新来自对健康场景约束的工程化，而不是把所有步骤都交给生成模型。"))
    story.extend(
        [
            p("6.1 技术创新点", H2),
            table(
                [
                    ["编号", "技术创新点", "价值"],
                    ["T-01", "置信度驱动的人机协同识别：低置信菜单项强制进入可编辑校正环节", "把 OCR 不确定性变成显式交互，防止错误一路传播到推荐"],
                    ["T-02", "生成式理解与确定性约束分工：模型理解意图，规则引擎校验预算、过敏和营养计算", "兼顾自然交互与硬约束可验证性"],
                    ["T-03", "稳定服务适配契约：前端只依赖 MenuItem、MealPlan、ChatMessage 等领域对象", "可替换模型/后端，不侵入页面逻辑"],
                    ["T-04", "可追溯健康回答：引用标题、机构、章节作为一等数据结构", "支持引用核验、审计和未来 RAG 评测"],
                    ["T-05", "资源生命周期治理：对象 URL、定时器、监听器和 ECharts 实例统一清理", "降低长会话和多路由切换中的内存泄漏"],
                    ["T-06", "相关性降级表达：小样本趋势用确定性统计与模板语言，不调用模型推断因果", "降低健康场景中的过度解释风险"],
                ],
                [15 * mm, 78 * mm, 76 * mm],
                font_size=6.7,
            ),
            p("6.2 应用创新点", H2),
            table(
                [
                    ["编号", "应用创新点", "价值"],
                    ["A-01", "从“营养知识库”转向“当前可买到什么”的场景化决策", "降低从建议到行动的距离"],
                    ["A-02", "三方案并列展示明确取舍，而不是只给单一“最佳答案”", "尊重预算、饱腹感和个人偏好的多目标现实"],
                    ["A-03", "自然语言换菜后重算，保留用户对方案的控制权", "支持渐进式协商，避免一次性黑盒推荐"],
                    ["A-04", "把今日饮水、睡眠、活动与餐食选择置于同一上下文", "形成轻量的日常健康决策闭环"],
                    ["A-05", "包装标签识别强调单位、份数和过敏核对，而非简单判定“健康/不健康”", "避免道德化标签，提升信息素养"],
                    ["A-06", "健康边界作为常驻产品能力，而非隐藏免责声明", "在关键入口持续提示何时应转向专业人员"],
                ],
                [15 * mm, 78 * mm, 76 * mm],
                font_size=6.7,
            ),
            PageBreak(),
        ]
    )


def testing_overview(story: list) -> None:
    story.extend(section_start("07 / TEST & DEPLOY", "白盒测试策略与覆盖", "测试从可见源码路径出发，覆盖服务契约、状态持久化、异常分支和构建质量。"))
    story.extend(
        [
            p("7.1 测试对象与方法", H2),
            table(
                [
                    ["层级", "白盒关注点", "主要方法"],
                    ["服务适配层", "分支条件、返回结构、约束解析、安全拒答", "Vitest 单元测试、等价类与边界值"],
                    ["Pinia 状态层", "初始化、损坏存储、深度持久化、上限计算、清除数据", "jsdom + Pinia 隔离实例 + localStorage 操作"],
                    ["视图逻辑", "加载/失败/禁用态、对象 URL 和计时器清理", "静态审查 + 组件级测试建议"],
                    ["工程构建", "TypeScript 严格检查、Vite 生产构建、代码分割", "pnpm run build 与产物体积检查"],
                ],
                [31 * mm, 77 * mm, 61 * mm],
            ),
            p("7.2 路径覆盖设计", H2),
            table(
                [
                    ["路径", "输入/前置", "预期断言"],
                    ["菜单正常识别", "调用 recognizeMenu", "返回不少于 3 项；置信度均在 (0,1]"],
                    ["预算约束", "请求“预算 25 元”", "恰好三方案，价格均不超过 25，理由非空"],
                    ["忌口组合", "请求“不要辣，不吃牛肉”", "所有方案不含香辣牛肉"],
                    ["问答命中", "问题含“早餐”", "回答引用膳食指南"],
                    ["问答拒答", "疾病诊断请求", "不做判断，仍提供安全规范引用"],
                    ["持久化边界", "达到/超过目标、写入嵌套字段、清理", "百分比封顶 100；状态序列化；删除后归零"],
                    ["损坏存储", "localStorage 写入非法 JSON", "初始化不崩溃，删除损坏键并使用默认值"],
                ],
                [40 * mm, 55 * mm, 74 * mm],
                font_size=6.8,
            ),
            p("7.3 尚需补充的测试", H2),
            bullet("组件级测试：上传文件、错误提示、低置信行、重算、确认写入、删除二次确认。"),
            bullet("端到端测试：桌面与移动端主流程、路由懒加载、刷新持久化、断网降级和无障碍键盘操作。"),
            bullet("真实 AI 接入测试：Schema 无效、超时、限流、引用错配、提示注入、对抗菜单图像和高风险健康问题。"),
            PageBreak(),
        ]
    )


def testing_results(story: list) -> None:
    if not TEST_REPORT.exists():
        raise FileNotFoundError(f"White-box report is required before final PDF generation: {TEST_REPORT}")
    report_text = TEST_REPORT.read_text(encoding="utf-8")
    for evidence in ["17/17", "2 个 P1", "5 个 P2", "5 个 P3", "6/6", "No known vulnerabilities found"]:
        if evidence not in report_text:
            raise ValueError(f"Expected white-box evidence is missing: {evidence}")
    story.extend(section_start("07 / TEST & DEPLOY", "白盒测试结果与缺陷分析", "以下结论来自独立测试子任务产出的可重复执行结果。"))
    story.extend(
        [
            p("7.4 执行环境与结果", H2),
            table(
                [
                    ["检查项", "命令/范围", "结果", "判定"],
                    ["自动化测试", "pnpm run test", "5 个测试文件，17/17 通过，总耗时 6.94 s", "通过"],
                    ["类型检查", "pnpm exec vue-tsc -b --pretty false", "0 诊断", "通过"],
                    ["生产构建", "pnpm run build", "2189 模块，4.47 s；InsightsView 542.96 kB", "通过，带非阻断警告"],
                    ["生产依赖审计", "pnpm audit --prod", "No known vulnerabilities found", "通过"],
                    ["路由直达冒烟", "预览服务访问 6 条业务路由", "6/6 返回 HTTP 200、text/html 且包含 #app", "通过"],
                ],
                [36 * mm, 46 * mm, 55 * mm, 32 * mm],
                font_size=6.6,
            ),
            p("7.5 缺陷分级结论", H2),
            two_cards(
                "演示部署：有条件通过",
                "现有测试、类型检查、构建、生产依赖审计和 6 条业务路由直达均通过。配置 SPA history fallback 后，可用于比赛展示或内部原型验证。",
                "真实生产上线：不通过",
                "共确认 12 项缺陷：2 个 P1、5 个 P2、5 个 P3。两项 P1 涉及核心点餐决策正确性和医疗安全边界，修复前不能面向真实用户提供健康决策服务。",
            ),
            Spacer(1, 5 * mm),
            callout("P1 / WB-01：点餐约束未真正参与方案计算", "buildPlans 只识别少量关键词，方案菜名、价格和营养值大部分硬编码。修改识别价格不会改变方案；预算 10 元仍返回 16-20 元方案；空菜单仍生成原菜品；过敏原字段从未参与筛选。应把自然语言转为结构化约束，只从确认菜单组合，并由确定性规则先处理预算、过敏和忌口。", ORANGE_SOFT),
            Spacer(1, 4 * mm),
            callout("P1 / WB-02：医疗高风险意图可被普通关键词绕过", "askHealthAssistant 先按早餐、饮水、睡眠子串命中，没有在检索前拦截疾病、孕产、未成年人、用药、进食障碍和急症。例如“孕期饮水要多少”会返回普通饮水建议。必须把高风险分类放在知识检索之前，并在后端执行规则与红队回归。", ORANGE_SOFT),
            PageBreak(),
        ]
    )

    story.extend(section_start("07 / TEST & DEPLOY", "缺陷矩阵与整改优先级", "优先修复会造成错误健康决策、用户误解或隐私暴露的问题。"))
    story.extend(
        [
            p("7.6 P2 与 P3 缺陷矩阵", H2),
            table(
                [
                    ["编号/级别", "问题", "影响与建议"],
                    ["WB-03 / P2", "设置偏好保存与数据导出未实现", "刷新丢失，点餐不能使用过敏信息；接入 Store/后端并实现导出"],
                    ["WB-04 / P2", "营养标签“记入今天”按钮无行为", "造成已记录错觉；绑定份数、写入动作与成功反馈"],
                    ["WB-05 / P2", "localStorage 无 Schema 校验和写入降级", "类型污染可导致字符串拼接或异常；增加 type guard/Zod 与合理范围"],
                    ["WB-06 / P2", "生产构建公开完整 sourcemap", "暴露源码并增大产物；关闭或使用 hidden map 上传监控"],
                    ["WB-07 / P2", "缺少未知路由/404 兜底", "错误链接显示空内容；增加 catch-all 路由和返回首页入口"],
                    ["WB-08 / P3", "上传无真实类型、大小和解码校验", "破损预览和未来上传攻击面；客户端提示 + 服务端重编码"],
                    ["WB-09 / P3", "趋势页 chunk 542.96 kB", "首次进入趋势页较慢；进一步拆包或采用轻量图表"],
                    ["WB-10 / P3", "多个可操作按钮无行为", "视觉承诺与实际不一致；隐藏未实现入口或补齐交互"],
                    ["WB-11 / P3", "日期与趋势结论硬编码", "时间变化后信息过期；从 Store 和系统时间统一派生"],
                    ["WB-12 / P3", "缺少 CSP 与宿主安全头", "生产纵深防御不足；由 CDN/Nginx 设置 CSP、HSTS 等"],
                ],
                [25 * mm, 61 * mm, 83 * mm],
                font_size=6.2,
            ),
            p("7.7 正向观察", H2),
            bullet("TypeScript 严格模式、Vue 类型检查和生产构建通过；生产直接依赖审计未发现已知漏洞。", SMALL),
            bullet("路由懒加载使 ECharts 未进入首屏主包；对象 URL、计时器、resize 监听和图表实例均在卸载时释放。", SMALL),
            bullet("模板未发现 v-html、innerHTML、eval、前端 API 密钥或真实网络请求，当前 XSS 与密钥暴露面较小。", SMALL),
            bullet("AI 异步失败有显式降级，餐食写入必须由用户确认，损坏 JSON 能回退默认数据。", SMALL),
            p("7.8 整改顺序", H2),
            callout("先安全与正确性，后完整性与体验", "第一批修复 WB-01/WB-02，并建立约束/高风险自动回归；第二批处理 Store Schema、设置持久化、标签写入、sourcemap 与 404；第三批补齐按钮行为、动态趋势、上传校验、CSP 和体积预算。修复后再执行 17 个现有用例、扩展安全用例和端到端回归。", GREEN_SOFT),
            Spacer(1, 4 * mm),
            p("测试证据文件：WHITEBOX_TEST_REPORT.md（152 行，位于项目根目录）。覆盖率插件未安装，因此未生成行/分支百分比；本报告不虚构覆盖率数字。", SMALL),
            PageBreak(),
        ]
    )


def deployment(story: list) -> None:
    story.extend(section_start("07 / TEST & DEPLOY", "部署方案与上线检查", "当前原型可静态部署；真实 AI 版本需要后端、数据库和可观测性配套。"))
    story.extend(
        [
            p("7.7 原型部署", H2),
            table(
                [
                    ["步骤", "命令/动作", "产物与检查"],
                    ["安装依赖", "pnpm install --frozen-lockfile", "依赖版本严格依据 pnpm-lock.yaml"],
                    ["自动测试", "pnpm run test", "所有 Vitest 用例通过"],
                    ["生产构建", "pnpm run build", "vue-tsc 无错误；dist 生成；审查块体积告警"],
                    ["静态发布", "上传 dist 到 CDN/静态托管", "配置 SPA history fallback 到 index.html"],
                    ["验收", "桌面/移动端冒烟测试", "六条路由、上传预览、状态刷新、趋势图和错误提示"],
                ],
                [28 * mm, 59 * mm, 82 * mm],
            ),
            p("7.8 生产环境配置", H2),
            bullet("前端仅保存 VITE_API_BASE_URL 等公开配置；任何供应商密钥只进入后端密钥管理系统。"),
            bullet("后端容器以非 root 用户运行；数据库和对象存储使用私网；出口访问按模型供应商域名白名单控制。"),
            bullet("健康数据加密传输和静态加密；访问日志脱敏；备份、删除请求和留存策略可验证。"),
            bullet("为 OCR、规划、RAG 和安全拒答分别建立指标面板，不用单一“成功率”掩盖局部失效。"),
            p("7.9 发布门禁", H2),
            table(
                [
                    ["门禁", "最低条件", "失败处理"],
                    ["代码质量", "类型检查、单元测试、关键 E2E 全绿", "阻断发布"],
                    ["AI 质量", "约束满足率、引用支持率、安全召回率达到阈值", "回滚模型/提示词/知识版本"],
                    ["性能", "LCP、路由块体积、API P95、错误率符合预算", "优化拆包、缓存或降级"],
                    ["安全与隐私", "密钥扫描、依赖扫描、上传安全、日志脱敏通过", "阻断发布并修复"],
                    ["可回滚", "前端版本、API、模型和知识库均可独立回滚", "执行自动回滚并保留审计"],
                ],
                [29 * mm, 84 * mm, 56 * mm],
            ),
            PageBreak(),
        ]
    )


def roadmap(story: list) -> None:
    story.extend(section_start("08 / CONCLUSION", "总结与展望", "餐衡已验证以“可解释决策”连接日常健康记录与实际就餐选择的产品路径。"))
    story.extend(
        [
            p("8.1 总结", H2),
            p("项目在有限代码规模内形成了较完整的业务闭环：输入来自菜单图片、偏好和今日记录；中间通过人工校正与多方案比较降低不确定性；输出包含可执行选择、估算范围和理由；用户确认后才写入状态。健康问答和趋势洞察主动限制结论强度，体现了健康场景中较成熟的风险意识。"),
            p("从工程角度看，Vue 视图、Pinia 状态、领域类型和 AI 服务适配层职责清晰，路由懒加载、异常反馈与资源释放具备较好的原型质量。主要差距集中在真实 AI 能力、后端安全、数据治理、模型评测和自动化测试深度。"),
            p("8.2 演进路线", H2),
            table(
                [
                    ["阶段", "目标", "关键交付物", "退出标准"],
                    ["M1 工程加固", "补齐组件/E2E 测试与输入校验", "测试矩阵、Schema 校验、体积优化、CI 门禁", "关键路径自动化；构建无高风险告警"],
                    ["M2 真实 AI 试点", "接入菜单识别、约束规划与 RAG", "后端 API、知识白名单、评测集、安全规则", "离线指标达标；小流量灰度无严重越界"],
                    ["M3 数据闭环", "用校正和采纳反馈持续优化", "反馈事件、模型/提示词版本、评测看板", "性能与质量指标可按版本对比"],
                    ["M4 场景扩展", "拓展食堂/餐厅/包装食品合作", "菜单数据接口、机构端配置、合规方案", "真实场景留存和决策效率验证"],
                ],
                [28 * mm, 46 * mm, 61 * mm, 34 * mm],
                font_size=6.8,
            ),
            p("8.3 长期方向", H2),
            two_cards(
                "技术方向",
                "多模型路由与离线缓存；营养知识图谱；多模态菜单版面理解；个体偏好的可解释学习；联邦/端侧推理探索；贯穿数据、模型和规则的审计链。",
                "应用方向",
                "校园和园区菜单协同；家庭购物与备餐；慢性病人群仅在医疗机构监督下的合规扩展；面向营养师的方案审核台；公共健康知识传播。",
            ),
            Spacer(1, 8 * mm),
            callout("最终判断", "该项目适合作为 AI 健康决策产品的前端原型和交互验证基础。下一步优先级应是：先补足工程测试与输入治理，再接入可评测的真实 AI 服务，最后扩展个性化和跨设备数据能力。", GREEN_SOFT),
            PageBreak(),
        ]
    )


def appendix(story: list) -> None:
    story.extend(section_start("APPENDIX", "附录：源码证据与质量检查清单", "关键结论均可回溯到当前项目文件。"))
    story.extend(
        [
            p("A.1 源码证据索引", H2),
            table(
                [
                    ["结论", "源码位置"],
                    ["六条业务路由与懒加载", "src/router.ts"],
                    ["智能点餐三阶段状态机、对象 URL 释放、用户确认写入", "src/views/SmartMealView.vue"],
                    ["AI/OCR/规划/问答适配契约与演示实现", "src/services/mockApi.ts"],
                    ["今日状态、派生进度、本地持久化和删除", "src/stores/health.ts"],
                    ["图表按需注册、复用、监听移除与 dispose", "src/views/InsightsView.vue"],
                    ["问答引用、拒答与异常降级", "src/views/AssistantView.vue"],
                    ["标签预览、计时器和资源清理", "src/views/RecordsView.vue"],
                    ["隐私开关、数据删除二次确认和健康边界", "src/views/SettingsView.vue"],
                    ["服务契约测试", "src/services/mockApi.test.ts"],
                    ["技术栈、脚本与版本", "package.json / pnpm-lock.yaml"],
                ],
                [76 * mm, 93 * mm],
            ),
            p("A.2 文档生成质量检查", H2),
            table(
                [
                    ["检查项", "标准"],
                    ["页数", "不超过 30 页"],
                    ["字体", "中文字体嵌入，无乱码或缺字方框"],
                    ["版面", "页眉、页脚、页码连续；表格无截断；图形与文字不重叠"],
                    ["内容", "包含项目概述、需求、架构、AI、实现、测试部署、总结展望"],
                    ["AI 重点", "选型理由、集成方式、优化策略均独立成节"],
                    ["创新点", "技术创新点与应用创新点明确分列"],
                    ["证据", "白盒测试报告存在并在 PDF 生成前读取"],
                ],
                [42 * mm, 127 * mm],
            ),
            p("A.3 免责声明", H2),
            p("餐衡仅面向普通成年人的一般健康信息管理。本报告中的 AI 生产化方案属于工程设计建议，不代表已完成医疗器械、互联网医疗或个人信息保护等专项合规认证。涉及疾病、孕产期、未成年人、进食障碍、用药或急性症状时，应由专业医疗人员处理。", SMALL),
        ]
    )


def build_pdf() -> int:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    story: list = []
    cover_page(story)
    executive_summary(story)
    project_overview(story)
    requirements(story)
    requirements_boundary(story)
    architecture_current(story)
    architecture_target(story)
    ai_selection(story)
    ai_integration(story)
    ai_optimization(story)
    implementation_flow(story)
    implementation_state(story)
    innovation(story)
    testing_overview(story)
    testing_results(story)
    deployment(story)
    roadmap(story)
    appendix(story)

    frame = Frame(MARGIN_X, BOTTOM, PAGE_W - 2 * MARGIN_X, PAGE_H - TOP - BOTTOM, id="normal")
    doc = BaseDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        leftMargin=MARGIN_X,
        rightMargin=MARGIN_X,
        topMargin=TOP,
        bottomMargin=BOTTOM,
        title="餐衡 FoodLens 项目白盒测试与技术报告",
        author="Codex 文档子智能体",
        subject="项目概述、需求分析、架构设计、AI 技术方案、核心实现、白盒测试与部署",
    )
    doc.addPageTemplates(PageTemplate(id="report", frames=[frame], onPage=header_footer))
    doc.build(story)
    reader = PdfReader(str(OUTPUT))
    return len(reader.pages)


if __name__ == "__main__":
    pages = build_pdf()
    print(f"OUTPUT={OUTPUT}")
    print(f"PAGES={pages}")
    if pages > 30:
        raise SystemExit(f"Page limit exceeded: {pages}")
