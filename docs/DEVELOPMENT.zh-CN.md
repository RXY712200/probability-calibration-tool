# Probability Calibration Tool 开发、构建与发布指南

本文档说明 Probability Calibration Tool 当前源码仓库的开发环境、测试、本地化编译、Windows 打包、Packaged Smoke、Release 验证与正式发布流程。

本文主要面向：

- 后续维护源码的开发者；
- 修改数学模型、Workflow、数据库或 UI 的维护者；
- 维护简体中文语言包的人；
- 制作正式 Windows Release 的维护者。

当前产品技术行为请参阅 [技术参考](TECHNICAL_REFERENCE.zh-CN.md)。

普通用户操作请参阅 [用户指南](USER_GUIDE.zh-CN.md)。

本地化架构与语言包规则请参阅 [本地化维护指南](LOCALIZATION.zh-CN.md)。

---

## 1. 当前开发基线

当前项目要求：

```text
Python >= 3.13, < 3.14
```

运行时主要依赖：

```text
PySide6
SciPy
```

开发依赖主要包括：

```text
PyInstaller
pytest
Ruff
```

仓库同时维护：

```text
pyproject.toml
uv.lock
```

正式开发和 Release 应优先使用锁定环境，而不是临时安装任意最新依赖。

---

## 2. 当前正式平台

当前正式桌面 Release 目标：

```text
Windows x64
```

目前主要测试环境：

```text
Windows 11 x64
```

当前项目不在本文档中承诺：

```text
Linux
macOS
Windows ARM
```

具有相同等级的正式发行验证。

---

## 3. 仓库主要结构

当前主要目录：

```text
src\
tests\
tools\
packaging\
translations\
docs\
```

以及：

```text
pyproject.toml
uv.lock
SPEC_1.0.md
README.md
LICENSE
THIRD_PARTY_NOTICES.md
```

各目录职责：

```text
src
    正式应用源码

tests
    自动化测试

tools
    开发、QA、Release 辅助工具

packaging
    PyInstaller 构建入口与 spec

translations
    正式翻译源

docs
    当前维护文档

SPEC_1.0.md
    1.0 历史设计与验收基线
```

---

## 4. 从干净工作树开始

正式开发或 Release 前先检查：

```powershell
git status
```

确认：

```text
当前 branch
未提交修改
未跟踪文件
```

都符合预期。

不要在混有：

```text
临时数据库
旧 Build
旧 Release ZIP
人工 QA 文件
未知源码修改
```

的工作树上直接制作正式 Release。

---

## 5. 历史 Tag

当前历史正式 tag 包括：

```text
v1.0
v1.1
```

这些 tag 是已经发布版本的历史快照。

可以用于：

```text
审计
比较
复现历史版本
```

但不应为了后续文档或许可证整理而移动历史 tag。

新的正式 Release 应创建新的 commit 和 tag。

---

## 6. 建立锁定开发环境

仓库根目录执行：

```powershell
uv sync --locked --all-groups
```

目标：

```text
使用 uv.lock
安装 Runtime dependencies
安装 Development dependencies
```

正式 Release 不建议使用：

```text
pip install 任意最新版依赖
```

后再声称与锁定构建环境等价。

---

## 7. 为什么要尊重 `uv.lock`

`pyproject.toml` 定义：

```text
允许的依赖范围
```

`uv.lock` 定义：

```text
当前锁定解析结果
```

因此依赖升级应该作为明确的开发变化：

```text
更新依赖
        ↓
更新 lock
        ↓
完整测试
        ↓
重新 Package QA
```

不能在 Release 构建机上静默升级依赖。

---

## 8. 运行源码

Production Python 入口最终进入：

```text
probability_calibration_tool.bootstrap
```

开发时从仓库根目录运行：

```powershell
uv run python -m probability_calibration_tool
```

这会经过与正式应用一致的：

```text
Localization
StartupService
Runtime Lock
Database Safety
DesktopHost
Qt Event Loop
```

---

## 9. 不要直接运行 UI 文件作为正式入口

例如不建议长期使用：

```powershell
python src\probability_calibration_tool\ui\main_window.py
```

来代表完整产品。

单独运行 UI 文件可能绕过：

```text
Runtime
Startup validation
Localization initialization
Session routing
Restore safety
```

所以正式开发验证应使用 production entrypoint。

---

## 10. 开发数据必须与真实用户数据隔离

真实默认用户数据：

