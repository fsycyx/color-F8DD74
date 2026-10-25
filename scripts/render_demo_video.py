from __future__ import annotations

import math
import subprocess
from pathlib import Path

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
TMP = ROOT / "tmp" / "video"
SCREENS = TMP / "screens"
SCENES = TMP / "scenes"
OUTPUT = ROOT / "output" / "video"
WIDTH, HEIGHT = 1920, 1080
FPS = 30

FONT_REGULAR = r"C:\Windows\Fonts\msyh.ttc"
FONT_BOLD = r"C:\Windows\Fonts\msyhbd.ttc"

GREEN = "#125d42"
MINT = "#e9f3ee"
INK = "#15251e"
MUTED = "#65716b"
WHITE = "#ffffff"
GOLD = "#d78b42"
BLUE = "#2f6ca4"


def font(size: int, bold: bool = False):
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REGULAR, size)


def rounded(draw, box, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def fit_text(draw, text, box_width, start_size, min_size=22, bold=False):
    size = start_size
    while size > min_size and draw.textbbox((0, 0), text, font=font(size, bold))[2] > box_width:
        size -= 1
    return font(size, bold)


def make_menu_fixture():
    path = TMP / "fixtures" / "menu-demo.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", (1200, 1600), "#f7f2e7")
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((70, 60, 1130, 1540), radius=28, fill="#fffdf8", outline="#d8c8ad", width=4)
    draw.text((120, 110), "今日食堂菜单", font=font(68, True), fill=GREEN)
    draw.text((120, 205), "营养套餐 · 当日供应", font=font(34), fill=MUTED)
    items = [
        ("糙米饭", "¥3"), ("清蒸鸡腿", "¥10"), ("蒜蓉西兰花", "¥6"),
        ("番茄炒蛋", "¥7"), ("香辣牛肉", "¥13"), ("时令水果", "¥5"),
    ]
    y = 330
    for idx, (name, price) in enumerate(items, 1):
        draw.ellipse((120, y + 12, 148, y + 40), fill=GREEN if idx < 5 else GOLD)
        draw.text((180, y), name, font=font(42, True), fill=INK)
        draw.text((870, y), price, font=font(42, True), fill=GREEN)
        draw.line((120, y + 75, 1080, y + 75), fill="#e1ded5", width=2)
        y += 150
    draw.text((120, 1300), "少油少盐 · 如有过敏请提前告知", font=font(30), fill=MUTED)
    image.save(path)


def background():
    image = Image.new("RGB", (WIDTH, HEIGHT), "#f4f6f3")
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, WIDTH, 12), fill=GREEN)
    draw.rectangle((0, HEIGHT - 10, WIDTH, HEIGHT), fill="#dbe8e1")
    return image


def title_card(title, subtitle, eyebrow, bullets=None, accent=GREEN):
    image = background()
    draw = ImageDraw.Draw(image)
    draw.text((120, 92), eyebrow, font=font(25, True), fill=accent)
    draw.text((120, 178), title, font=fit_text(draw, title, 1600, 74, bold=True), fill=INK)
    draw.text((124, 286), subtitle, font=fit_text(draw, subtitle, 1560, 36), fill=MUTED)
    draw.rounded_rectangle((120, 382, 1800, 900), radius=18, fill=WHITE, outline="#cedbd4", width=2)
    if bullets:
        y = 455
        for idx, item in enumerate(bullets, 1):
            draw.ellipse((190, y + 8, 220, y + 38), fill=accent)
            draw.text((250, y), item, font=fit_text(draw, item, 1450, 37, bold=idx == 1), fill=INK)
            y += 115
    draw.text((120, 990), "餐衡 FoodLens  ·  仅提供一般健康信息，不替代医疗诊断", font=font(24), fill=MUTED)
    return image


