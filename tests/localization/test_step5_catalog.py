from __future__ import annotations

import re
import subprocess
import sys
import unicodedata
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

from probability_calibration_tool.ui.localization import CHARACTER_SOURCES

from .step5_support import CONTEXTS, INACTIVE_TYPES, ROOT, TS_PATH, catalog_map, load_catalog

PLACEHOLDER = re.compile(r"%[1-9][0-9]*")
IDENTICAL_ALLOWLIST = {
    ("Characters", "???"): "Frozen canonical character identity",
}

CHARACTERS = (
    "以撒",
    "抹大拉",
    "该隐",
    "犹大",
    "???",
    "夏娃",
    "参孙",
    "阿撒泻勒",
    "拉撒路",
    "伊甸",
    "游魂",
    "莉莉丝",
    "店主",
    "亚玻伦",
    "遗骸",
    "伯大尼",
    "雅各和以扫",
    "堕化以撒",
    "堕化抹大拉",
    "堕化该隐",
    "堕化犹大",
    "堕化???",
    "堕化夏娃",
    "堕化参孙",
    "堕化阿撒泻勒",
    "堕化拉撒路",
    "堕化伊甸",
    "堕化游魂",
    "堕化莉莉丝",
    "堕化店主",
    "堕化亚玻伦",
    "堕化遗骸",
    "堕化伯大尼",
    "堕化雅各",
)