```text
%LOCALAPPDATA%\ProbabilityCalibrationTool\
```

开发以下测试时不得直接操作真实用户目录：

```text
Restore
Emergency Restore
Corrupt database
Multiple pending
Missing Snapshot
Invalid Stats
Language Pack failure
Settings failure
```

必须使用：

```text
temporary directory
isolated LOCALAPPDATA
test fixture
```

---

## 11. 不要在真实数据库上做 Fault Injection

以下操作只允许在受控测试环境：

```text
删除 Snapshot
损坏 probability.db
制造多个 pending
破坏 Stats
删除 Index
修改 Schema Version
制造 Sidecar
删除语言包
破坏 settings.ini
```

不要使用个人实际数据库作为故障实验对象。

---

## 12. 完整自动化测试

正式基础测试：

```powershell
uv run pytest
```

v1.1 Release 的历史最终结果曾为：

```text
1340 passed
```

这个数字是：

```text
v1.1 历史 Release evidence
```

不是未来版本必须永远保持的固定测试总数。

永久要求是：

> 当前正式 test suite 必须全部通过。

---

## 13. 测试失败时先判断合同是否变化

特别是以下测试失败时：

```text
Golden math tests
Transaction tests
Recovery tests
Correction tests
Restore tests
Anti-Anchoring tests
Architecture tests
```

不能第一反应只是：

```text
修改 expected
```

应先判断：

```text
Implementation Bug
```

还是：

```text
Intentional Contract Change
```

如果是合同变化，还需要同步：

```text
Model / Schema Version
Migration
Technical Reference
User Guide
Localization
Release Notes
```

---

## 14. Ruff

当前 Ruff 目标版本：

```text
Python 3.13
```

正式检查：

```powershell
uv run ruff check .
```

Release 前应做到：

```text
Ruff PASS
```

除非有明确记录并经过审查的例外。

---

## 15. Ruff 不替代测试

即使：

```text
Ruff PASS
```

也不能证明：

```text
数学正确
事务正确
Recovery 正确
Restore 安全
```

因此：

```text
Ruff PASS
≠
Release PASS
```

---

## 16. 简体中文翻译源

正式翻译源：

```text
translations\probability_calibration_tool_zh_CN.ts
```

它是：

```text
zh_CN translation authority
```

编译后的 `.qm` 不是长期维护源。

---

## 17. 编译 `.qm`

当前 PySide6 环境提供：

```text
pyside6-lrelease
```

建议使用严格模式：

```powershell
uv run pyside6-lrelease `
  translations\probability_calibration_tool_zh_CN.ts `
  -qm probability_calibration_tool_zh_CN.qm `
  -fail-on-unfinished `
  -fail-on-invalid
```

目标：

```text
unfinished translation
→ build failure

invalid translation
→ build failure
```

---

## 18. 当前翻译 QA 基线

v1.1 的历史翻译基线：

```text
225 active translations
12 contexts
0 unfinished
```

这只是 v1.1 的历史冻结结果。

以后新增 UI string 后：

```text
translation count
TS SHA-256
context count
```

都可能合理变化。

不能为了保持旧数字而阻止正常本地化演进。

---

## 19. Historical Localization QA Helpers

仓库中存在一些为 v1.1 Localization 工作流建立的工具和证据。

例如：

```text
tools\localization_step5_inventory.py
tools\localization_step7_prepare.py
```

以及历史：

```text
outputs\localization_step...
```

这些工具中的部分 frozen hash、translation count 和 scenario 具有：

```text
v1.1-specific QA
```

性质。

它们不能被解释成：

> 未来每个 Release 永远不允许变化的通用构建协议。

---

## 20. Translation Inventory 不是第二 Authority

如果工具从：

```text
translations\probability_calibration_tool_zh_CN.ts
```

生成：

```text
inventory
report
evidence
```

真正翻译 authority 仍是：

```text
官方 TS
```

生成报告只属于：

```text
QA evidence
```

不能与 TS 并列成为第二份翻译真相来源。

---

## 21. Manual Localization QA

修改翻译或 UI 后，还应人工检查：

```text
Main Window
Analysis
Maintenance
Correction
Restore
Recovery
Safety Window
Language Dialog
Error / Warning
High DPI / Scaling
```

重点观察：

```text
文字截断
按钮宽度
表格宽度
换行
Modal 尺寸
中英混杂
```

自动化测试无法完全替代真实视觉 QA。