def architecture_card(title, subtitle, columns):
    image = background()
    draw = ImageDraw.Draw(image)
    draw.text((120, 78), "AI 技术亮点", font=font(26, True), fill=GREEN)
    draw.text((120, 145), title, font=font(64, True), fill=INK)
    draw.text((122, 238), subtitle, font=font(31), fill=MUTED)
    count = len(columns)
    gap = 26
    card_w = (1680 - gap * (count - 1)) // count
    x = 120
    palette = ["#e9f3ee", "#e8f0f7", "#f5ece2", "#efebf7", "#f0f2ee"]
    for i, (head, body) in enumerate(columns):
        rounded(draw, (x, 360, x + card_w, 830), 16, palette[i % len(palette)], "#c7d6ce", 2)
        draw.text((x + 28, 405), f"0{i + 1}", font=font(24, True), fill=GREEN)
        draw.text((x + 28, 465), head, font=fit_text(draw, head, card_w - 56, 34, bold=True), fill=INK)
        lines = body.split("\n")
        y = 555
        for line in lines:
            draw.text((x + 28, y), line, font=fit_text(draw, line, card_w - 56, 25), fill=MUTED)
            y += 58
        if i < count - 1:
            draw.polygon([(x + card_w + 6, 585), (x + card_w + 21, 570), (x + card_w + 21, 600)], fill=GREEN)
        x += card_w + gap
    draw.text((120, 960), "模型负责理解与解释，关键健康约束由确定性规则兜底。", font=font(28, True), fill=GREEN)
    return image


def screenshot_scene(filename, caption, detail, chapter):
    source = Image.open(SCREENS / filename).convert("RGB")
    canvas = Image.new("RGB", (WIDTH, HEIGHT), "#101c17")
    blurred = source.resize((WIDTH, HEIGHT)).filter(ImageFilter.GaussianBlur(22))
    blurred = Image.blend(blurred, Image.new("RGB", blurred.size, "#183127"), 0.30)
    canvas.paste(blurred, (0, 0))
    page = source.resize((1690, 951), Image.Resampling.LANCZOS)
    canvas.paste(page, (115, 34))
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.rounded_rectangle((98, 790, 1822, 1040), radius=20, fill=(8, 25, 19, 235), outline=(85, 142, 113, 255), width=2)
    od.rounded_rectangle((128, 818, 350, 866), radius=8, fill=(18, 93, 66, 255))
    od.text((153, 826), chapter, font=font(23, True), fill=WHITE)
    od.text((128, 886), caption, font=fit_text(od, caption, 1635, 42, bold=True), fill=WHITE)
    od.text((128, 956), detail, font=fit_text(od, detail, 1635, 27), fill="#d8e6df")
    return Image.alpha_composite(canvas.convert("RGBA"), overlay).convert("RGB")


def closing_card():
    image = background()
    draw = ImageDraw.Draw(image)
    draw.text((120, 95), "演示总结", font=font(27, True), fill=GREEN)
    draw.text((120, 175), "从记录事实，到做出更合适的当下选择", font=fit_text(draw, "从记录事实，到做出更合适的当下选择", 1600, 65, bold=True), fill=INK)
    boxes = [
        ("核心体验", "记录、识别、比较、问答\n形成连续的日常决策闭环", MINT),
        ("AI 原则", "模型理解 + 规则约束 + 引用证据\n不把生成内容当作医学判断", "#e8f0f7"),
        ("质量现状", "17/17 自动化用例通过\n演示可用，生产上线仍需修复 P1", "#f7ede4"),
    ]
    x = 120
    for head, body, fill in boxes:
        rounded(draw, (x, 390, x + 520, 745), 18, fill, "#c9d7d0", 2)
        draw.text((x + 35, 435), head, font=font(35, True), fill=GREEN)
        y = 525
        for line in body.split("\n"):
            draw.text((x + 35, y), line, font=font(27), fill=INK)
            y += 62
        x += 570
    draw.text((120, 890), "餐衡 FoodLens", font=font(45, True), fill=GREEN)
    draw.text((120, 958), "谢谢观看", font=font(30), fill=MUTED)
    return image


def write_srt(scenes):
    def stamp(seconds):
        ms = int(round(seconds * 1000))
        h, ms = divmod(ms, 3600000)
        m, ms = divmod(ms, 60000)
        s, ms = divmod(ms, 1000)
        return f"{h:02}:{m:02}:{s:02},{ms:03}"

    cursor = 0.0
    lines = []
    for index, scene in enumerate(scenes, 1):
        start, end = cursor, cursor + scene["duration"]
        lines.extend([str(index), f"{stamp(start)} --> {stamp(end)}", scene["subtitle"], ""])
        cursor = end
    (OUTPUT / "餐衡FoodLens五分钟演示视频字幕.srt").write_text("\n".join(lines), encoding="utf-8-sig")


