# Phase 5 Completion Report

## Files created

15 个 UI 模块、13 个测试/支持文件、3 个交付文件：

```text
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\ui\__init__.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\ui\analysis_panel.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\ui\banners.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\ui\character_matrix.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\ui\close_guard.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\ui\formatting.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\ui\main_window.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\ui\maintenance_page.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\ui\post_run_panel.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\ui\pre_run_panel.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\ui\presentation.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\ui\recovery_page.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\ui\round_page.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\ui\startup_pages.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\ui\widgets.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\application\test_presentation_capabilities.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\ui\__init__.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\ui\conftest.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\ui\helpers.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\ui\test_analysis_safety.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\ui\test_architecture_formatting.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\ui\test_close_guard.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\ui\test_dpi_structure.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\ui\test_maintenance.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\ui\test_pre_run.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\ui\test_recovery_ui.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\ui\test_startup_pages.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\ui\test_workflow_contract.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\outputs\phase5_completion_report.md
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\outputs\phase5_validation_commands.md
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\outputs\phase5_pending_preview.png
```

## Files modified

```text
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\application\workflow.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\pyproject.toml
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\uv.lock
```

## Dependencies

直接依赖增加 `PySide6>=6.8,<7`。执行 `uv sync` 刷新 uv.lock 并安装 PySide6、PySide6-Addons、PySide6-Essentials、shiboken6，均锁定 **6.11.2**。未添加 pytest-qt、主题框架、QML 或 Designer 文件。

## Schema

Schema v1 unchanged

SPEC 与 schema.py 的 SHA-256 均与实施前一致；Core、Golden values、Persistence、Phase 4 和所有既有测试文件未修改。

## Accepted-phase changes

唯一 Phase 3 改动是只读 `Workflow.can_modify_prediction`：仅组合既有 PENDING_LOCKED 状态与既有 Audit Lock，公开 Modify 是否允许。不提供 setter，不暴露私有字段，不改变任何业务转换、锁定或重置语义。新增 4 项能力回归测试。

其余 ui/ 外新增内容仅是测试及交付文件；既有文件另改 pyproject.toml、uv.lock。

## UI architecture

- `main_window`：单窗口、页面导航、集中渲染、调用公共 Workflow 与注入接口。
- `round_page`：常驻 pre-run / analysis / post-run 布局及状态投影。
- `character_matrix`、`pre_run_panel`、`post_run_panel`：选择、原始输入、保存/作废确认。
- `analysis_panel`：两条独立分析线与敏感文本清除。
- `maintenance_page`、`recovery_page`、`startup_pages`：维护、恢复、错误及紧急恢复展示。
- `banners`、`close_guard`：单条横幅、关闭确认。
- `formatting`、`presentation`、`widgets`：展示格式、窄 DTO/注入接口、基础控件。

UI 不执行 SQL，不实例化 Repository/UoW，不导入 Core/SciPy/math，不复算模型或自行转换业务状态。无生产 bootstrap/__main__ 接线。

## Main Window

一个 QMainWindow；左侧稳定 Character Pane，右侧导航、单条 Banner 和 QStackedWidget。页面为 Round、Maintenance、Recovery、Recovery Error、Startup Safety、Emergency Recovery。RoundPage 始终复用，不为 Draft/Pending/Edit 复制界面。

## Character Matrix

恰好 **34 个按钮、17×2 配对行**。稳定 ID 1–17 对应 Normal，18–34 对应 Tainted；显示名从注入的权威维护视图提取，不复制角色名单。最后一对为 Jacob & Esau / Tainted Jacob；Qt 的 & 转义已处理。

首次无选择，QButtonGroup 保持互斥。使用 QGridLayout、自然 sizeHint 和稳定侧栏宽度，无绝对定位或常规滚动条。

## Pre-run

角色及 Use history / Do not use history 首次均无默认选择。概率和两项赔率使用 QLineEdit，概率旁固定 %。无强校验器、自动 clamp、赔率 locale 转换或科学计数解析。

概率仅做命令传输所需的整数转换；范围与有效性由 Application/Core 决定，无法转换的文本原样送交 Application 返回结构化错误。输入框保留原始文本，赔率 2.00 不改为 2；0/100 保持原样，分析注明 1%/99% 用于计算。

Enter/Return 不触发 Calculate 或 Recalculate；对应两种状态、三个字段均有 QTest。错误按 InputValidationError.field 显示在字段旁，不解析异常消息定位字段。

## Workflow rendering