---

## 22. PyInstaller 正式入口

当前 packaging entry：

```text
packaging\pyinstaller_entry.py
```

其职责是进入：

```text
probability_calibration_tool.bootstrap
```

而不是建立一套专门给 binary 的第二启动逻辑。

---

## 23. 正式 PyInstaller Spec

正式配置：

```text
packaging\ProbabilityCalibrationTool.spec
```

当前采用：

```text
Analysis
PYZ
EXE
COLLECT
```

并构建：

```text
console = False
```

的 Windows GUI application。

---

## 24. Build 命令

从仓库根目录执行：

```powershell
uv run pyinstaller --noconfirm --clean packaging\ProbabilityCalibrationTool.spec
```

正常输出：

```text
dist\ProbabilityCalibrationTool\
```

主程序：

```text
dist\ProbabilityCalibrationTool\ProbabilityCalibrationTool.exe
```

---

## 25. 当前是 `onedir`

正式打包模式：

```text
onedir
```

不是：

```text
onefile
```

所以：

```text
ProbabilityCalibrationTool.exe
_internal\
```

共同构成正式 runtime。

用户不能只复制：

```text
ProbabilityCalibrationTool.exe
```

然后删除 `_internal`。

---

## 26. `_internal` 是 Runtime 的组成部分

其中可能包含：

```text
Python Runtime
Qt
PySide6 Plugins
SciPy Native Modules
SQLite Runtime
其它 Native Dependencies
```

它不是：

```text
Build Cache
```

也不是用户可以随意删除的目录。

---

## 27. Build 时限制 Native Discovery PATH

正式 spec 会限制构建阶段的 PATH，避免开发机上无关 DLL 污染 Qt / native dependency discovery。

这一限制源于实际开发环境中外部 native library 对 Qt dependency discovery 的干扰风险。

除非重新完成：

```text
native dependency closure
packaged smoke
Windows manual QA
```

否则不要随意移除。

---

## 28. 不使用 `collect_all` 粗暴打包

当前正式 spec 不依赖：

```text
collect_all
```

把整个开发环境无选择塞入 artifact。

如果未来出现缺 module：

```text
先查 PyInstaller hook
hidden import
native dependency
实际 import path
```

而不是直接扩大整个 package。

---

## 29. App 中文语言包不进入 Main Build

当前正式合同：

```text
Main Package
→ English built-in
```

应用专属：

```text
probability_calibration_tool_zh_CN.qm
```

不应打进 Main ZIP。

简体中文使用独立 Language Pack Release Asset。

---

## 30. Qt Framework Translation 不等于 App Pack

Main package 的：

```text
_internal\PySide6\translations\
```

中可能包含 Qt 自身 translation catalogs。

这不表示：

```text
Probability Calibration Tool zh_CN Application Pack
```

已被内置。

二者必须区分。

---

## 31. Artifact Audit

正式 Build 后先验证：

```powershell
uv run python tools\release_verify.py `
  --artifact dist\ProbabilityCalibrationTool
```

Artifact Audit 应检查：

```text
Main EXE
PE Architecture
GUI Subsystem
Python Runtime
Qt Runtime
SciPy Runtime
SQLite Runtime
项目文件泄漏
用户数据泄漏
Symlink
SHA-256 Inventory
```

---

## 32. Windows Binary Contract

当前正式 artifact 应为：

```text
AMD64
PE32+
Windows GUI subsystem
```

不能把：

```text
x86 build
Console build
```

误当成正式 Windows x64 Release。

---

## 33. 关键 Runtime Component

正式 audit 至少应确认类似：

```text
ProbabilityCalibrationTool.exe
python313.dll
qwindows.dll
Qt6Widgets.dll
SciPy native components
sqlite3.dll
```

等必要 Runtime 存在。

因此：

```text
EXE 文件生成成功
```

不代表：

```text
Artifact 完整
```

---

## 34. Release Artifact 不得包含用户数据库

Main artifact 禁止包含：

```text
probability.db
*.db
*.sqlite
*.sqlite3
```

以及任何开发或 QA database。

正式应用包绝不能携带维护者自己的真实业务数据。

---

## 35. Release Artifact 不得包含用户日志与 Lock

同样不得包含：

```text
app.log
application.lock
settings.ini
```

等用户运行时数据。

---

## 36. Release Artifact 不应泄露仓库

正式 runtime artifact 不应包含：

```text
src
tests
tools
outputs
.pytest_cache
.ruff_cache
.venv
pyproject.toml
uv.lock
```

等源码仓库或开发环境内容。

---

## 37. License Files 是合法发行文档

正式 Release 可以并建议包含：

```text
LICENSE
THIRD_PARTY_NOTICES.md
licenses\
```

这些不是：

```text
Repository Leakage
```

而是发行许可证与第三方 notices。

具体第三方材料必须根据当前最终 artifact 核对。

---

## 38. `outputs` 不属于 Runtime

历史 `outputs` 中的：

```text
Build Log
Validation Report
Packaged Smoke Evidence
Manual QA
Translation Inventory
```

属于：

```text
开发 / QA Evidence
```

不是应用 Runtime Dependency。

因此不能进入用户 Main ZIP。

---

## 39. Packaged Smoke

Artifact Audit 后必须真正运行：

```text
打包后的 EXE
```

而不是只测试 Python source。

当前工具：

```text
tools\packaged_smoke.py
```

用于测试 packaged application 的真实独立运行。

---

## 40. 推荐 Packaged Smoke

例如：

```powershell
uv run python tools\packaged_smoke.py `
  --artifact dist\ProbabilityCalibrationTool `
  --evidence outputs\packaged_smoke.json