FROZEN_EXACT = {
    ("Analysis", "Subjective Analysis"): "主观概率分析",
    ("Analysis", "Probability"): "概率",
    ("Analysis", "Uncertainty interval"): "不确定性区间",
    ("Analysis", "Win-side EV / S"): "胜方 EV / S",
    ("Analysis", "Lose-side EV / S"): "负方 EV / S",
    ("Analysis", "Break-even thresholds"): "盈亏平衡阈值",
    ("Analysis", "Odds combination"): "赔率组合状态",
    ("Analysis", "Calculated locally"): "计算时间（本地时间）",
    ("Analysis", "Historical Analysis — independent model"): "历史模型分析——独立模型",
    ("Analysis", "Eligible observations"): "有效历史样本",
    ("Analysis", "Historical probability"): "历史概率",
    ("Analysis", "Historical interval"): "历史概率不确定性区间",
    ("Analysis", "Win-side EV / posterior"): "胜方 EV / 后验概率",
    ("Analysis", "Lose-side EV / posterior"): "负方 EV / 后验概率",
    ("Analysis", "Model relations"): "模型关系",
    ("Analysis", "Data through locally"): "数据截止时间（本地时间）",
    (
        "Analysis",
        "Locked analysis from the last successful calculation. Pending edits are not reflected until Recalculate succeeds.",
    ): "当前显示的是上次成功计算后锁定的分析结果。当前修改只有在重新计算成功后才会反映到分析结果中。",
    (
        "Analysis",
        "Win %1; loss event %2; loss as win-probability %3",
    ): "胜方：%1；负方事件概率：%2；负方（按胜率表示）：%3",
    (
        "Analysis",
        "%1% entered; %2% used for mathematical calculation.",
    ): "输入值为 %1%；数学计算按 %2% 使用。",
    (
        "Analysis",
        "Warning: Double-positive window detected. Check the input/multiplier timing.",
    ): "警告：检测到双侧正 EV 区间。请检查输入值和赔率倍率的取值时点。",
    (
        "Analysis",
        "Historical reference was not requested for this prediction.",
    ): "本次预测未选择参考历史数据。",
    (
        "Analysis",
        "No eligible history is available for the current character/regime.",
    ): "当前角色在当前历史阶段暂无有效历史样本。",
    (
        "Analysis",
        "Historical data is not yet sufficient for numerical reference.",
    ): "历史数据尚不足，暂不提供数值参考。",
    ("Analysis", "Wins %1; losses %2; samples %3"): "胜：%1；负：%2；样本数：%3",
    ("Analysis", "Win: %1; Loss: %2"): "胜方：%1；负方：%2",
    ("AppShell", "Dismiss"): "关闭提示",
    ("AppShell", "Historical Correction"): "历史记录更正",
    ("AppShell", "Restore"): "备份恢复",
    ("AppShell", "Round"): "单局",
    ("AppShell", "Maintenance"): "维护",
    ("Correction", "Historical Correction — post-run facts only"): "历史记录更正——仅限局后信息",
    (
        "Correction",
        "Identify a completed record by character, time and round ID.",
    ): "请根据角色、时间和单局 ID 确认要更正的已完成记录。",
    ("Correction", "Correct selected record"): "更正所选记录",
    ("Correction", "Corrected result: Win"): "更正后的结果：胜",
    ("Correction", "Corrected result: Loss"): "更正后的结果：负",
    ("Correction", "Corrected: Include"): "更正后：计入历史",
    ("Correction", "Corrected: Exclude"): "更正后：不计入历史",
    ("Correction", "Required correction reason"): "更正原因（必填）",
    ("Correction", "Confirm Correction"): "确认更正",
    ("Correction", "Back"): "返回",
    ("Correction", "Correction saved."): "更正已保存。",
    ("DomainLabels", "Robust positive"): "稳健正 EV",
    ("DomainLabels", "Robust negative"): "稳健负 EV",
    ("DomainLabels", "Crosses threshold"): "触及盈亏平衡阈值",
    ("DomainLabels", "Normal overlap"): "常规阈值重叠",
    ("DomainLabels", "Critical"): "阈值临界",
    ("DomainLabels", "Double positive window"): "双侧正 EV 区间",
    ("DomainLabels", "Agreement positive"): "正向一致",
    ("DomainLabels", "Agreement negative"): "负向一致",
    ("DomainLabels", "Conflict"): "方向冲突",
    ("DomainLabels", "Uncertain"): "关系不确定",
    ("DomainLabels", "History unavailable"): "历史模型不可用",
    ("DomainLabels", "No history"): "暂无有效历史数据",
    ("DomainLabels", "Insufficient"): "历史数据尚不足",
    ("DomainLabels", "Valid"): "历史模型有效",
    ("DomainLabels", "N/A"): "不适用",
    ("DomainLabels", "Win"): "胜",
    ("DomainLabels", "Loss"): "负",
    ("DomainLabels", "Include"): "计入历史",
    ("DomainLabels", "Exclude"): "不计入历史",
    ("Localization", "Language"): "界面语言",
    ("Localization", "Language…"): "界面语言…",
    ("Localization", "Built-in"): "内置",
    ("Localization", "External language pack"): "外部语言包",
    (
        "Localization",
        'The preferred interface language is "简体中文", but its language pack was not found. English will be used for this launch. The preferred language setting will not be changed.',
    ): "首选界面语言为“简体中文”，但当前未找到对应语言包。本次启动将使用 English。首选语言设置不会被更改。",
    (
        "Localization",
        'The "简体中文" language pack could not be loaded. English will be used for this launch. The preferred language setting will not be changed.',
    ): "无法加载“简体中文”语言包。本次启动将使用 English。首选语言设置不会被更改。",
    (
        "Localization",
        "The saved interface language preference is invalid. English will be used for this launch. The settings file will not be changed automatically.",
    ): "保存的界面语言偏好无效。本次启动将使用 English。设置文件不会被自动修改。",
    (
        "Localization",
        "The interface language preference could not be read. English will be used for this launch. The existing settings file will not be modified.",
    ): "无法读取界面语言偏好。本次启动将使用 English。现有设置文件不会被修改。",
    (
        "Localization",
        'The "简体中文" language pack could not be verified, so the new interface language setting was not saved. Make sure the language pack still exists and can be loaded.',
    ): "无法验证“简体中文”语言包，因此未保存新的界面语言设置。请确认语言包仍然存在且可以正常加载。",
    (
        "Localization",
        "The interface language preference could not be saved. The existing preference remains unchanged.",
    ): "无法保存界面语言偏好，现有首选语言设置保持不变。",
    (
        "Localization",
        "The interface language preference was saved. English will take effect the next time the application starts.",
    ): "界面语言偏好已保存。English 将在下次启动时生效。",
    (
        "Localization",
        "The interface language preference was saved. The new interface language will take effect the next time the application starts.",
    ): "界面语言偏好已保存。新的界面语言将在下次启动时生效。",
    (
        "Localization",
        "Simplified Chinese is active, but Qt's standard translations could not be loaded. Some Qt-owned text may remain in English.",
    ): "简体中文界面已启用，但 Qt 标准翻译未能加载。部分 Qt 控件自带文字可能仍显示 English。",
    ("Localization", "Unavailable"): "不可用",
    ("Localization", "Preferred language: %1"): "首选界面语言：%1",
    ("Localization", "Current language: %1"): "当前界面语言：%1",
    ("Localization", "Available"): "可用",
    ("Localization", "Cancel"): "取消",
    ("Localization", "Confirm"): "确认",
    ("Maintenance", "Maintenance / Regimes"): "维护 / 历史阶段",
    ("Maintenance", "Character"): "角色",
    ("Maintenance", "Current regime"): "当前历史阶段",
    ("Maintenance", "Started locally"): "开始时间（本地时间）",
    ("Maintenance", "Reason"): "原因",
    ("Maintenance", "Start New Regime"): "开始新的历史阶段",
    ("Maintenance", "Optional reason"): "原因（可选）",
    ("Maintenance", "Back"): "返回",
    ("Maintenance", "Confirm"): "确认",
    ("Maintenance", "%1 · Current regime %2"): "%1 · 当前历史阶段：%2",
    ("Recovery", "Recover pending round"): "恢复未完成单局",
    ("Recovery", "Continue"): "继续",
    ("Recovery", "Use history"): "参考历史数据",
    ("Recovery", "Do not use history"): "不参考历史数据",
    ("Restore", "pre_restore"): "备份恢复前备份",
    ("Restore", "Emergency Restore"): "紧急备份恢复",
    ("Restore", "Normal Restore"): "常规备份恢复",
    ("Restore", "Reload verified backups"): "重新加载已验证备份",
    (
        "Restore",
        "Replace the live database with the selected verified backup?",
    ): "确认使用所选已验证备份替换当前数据库吗？",
    ("Restore", "Confirm Restore"): "确认备份恢复",
    ("Restore", "Emergency Recovery"): "紧急数据恢复",
    (
        "Restore",
        "Select a verified backup explicitly before requesting Restore.",
    ): "请先明确选择一个已验证备份，再执行备份恢复。",
    ("Restore", "Restore selected backup"): "从所选备份恢复",
    ("Restore", "Close"): "关闭",
    ("Restore", "Unavailable"): "不可用",
    (
        "Round",
        "Candidate edits will be lost. The previously committed pending prediction remains safe.",
    ): "尚未重新计算的修改将丢失；此前已保存的未完成单局保持不变。仍要关闭程序吗？",
    (
        "Round",
        "Post-run choices are not persisted. The pending prediction remains recoverable.",
    ): "当前选择的局后结果和历史计入设置尚未保存；未完成单局仍可在下次启动时恢复。仍要关闭程序吗？",
    ("Round", "Close pending round"): "关闭程序",
    ("Round", "Cancel"): "取消",
    ("Round", "Close Anyway"): "仍要关闭",
    ("Round", "Post-run"): "局后处理",
    ("Round", "Win"): "胜",
    ("Round", "Loss"): "负",
    ("Round", "Include"): "计入历史",
    ("Round", "Exclude"): "不计入历史",
    (
        "Round",
        "Save the selected result and history inclusion?",
    ): "确认保存当前选择的结果和历史计入设置吗？",
    ("Round", "Back"): "返回",
    ("Round", "Confirm Save"): "确认保存",
    ("Round", "Void Pending"): "作废未完成单局",
    (
        "Round",
        "Void this pending round? Its audit record will be preserved.",
    ): "确认作废这个未完成单局吗？该记录及其审计信息会保留，不会被删除。",
    ("Round", "Optional reason"): "原因（可选）",
    ("Round", "Confirm Void"): "确认作废",
    ("Round", "Pre-run inputs"): "局前预测输入",
    ("Round", "Use history"): "参考历史数据",
    ("Round", "Do not use history"): "不参考历史数据",
    ("Round", "Subjective probability"): "主观概率",
    ("Round", "Win odds"): "胜方赔率",
    ("Round", "Lose odds"): "负方赔率",
    ("Round", "Calculate"): "计算",
    ("Round", "Modify"): "修改",
    ("Round", "Round saved successfully."): "单局已保存。",
    ("Round", "New Round"): "新一局",
    ("Round", "Recalculate"): "重新计算",
    ("Round", "Working…"): "处理中…",
    (
        "StartupSafety",
        "Probability Calibration Tool 1.1 — Data Safety",
    ): "Probability Calibration Tool 1.1 — 数据安全",
    ("StartupSafety", "Close"): "关闭",
}