def main():
    SCENES.mkdir(parents=True, exist_ok=True)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    make_menu_fixture()

    scenes = [
        {"duration": 12, "subtitle": "餐衡 FoodLens：面向日常饮食与生活方式记录的 AI 健康决策助手。", "image": title_card("餐衡 FoodLens", "五分钟项目演示 · 中文字幕版", "AI 健康决策助手", ["项目介绍", "核心功能演示", "AI 技术亮点与质量边界"])},
        {"duration": 14, "subtitle": "项目聚焦普通成年人日常场景，把饮食选择、健康记录、趋势洞察和知识问答连接成一条可解释的决策链。", "image": title_card("项目介绍", "让健康建议从“知道”走向“当下可执行”", "01 / PROJECT", ["真实菜单与个人偏好共同参与决策", "只基于用户主动记录的数据形成洞察", "一般健康信息，不替代医疗诊断"])},
        {"duration": 14, "subtitle": "首页汇总饮水、睡眠、活动和蔬菜状态，并把下一步行动放在最醒目的位置。", "screen": ("01-dashboard.png", "今日健康驾驶舱", "四项关键指标与行动建议在一个页面内完成扫描。", "核心功能")},
        {"duration": 12, "subtitle": "用户可以通过快捷按钮记录饮水，状态立即写入今日上下文，并同步更新进度。", "screen": ("02-dashboard-water.png", "快速记录，状态即时联动", "同一份 Pinia 状态会被首页、记录页与趋势页复用。", "核心功能")},
        {"duration": 14, "subtitle": "智能点餐从上传真实菜单开始。图片在演示版中只用于浏览器本地预览，不上传原图。", "screen": ("04-meal-image-ready.png", "上传菜单或外卖截图", "同时输入预算、忌口和希望补充的营养目标。", "智能点餐")},
        {"duration": 16, "subtitle": "识别结果先进入人工校正环节。低置信度项目会被突出显示，避免错误数据直接进入推荐。", "screen": ("05-meal-review.png", "识别之后，先校正再计算", "菜名与价格可编辑，平均置信度可见。", "智能点餐")},
        {"duration": 16, "subtitle": "系统并列展示均衡、轻负担和饱腹三类方案，明确价格、能量范围、蛋白质、蔬菜量和推荐理由。", "screen": ("06-meal-plans.png", "三个方案，清楚呈现取舍", "不只给单一答案，让用户比较后自主选择。", "智能点餐")},
        {"duration": 12, "subtitle": "只有用户主动确认后，方案才会写入今日记录，AI 不自动执行有状态操作。", "screen": ("07-meal-selected.png", "用户确认后再写入", "保留对最终选择的控制权。", "智能点餐")},
        {"duration": 14, "subtitle": "健康记录覆盖饮水、睡眠、活动、情绪与饥饿感，十秒即可完成一次记录。", "screen": ("08-records.png", "记录事实，不评判选择", "数据越完整，后续建议越贴近当天情境。", "健康记录")},
        {"duration": 14, "subtitle": "包装食品功能支持营养标签和配料表识别，并要求用户核对单位和实际份数。", "screen": ("09-label-upload.png", "食品标签识别", "拍摄后仍需核对每份或每百克的标示方式。", "健康记录")},
        {"duration": 16, "subtitle": "识别结果同时展示营养信息和潜在过敏原，并明确交叉污染风险与信息边界。", "screen": ("10-label-result.png", "营养信息与过敏风险并列呈现", "系统整理信息，不简单判断食品“好”或“坏”。", "健康记录")},
        {"duration": 15, "subtitle": "趋势页把七日记录转化为饮水、睡眠和活动变化，帮助用户复盘习惯。", "screen": ("11-insights-water.png", "七日趋势，而不是单日评分", "结论只来自用户主动记录的数据。", "趋势洞察")},
        {"duration": 13, "subtitle": "用户可以切换指标查看变化。系统只描述数据关联，不把相关性包装成医学因果。", "screen": ("12-insights-activity.png", "可切换的趋势与小行动", "用确定性统计生成轻量、可执行的下周目标。", "趋势洞察")},
        {"duration": 14, "subtitle": "AI 健康问答首先声明能力边界，只回答饮食、饮水、活动与睡眠的一般知识。", "screen": ("13-assistant-intro.png", "有来源的健康知识", "证据不足时明确拒答，不进行疾病诊断。", "AI 问答")},
        {"duration": 16, "subtitle": "命中知识库后，回答同时显示资料标题、发布机构和章节，支持后续核验。", "screen": ("14-assistant-citation.png", "回答与引用一起呈现", "可追溯结构为未来接入 RAG 和引用校验保留接口。", "AI 问答")},
        {"duration": 14, "subtitle": "当前原型仍存在高风险意图可能被普通关键词绕过的问题，生产版本必须先做安全分类，再检索和生成。", "screen": ("15-assistant-boundary.png", "安全边界必须前置", "白盒测试已将该问题列为 P1 上线阻断项。", "质量边界")},
        {"duration": 14, "subtitle": "设置页持续展示隐私控制和健康边界，敏感删除操作需要二次确认。", "screen": ("16-settings.png", "隐私控制与健康边界", "正式上线还需补齐偏好持久化、数据导出与服务端治理。", "设置与隐私")},
        {"duration": 15, "subtitle": "AI 技术选型采用分层组合：视觉模型负责 OCR，规则引擎执行硬约束，RAG 负责有来源问答。", "image": architecture_card("为什么采用分层 AI", "把可解释性、可验证性和健康安全放在模型能力之前", [("视觉识别", "OCR 提取文字\n视觉模型补充版面"), ("规则规划", "预算与过敏硬约束\n多目标方案排序"), ("健康问答", "权威资料 RAG\n受限生成与引用")])},
        {"duration": 15, "subtitle": "前端只依赖稳定的数据契约。真实模型和数据库通过后端适配层接入，密钥、规则和审计不进入浏览器。", "image": architecture_card("AI 集成方式", "前端交互与后端智能能力解耦", [("Vue 前端", "上传与人工校正\n方案比较与确认"), ("API 适配层", "结构化 Schema\n超时、重试与降级"), ("AI 编排", "OCR、约束求解\nRAG 与安全分类"), ("可信数据", "营养数据库\n权威健康资料")])},
        {"duration": 14, "subtitle": "优化策略覆盖输入压缩、结构化输出、缓存与模型路由，同时用规则兜底、引用校验和红队回归控制风险。", "image": architecture_card("优化策略与安全评测", "同时约束准确性、安全性、延迟与成本", [("输入层", "图像压缩与纠偏\n问题分类"), ("模型层", "结构化输出\n小样本与路由"), ("检索层", "混合检索与重排\n元数据过滤"), ("规则层", "过敏与医疗拦截\n数值复算"), ("评测层", "引用正确率\n拒答与回归集")])},
        {"duration": 16, "subtitle": "白盒测试 17 项全部通过，但发现两项 P1：点餐约束尚未真正参与计算，医疗高风险意图拦截不足。演示可用，生产上线前必须修复。", "image": closing_card()},
    ]

    total = sum(scene["duration"] for scene in scenes)
    if total != 300:
        raise RuntimeError(f"Scene duration must total 300 seconds, got {total}")

    concat_lines = []
    for idx, scene in enumerate(scenes, 1):
        if "screen" in scene:
            filename, caption, detail, chapter = scene["screen"]
            image = screenshot_scene(filename, caption, detail, chapter)
        else:
            image = scene["image"]
        scene_path = SCENES / f"scene-{idx:02}.png"
        image.save(scene_path, quality=95)
        concat_lines.extend([f"file '{scene_path.as_posix()}'", f"duration {scene['duration']}"])
    concat_lines.append(f"file '{(SCENES / f'scene-{len(scenes):02}.png').as_posix()}'")
    concat_file = TMP / "concat.txt"
    concat_file.write_text("\n".join(concat_lines), encoding="utf-8")
    write_srt(scenes)

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    output_path = OUTPUT / "餐衡FoodLens五分钟演示视频.mp4"
    command = [
        ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file),
        "-vf", f"fps={FPS},scale={WIDTH}:{HEIGHT}:flags=lanczos,format=yuv420p",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-movflags", "+faststart",
        "-t", "300", "-an", str(output_path),
    ]
    subprocess.run(command, check=True)
    print(output_path)


if __name__ == "__main__":
    main()