```

正式 external exercise 应使用：

```text
仓库外临时目录
```

而不是让 binary 继续依赖 repository。

---

## 41. Smoke 必须隔离环境变量

Packaged Smoke 应尽量移除：

```text
PYTHON*
VIRTUAL_ENV
QT_*
PYSIDE*
PYINSTALLER*
_PYI*
```

等开发环境影响。

目的是证明：

> 最终 EXE 使用自己的 package，而不是偷偷依赖 `.venv` 或开发机 Python 环境。

---

## 42. Smoke 使用隔离 `LOCALAPPDATA`

Packaged Smoke 必须把：

```text
LOCALAPPDATA
```

指向测试目录。

然后验证应用自行建立：

```text
ProbabilityCalibrationTool\data\probability.db
ProbabilityCalibrationTool\runtime\application.lock
ProbabilityCalibrationTool\backups\
```

而不是访问维护者真实用户数据。

---

## 43. Smoke 使用无关 Working Directory

应用应从：

```text
unrelated working directory
```

启动。

测试结束后，该目录不应出现：

```text
probability.db
settings.ini
app.log
backup
lock
```

等用户数据。

这验证应用不会把数据错误写到：

```text
Current Working Directory
```

---

## 44. Smoke 验证 Runtime Module 来源

正式 QA 应确认关键加载模块来自：

```text
Packaged Artifact
```

而不是：

```text
Repository
.venv
其它 Python installation
```

尤其包括：

```text
Qt
Python Runtime
SQLite
SciPy Native Modules
```

---

## 45. Single-Instance QA

自动 Packaged Smoke 可以观察：

```text
第一实例持续运行
第二实例不能进入完整正常主窗口
single-instance notification path 出现
```

但真实：

```text
第二实例提示框
关闭操作
用户交互
```

仍应保留人工 Windows 验收。

---

## 46. Database Release Verification

数据库 verifier 应使用：

```text
read-only
query-only
```

方式检查：

```text
integrity
foreign keys
schema version
round count
snapshot count
pending count
completed count
```

验证工具不应在检查过程中自动：

```text
Migration
Repair
Stats rebuild
```

---

## 47. Verification Tool 不应修改被检查对象

Release verification 的原则：

> 检查输入，而不是边检查边修复输入。

如果 verifier 发现：

```text
Stats mismatch
Schema mismatch
Corruption
```

应该报告失败。

不能为了让 Release Gate 变绿，偷偷修改被验证数据库或 artifact。

---

## 48. Main Release ZIP

正式 Main Asset 命名：

```text
ProbabilityCalibrationTool-<version>-Windows-x64.zip
```

例如：

```text
ProbabilityCalibrationTool-1.1-Windows-x64.zip
```

---

## 49. Main ZIP 必须保持 onedir 结构

典型结构：

```text
ProbabilityCalibrationTool\
    ProbabilityCalibrationTool.exe
    _internal\
    LICENSE
    THIRD_PARTY_NOTICES.md
    licenses\