FROZEN_ERRORS = {
    "Odds must be a finite numeric multiplier.": "赔率必须是有限的数值倍率。",
    "Odds must be representable as a finite binary64 value.": "赔率数值超出程序可表示的有限范围。",
    "Odds must be finite and at least 1.": "赔率必须是有限数值，且不得小于 1。",
    "Odds must use unsigned decimal notation.": "赔率必须使用不带正负号的普通十进制格式。",
    "Prediction inputs have not been provided.": "尚未提供预测输入。",
    "Prediction revision is closed after result selection or recovery.": "选择局后结果或进入未完成单局恢复后，不能再修改局前预测。",
    "Another operation is in progress.": "另一项操作正在处理中，请稍候。",
    "Confirmation expired. Confirm the operation again.": "本次确认已失效，请重新确认该操作。",
    "Desktop session has been disposed.": "当前操作会话已失效。",
    "Normal operation is not available.": "当前状态下无法继续正常操作。",
    "Return to a healthy Draft before changing administrative data.": "请先返回正常的草稿状态，再进行维护操作。",
    "Operation is not allowed in the current state.": "当前状态下无法执行此操作。",
    "An explicit boolean choice is required.": "必须明确选择一个选项。",
    "Reason must be text.": "原因必须为文本。",
    "A nonempty correction reason is required.": "必须填写更正原因。",
    "Character ID must be an integer.": "角色 ID 必须为整数。",
    "Choose an active character.": "请选择一个可用角色。",
    "Raw subjective probability must be an integer from 0 to 100.": "输入的主观概率必须是 0 到 100 之间的整数。",
    "A pending round blocks historical correction.": "存在未完成单局，无法进行历史记录更正。",
    "Backup selection expired. Reload and select again.": "备份选择已失效，请重新加载并选择。",
    "No pending round is available for recovery.": "当前没有可恢复的未完成单局。",
    "Finish or void the existing pending round first.": "请先完成或作废当前未完成单局。",
    "Backup accepted; rotation stopped safely with possible over-retention.": "备份已接受；轮换已安全停止，保留的备份数量可能超过设定上限。",
}