用户操作调用公共 Workflow 后统一 `render_from_workflow()`。启用、只读、可见性、Modify、确认模式和 post-run 选择均源自 Workflow 公共状态/能力/视图。

UI 只保存会话偏好、页面选择、临时确认显示及控件同步缓存，不维护第二套 pending/exposure/compromise/Audit Lock 状态机。被 Workflow 拒绝的 Qt 选择会重绘回权威值。同步操作不使用 QThread 或 processEvents 制造重入。

## Modify / Recalculate

Modify 调用 Workflow.modify；编辑时保留上次成功提交的分析，并明确标注“候选编辑尚未反映”。输入时不计算。

Recalculate 继续调用 Workflow.calculate，由 Workflow 决定 Calculate/Recalculate。失败时保留 PENDING_EDIT、候选原文和原提交分析；测试确认数据库不变。

## Analysis

Subjective 在上，Historical 在下，两个独立卡片。展示已有概率、区间、EV、S、阈值、后验概率及关系枚举，不合成概率、不提供推荐方向或 Stake。

百分比、紧凑带符号 EV、赔率及本地时间格式集中管理；不改变底层存储和数学。

## Historical anti-leakage

- HIDDEN：仅说明未请求历史。
- NO_HISTORY：仅说明无合格历史。
- INSUFFICIENT：仅说明不足以给出数字参考，无 n、缺口或 Gate 进度。
- VISIBLE：只填入已有安全 VisibleHistoryView 的数字。

每次渲染先清除全部历史值和字段标题，再按安全状态填入。隐藏数值文本是 **CLEARED，不只是 hidden**。测试递归检查可见/隐藏控件，包含内部历史 VALID、公开视图 HIDDEN 的真实数据库场景。

## New-Draft anti-leakage

Completed Notice → New Round 和 Void → Draft 均清空概率、赔率、两张分析卡、result/include、错误和过期横幅；非当前页面的 Recovery 分析也清空。

仅保留用户本会话明确选择的角色/历史偏好；重建窗口不保留，Recovery 加载的值不会自动变成新会话偏好。

## Audit Lock UI

新计算 pending 可 Modify；选择结果后不可 Modify；Confirm Save → Back 仍不可 Modify；Recovery Continue 立即不可 Modify。所有判断使用新增公共只读能力，UI 不检查私有锁字段。

## Post-run / Confirm Save

Win/Loss 与 Include/Exclude 两组均互斥、初始无选择。双方齐备后由 Workflow 进入页内确认，展示 Back / Confirm Save。Back 保留选择并允许调整，不重新开放预测编辑。

保存成功展示 Completed Notice / New Round。Void Pending 有独立页内确认、可选原因、Cancel / Confirm Void；不删除记录，也不与 Close 混同。

## Close behavior

- DRAFT：直接接受。
- PENDING_LOCKED 且无 post-run 选择：直接接受，pending 保留。
- PENDING_EDIT：确认放弃候选编辑，说明原提交预测安全。
- PENDING_LOCKED 有 result/include，或 CONFIRM_SAVE：确认未保存选择会丢失。
- CALCULATING / COMPLETING：忽略关闭。
- RECOVERY、RECOVERY_ERROR、startup safety、COMPLETED_NOTICE：无独立活动操作时可关闭。
- 注入的独立恢复请求活动期间：忽略关闭。

关闭事件不保存、不作废、不写数据库。

## Banners / errors

普通输入错误仅字段内显示；业务错误、信息和警告共用一个可关闭 Banner，不无限叠加。备份警告文案保留“主事务已保存”的含义。

未预期异常使用 Phase 4 ErrorPresentation：日志包含同一 Error ID 和 traceback；UI 仅显示安全消息与 ID，不暴露 SQL、路径或异常堆栈。

## Maintenance

准确列为：Character、Current regime、Started locally、Reason、Included samples。34 行，禁用排序；样本数不显示为 Gate 进度。

无 wins、losses、win rate、Jeffreys、历史概率/区间/EV 或方向性历史列表。Start New Regime 必须显式选行和点击，再页内确认；pending 时不可用，RegimeService 仍是最终业务守卫。

## Recovery UI

既有 RecoveryView 仅含状态与 ID，因此使用窄 `RecoveryPresentation` 组合它与已有 LockedAnalysisView，不修改 Phase 3 DTO。页面只接收安全视图；未查询原始 SnapshotRecord 或 Persistence。

Inspect 不自动推进 Workflow；Continue 调用已有 continue_recovery，恢复同一 ID 和已提交分析，不重算，不默认 result/include。四种历史展示状态及切页清除均有契约测试。

## Startup safety UI