```

不能为了让 ZIP 看起来简单而只留下：

```text
ProbabilityCalibrationTool.exe
```

---

## 50. Language Pack ZIP

简体中文 Asset：

```text
ProbabilityCalibrationTool-LanguagePack-zh_CN-<version>.zip
```

当前推荐只包含：

```text
probability_calibration_tool_zh_CN.qm
```

用户自行安装到：

```text
%LOCALAPPDATA%\ProbabilityCalibrationTool\languages\
```

---

## 51. Main ZIP 与 Language Pack 分别验证

Main ZIP：

```text
Runtime 完整
无 App zh_CN pack
无用户数据
无仓库泄漏
```

Language Pack ZIP：

```text
只有 canonical QM
QTranslator 可加载
locale = zh_CN
catalog nonempty
sentinel valid
translation QA passed
```

一个通过不能替代另一个。

---

## 52. Release SHA-256

最终 ZIP 创建后计算：

```powershell
Get-FileHash `
  outputs\release\ProbabilityCalibrationTool-<version>-Windows-x64.zip `
  -Algorithm SHA256
```

Language Pack ZIP 同样计算。

Hash 必须针对：

> 最终真正上传 GitHub Release 的 exact bytes。

---

## 53. Hash 必须最后计算

正确顺序：

```text
最终内容
        ↓
最终 ZIP
        ↓
SHA-256
        ↓
上传相同 ZIP
```

如果 ZIP 内容在 hash 后又变化：

```text
必须重新计算 hash
```

---

## 54. Release-Specific Hash 不进入通用文档

某个版本的：

```text
ZIP SHA-256
QM SHA-256
```

应记录在：

```text
GitHub Release Notes
Release Manifest
Release Evidence
```

不要写死进：

```text
README
User Guide
Development Guide
Localization Guide
```

---

## 55. Version Update

当前项目 Product Version 存在于：

```text
pyproject.toml
```

同时 UI title 等位置可能存在：

```text
Probability Calibration Tool 1.1
```

未来更新版本前必须全仓检查：

```text
当前版本引用
历史版本引用
```

不能只改 `pyproject.toml`。

---

## 56. 不要机械替换旧版本号

例如搜索：

```powershell
git grep "1.1"
```

后不能直接：

```text
全部替换成 1.2
```

因为命中可能属于：

```text
当前 Window Title
历史 Release
历史 QA Report
SPEC 记录
v1.1 Tag 说明
```

必须判断语义。

---

## 57. `SPEC_1.0.md` 保持历史

新 Release 不应把：

```text
SPEC_1.0.md
```

重写成：

```text
当前最新版 SPEC
```

它继续表示：

> 1.0 历史设计与验收基线。

当前行为由：

```text
TECHNICAL_REFERENCE.zh-CN.md
```

维护。

---

## 58. Product Version 与 Model Version 分离

发布：

```text
Product 1.2
```

不自动意味着：

```text
Subjective Model = 2
Historical Model = 2
Schema = 2
```

只有实际合同变化才更新对应内部 version。

---

## 59. Product Version 与 Schema Version 分离

如果新 Release：

```text
只修改 UI / Documentation / Localization
```

SQLite Schema 完全不变：

```text
PRAGMA user_version
```

可以继续保持原版本。

不要为了数字整齐无意义增加 Schema Version。

---

## 60. Release 前推荐顺序

正式 Release 推荐：

```text
确认 Source / Version / Docs
        ↓
uv locked environment
        ↓
Ruff
        ↓
Full pytest
        ↓
Localization compile + QA
        ↓
PyInstaller clean build
        ↓
Artifact audit
        ↓
Packaged smoke
        ↓
Manual Windows acceptance
        ↓
Main ZIP
        ↓
Language Pack ZIP
        ↓
Final SHA-256
        ↓
Final content inspection
        ↓
Release Commit
        ↓
Annotated Tag
        ↓
Push
        ↓
GitHub Release
```

核心原则：

> 不要先打正式 Tag，再开始验证最终 Artifact。

---

## 61. Release Commit

正式 Release commit 应包含：

```text
本次真正源码
对应 Tests
Current Docs
Translation Source
Packaging Config
```

最终 Binary 应来自：

```text
该 commit 对应的源码
```

不要：

```text
先打 Tag
→ 后来发现 Build Bug
→ 手工修 dist
```

---

## 62. Annotated Tag

正式版本建议：

```powershell
git tag -a v<version> -m "Probability Calibration Tool <version>"
```

Tag 必须指向：

```text
最终 Release Commit
```

---

## 63. Push

确认 commit 与 tag：

```powershell
git push
git push origin v<version>
```

具体 branch policy 可随未来维护方式调整。

本文不强制 Git Flow。

---

## 64. 已发布 Tag 不重写

正式公开：

```text
v1.2
```

之后不应：

```text
移动 tag
删除后重新指向另一 commit
```

修复应发布：

```text
v1.2.1
v1.3
```

等新版本。

---

## 65. GitHub Release

正式 GitHub Release：

```text
绑定对应 Tag
```

上传：

```text
ProbabilityCalibrationTool-<version>-Windows-x64.zip