def test_official_catalog_metadata_and_complete_active_inventory():
    root, units = load_catalog()
    keys = [(unit.context, unit.source) for unit in units]
    assert root.tag == "TS" and root.get("language") == "zh_CN"
    assert root.get("sourcelanguage") == "en"
    assert len(units) == 225 and {unit.context for unit in units} == CONTEXTS
    assert len(keys) == len(set(keys))
    assert all(unit.translation and unit.translation.strip() == unit.translation for unit in units)
    assert all(unit.translation_type != "unfinished" for unit in units)
    assert not root.findall(".//numerusform")
    assert all(unit.numerus != "yes" and not unit.forms for unit in units)
    assert not root.findall(".//translation[@type='vanished']")
    assert not root.findall(".//translation[@type='obsolete']")


def test_official_keys_and_numerus_equal_fresh_production_extraction(tmp_path):
    executable = Path(sys.executable).parent / "pyside6-lupdate.exe"
    assert executable.is_file() and executable.resolve().is_relative_to((ROOT / ".venv").resolve())
    extracted = tmp_path / "production.ts"
    process = subprocess.run(
        [str(executable), "-extensions", "py", str(ROOT / "src"), "-ts", str(extracted)],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert process.returncode == 0, process.stdout + process.stderr
    production = ET.parse(extracted).getroot()
    production_keys = {
        (context.findtext("name") or "", message.findtext("source") or "")
        for context in production.findall("context")
        for message in context.findall("message")
        if (
            message.find("translation") is None
            or message.find("translation").get("type") not in INACTIVE_TYPES
        )
    }
    official_keys = {(unit.context, unit.source) for unit in load_catalog()[1]}
    assert production_keys == official_keys and len(production_keys) == 225
    assert {context for context, _ in production_keys} == CONTEXTS
    assert not production.findall(".//message[@numerus='yes']")


def test_placeholders_identity_allowlist_and_unicode_integrity():
    payload = TS_PATH.read_bytes()
    text = payload.decode("utf-8")
    assert unicodedata.normalize("NFC", text) == text and "�" not in text
    assert not any(ord(char) < 32 and char not in "\t\n\r" for char in text)
    units = load_catalog()[1]
    for unit in units:
        assert Counter(PLACEHOLDER.findall(unit.source)) == Counter(
            PLACEHOLDER.findall(unit.translation)
        )
        assert "%n" not in unit.translation
    identical = {(unit.context, unit.source) for unit in units if unit.source == unit.translation}
    assert identical == set(IDENTICAL_ALLOWLIST)


def test_frozen_character_matrix_and_high_risk_wording():
    catalog = catalog_map()
    assert catalog[("Characters", "Normal")] == "普通"
    assert catalog[("Characters", "Tainted")] == "堕化"
    for character_id, target in enumerate(CHARACTERS, 1):
        assert catalog[("Characters", CHARACTER_SOURCES[character_id])] == target
    assert len(FROZEN_EXACT) == 135
    assert len(FROZEN_ERRORS) == 23
    assert len(CHARACTERS) == 34
    for key, target in FROZEN_EXACT.items():
        assert catalog[key] == target
    for source, target in FROZEN_ERRORS.items():
        assert catalog[("Errors", source)] == target
    assert all("模式" not in unit.translation for unit in load_catalog()[1])


def test_catalog_has_no_marker_diagnostic_or_test_residue():
    text = TS_PATH.read_text(encoding="utf-8")
    forbidden = (
        "⟦",
        "⟧",
        "TODO",
        "FIXME",
        "Traceback",
        "pytest",
        "fixture",
        "Temporary test translation",
        "Round does not exist.",
        "Round must be pending.",
        "Round must be completed.",
    )
    assert not any(token in text for token in forbidden)
    assert not re.search(r"[A-Za-z]:[/\\]", text)