可展示 READY_DRAFT、READY_RECOVERY、RECOVERY_ERROR、EMERGENCY_RECOVERY、UNSUPPORTED_NEWER_SCHEMA、ALREADY_RUNNING、DATA_SAFETY_ERROR。

安全状态禁止普通导航；多个 pending 不列出供选择、不修复。较新 Schema 无 Force Open/Downgrade/Ignore。所有输入来自 ReliabilityResult，没有真实 StartupService/RuntimeContext 生产接线。

## Emergency Restore skeleton

只展示注入的候选 DTO，类别、本地时间及可选 Safety 原因。初始选择为空，焦点置于 Close，避免 Qt 自动首行焦点引发误选；只有显式选择有效候选且注入请求接口后才能 Restore。

无效候选不可选择。UI 不扫描目录、不调用 BackupService、不执行文件替换；测试仅记录抽象请求，未进行 Phase 6 Restore 接线。

## Tests

`uv run pytest` → **860 passed in 36.82s**。

- passed: 860
- failed: 0
- skipped: 0
- xfailed: 0
- xpassed: 0

`uv run pytest tests/ui --collect-only -q` → **90 collected**。

`uv run pytest tests/ui -q` → **90 passed**。

`uv run pytest tests/integration/application/test_presentation_capabilities.py -q` → **4 passed**。

766 项原有基线 + 90 UI + 4 能力测试 = 860。使用 pytest + PySide6 QTest，不使用 pytest-qt。所有数据库和运行目录为临时位置；Qt 离屏 fixture 显式加载 Windows Segoe UI，避免无字体导致的虚假布局验证。

## Golden UI tests

以下全部 PASS：

- First Run
- Valid Calculate
- HIDDEN leakage
- NO_HISTORY leakage
- INSUFFICIENT leakage
- stale-history clearing
- completed reset
- Modify behavior
- Audit Lock
- post-run choices
- Close Guard
- Maintenance leakage
- Recovery safe render
- DPI structural smoke
- real Workflow contract smoke

真实 Workflow UI 测试使用临时 SQLite 和原 Phase 1/2/3 服务，覆盖选择、输入、Calculate、Modify、Recalculate；未组合 Phase 4 生产启动/备份链。

## DPI

自动结构测试在 1100×800、1250×900 逻辑尺寸通过：34 个按钮仍可访问、几何有效、确认按钮在窗口内、历史变化不移动左矩阵。已检查使用真实字体的离屏截图 `phase5_pending_preview.png`。

实际 Windows 125%：未执行。
实际 Windows 150%：未执行。

**manual DPI acceptance pending**。离屏结构测试和截图不能替代实际显示缩放下的人工发布验收。

## Phase 1 regression

`uv run pytest tests/unit/core -q` → **213 passed**。

## Phase 2 regression

```text
uv run pytest tests/integration/persistence --ignore=tests/integration/persistence/test_migrations_phase4.py -q
```

原有基线 **293 passed**。仅排除新增 Phase 4 文件以单独统计；完整测试包含全部文件。

## Phase 3 regression

```text
uv run pytest tests/integration/application --ignore=tests/integration/application/reliability --ignore=tests/integration/application/test_presentation_capabilities.py -q
```

原有基线 **153 passed**。既有测试未修改。

## Phase 4 regression

```text
uv run pytest tests/integration/infrastructure tests/integration/application/reliability tests/integration/persistence/test_migrations_phase4.py -q
```

**107 passed**，包括 Restore runtime-state 修正测试。Backup、Migration、Startup、Stats、Restore 和 runtime locking 未改。

## Ruff

`uv run ruff check .` → **All checks passed!**

`uv run ruff format --check .` → **141 files already formatted**。

退出码均为 0。

## SPEC deviations

none

## SPEC concerns

none

## Incomplete work

代码实现：none。

人工发布验收：manual DPI acceptance pending（Windows 125% / 150%）。

## Known risks

- 实际 Windows DPI 人工验收尚未完成，是最终发布门槛，不能据此阶段宣称可发布。
- 本阶段按要求未提供生产启动入口、真实恢复库存/执行接线、Recent 触发器或打包测试。
- 同一环境此前拒绝了 source/test 缓存删除命令；未绕过策略或重试已被禁止的删除方式。生成缓存仍由现有 .gitignore 忽略，没有删除源文件。
- 离屏平台不发现系统字体，测试显式加载 Segoe UI；生产 Qt Windows 平台字体行为仍需人工确认。

## Phase 6 work

none

Phase 5 complete. No Phase 6 implementation was started.