ProbabilityCalibrationTool-LanguagePack-zh_CN-<version>.zip
```

普通用户不应依赖 GitHub 自动生成：

```text
Source code (zip)
Source code (tar.gz)
```

运行应用。

---

## 66. Release Notes

未来 Release Notes 推荐只聚焦：

```text
主要新增
主要修复
Breaking / Compatibility Notes
下载哪个 Asset
SHA-256
必要的 Upgrade Note
```

长期操作教程应链接：

```text
README
User Guide
```

而不是在每个 Release 重复整份用户手册。

---

## 67. v1.1 Release 保持历史不动

v1.1 发布时完整文档体系尚未建立，因此当时 Release Notes 承担了更多：

```text
下载
运行
语言包
```

说明。

现在不需要为了新文档体系：

```text
移动 v1.1 tag
重新打 v1.1 binary
重新计算其历史 hash
```

未来 Release 使用新规范即可。

---

## 68. Release Notes 可以使用中文

当前仓库文档已经决定：

```text
中文为主
不维护整套英文文档副本
```

因此未来 GitHub Release Notes 可以直接使用中文。

这与应用源码继续使用：

```text
English source strings
```

并不冲突。

---

## 69. Asset Filename 保持稳定 ASCII

即使 Release Notes 使用中文，正式 Asset 名仍建议：

```text
ProbabilityCalibrationTool-<version>-Windows-x64.zip
ProbabilityCalibrationTool-LanguagePack-zh_CN-<version>.zip
```

不要改成容易影响脚本和版本识别的任意中文文件名。

---

## 70. 不直接修改 `dist` 作为正式修复

如果打包后发现 Bug：

错误流程：

```text
手工修改 dist
        ↓
重新 ZIP
```

正确流程：

```text
修 Source
        ↓
Test
        ↓
Rebuild
        ↓
Re-Audit
        ↓
Re-Smoke
        ↓
新 ZIP
```

否则 Git Source 与最终 Binary 失去可追溯性。

---

## 71. ZIP 变化后必须重新验证

如果正式 ZIP 创建后又：

```text
加入 DLL
删除文件
加入 LICENSE
加入 notices
加入语言包
```

之前的：

```text
Artifact Audit
Packaged Smoke
SHA-256
```

已不再完整覆盖最终 bytes。

内容改变后：

```text
重新验证
重新 hash
```

---

## 72. Evidence 与 Artifact 分离

Release QA 可以生成：

```text
JSON
Log
Inventory
Screenshot
Manual Checklist
```

但这些 evidence 不属于用户 Runtime Package。

不要把：

```text
outputs\
```

塞进：

```text
ProbabilityCalibrationTool-<version>-Windows-x64.zip
```

---

## 73. Manual Windows Acceptance

正式 Release 至少人工确认：

```text
EXE 正常启动

Window Title / Version 正确

默认 English

主要 Round Workflow 可操作

Language Dialog 正常

外部 zh_CN QM 安装后重启变中文

UI 无明显文字截断

关闭行为正常

Single-instance 提示可正常退出
```

---

## 74. Manual QA 也使用隔离数据

即使是人工测试：

```text
Restore
Emergency Restore
Corruption
Multiple Pending
```

仍应使用：

```text
isolated LOCALAPPDATA
```

避免真实个人数据被 QA 操作污染。

---

## 75. Release Failure 不硬过 Gate

例如：

```text
pytest failed
Artifact 引用了 .venv
Main ZIP 包含 test DB
QM preflight failed
Native DLL missing
```

不能只因为：

```text
“我双击看起来能打开”
```

就忽略。

应先确认失败是：

```text
Test Problem
```

还是：

```text
Actual Product / Artifact Problem
```

---

## 76. Source、Runtime 与 Language Asset 是三种不同产物

### Source Repository

```text
src
tests
tools
packaging
translations
docs
pyproject.toml
uv.lock
```

### Windows Runtime Artifact

```text
ProbabilityCalibrationTool.exe
_internal
license material
```

### Language Pack

```text
probability_calibration_tool_zh_CN.qm
```

三者不能混成一个 ZIP。

---

## 77. 不冻结历史测试数量

例如：

```text
1013 passed
1340 passed
```

是历史阶段结果。

以后真正要求：

```text
Current official suite
→ all pass
```

而不是测试总数必须永远等于某个旧数字。

---

## 78. 不冻结历史 Artifact Hash

历史：

```text
v1.1 Main ZIP SHA-256
v1.1 Language Pack SHA-256
```

只描述 v1.1 exact bytes。

未来新版本：

```text
必须产生新的 hash
```

不能把旧 hash 当 build reproducibility 的唯一判断标准。

---

## 79. Development Change Checklist

普通开发提交前至少检查：

1. 这是 Implementation Change 还是 Product Contract Change？
2. 是否需要新增或更新 Tests？
3. 是否影响数学 Golden？
4. 是否影响 Schema / Migration？
5. 是否影响 Recovery？
6. 是否影响 Historical Correction？
7. 是否影响 Backup / Restore？
8. 是否影响 Anti-Anchoring？
9. 是否新增 user-facing English source string？
10. 是否更新 zh_CN TS？
11. Ruff 是否通过？
12. pytest 是否通过？
13. Technical Reference 是否仍准确？
14. User Guide 是否受影响？
15. Localization Guide 是否受影响？

---

## 80. Release Candidate Checklist

正式 RC 至少确认：

1. 当前 Product Version 已检查。
2. 历史规格没有被机械重写。
3. `uv.lock` 与项目依赖一致。
4. Ruff PASS。
5. Full pytest PASS。
6. zh_CN TS 无 unfinished。
7. `.qm` strict compile PASS。
8. Main Build 使用正式 PyInstaller spec。
9. Artifact Audit PASS。
10. Artifact 无用户数据库。
11. Artifact 无用户日志、settings 和 lock。
12. Artifact 无仓库源码泄漏。
13. Main Package 不含 App zh_CN Pack。
14. Packaged Smoke PASS。
15. Packaged Runtime 不依赖 Repository / `.venv`。
16. Isolated LocalAppData 工作正常。
17. Single-instance 自动验证符合预期。
18. Manual Windows Acceptance PASS。
19. 外部 zh_CN Pack 真实安装 + Restart PASS。
20. Main ZIP 结构正确。
21. Language Pack ZIP 内容正确。
22. 第三方许可证与 notices 已核对。
23. 最终 ZIP SHA-256 已重新计算。
24. Release Commit 与被构建源码一致。
25. Annotated Tag 指向该 Commit。
26. GitHub Release 绑定正确 Tag。
27. 上传的文件就是计算 Hash 的 exact files。

---

## 81. 当前 Production Pipeline

当前正式流程可以最终概括为：

```text
Source
  ↓
Locked Python 3.13 Environment
  ↓
Ruff
  ↓
pytest
  ↓
Localization QA
  ↓
PyInstaller Formal Spec
  ↓
onedir Artifact
  ↓
Artifact Audit
  ↓
Packaged Smoke
  ↓
Manual Windows Acceptance
  ↓
Main ZIP + Language Pack ZIP
  ↓
Third-Party License Review
  ↓
Final SHA-256
  ↓
Release Commit
  ↓
Annotated Tag
  ↓
GitHub Release
```

---

## 结论

Probability Calibration Tool 的正式 Release 不能简单理解成：

```text
PyInstaller 成功生成 EXE
→ 发布
```

完整 Release 需要同时证明：

```text
源码合同仍正确

锁定依赖可复现

自动测试通过

数学和数据库语义没有静默漂移

简体中文 translation 可验证

主应用 package 自包含

Packaged EXE 不依赖开发环境

发行物不夹带用户数据

真实 packaged application 能启动

用户数据写入正确 LocalAppData

App 中文语言包继续独立

第三方许可证材料与实际 Runtime 一致

最终 Asset 可以追溯到明确 Release Commit 和 Tag
```

因此：

```text
Build
```

只是 Release Pipeline 的中间阶段。

真正的 Release 终点是：

> 已验证的源码、已验证的 Windows Runtime、已验证的语言包、正确的许可证材料、明确的 Git identity 与一致的正式文档共同对应同一个版本。
