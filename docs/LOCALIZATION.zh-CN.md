# Probability Calibration Tool 本地化维护指南

本文档说明 Probability Calibration Tool 当前的界面本地化架构、语言包安装位置、语言偏好、启动回退、`.ts` / `.qm` 维护规则以及 Release 约束。

本文主要面向：

- 维护本地化代码的开发者；
- 修改简体中文翻译的维护者；
- 制作 Release 语言包的维护者；
- 排查语言包、语言设置和回退问题的人。

普通用户如何安装和切换语言，请参阅 [用户指南](USER_GUIDE.zh-CN.md)。

开发、编译与 Release 命令请参阅 [开发与发布指南](DEVELOPMENT.zh-CN.md)。

---

## 1. 当前语言模型

当前正式支持：

| 语言 | 内部值 | 来源 |
| --- | --- | --- |
| English | `en` | 内置 |
| 简体中文 | `zh_CN` | 外部语言包 |

当前支持的语言集合是显式定义的。

程序不会因为 `languages` 目录中出现任意 `.qm` 文件，就自动把新的语言加入 Language UI。

当前没有正式支持：

```text
zh
zh_TW
ja_JP
自动跟随系统语言
任意第三方 locale 自动发现
```

---

## 2. English 是内置基线

应用源码中的正式 source strings 使用 English。

因此，即使没有任何外部应用语言包：

```text
Probability Calibration Tool
→ 仍可完整使用 English UI
```

English 不依赖：

```text
probability_calibration_tool_en.qm
```

之类的额外应用语言包。

Language UI 中 English 的来源应理解为：

```text
Built-in
```

---

## 3. 简体中文是外部 App Translation Pack

当前简体中文应用语言包的正式文件名：

```text
probability_calibration_tool_zh_CN.qm
```

这是：

```text
Probability Calibration Tool 自身 UI 的 translation catalog
```

而不是：

```text
数据库
插件
设置文件
Qt framework translation
```

---

## 4. 语言包安装目录

默认应用数据根：

```text
%LOCALAPPDATA%\ProbabilityCalibrationTool\
```

应用语言包目录：

```text
%LOCALAPPDATA%\ProbabilityCalibrationTool\languages\
```

因此简体中文应用语言包的标准路径：

```text
%LOCALAPPDATA%\ProbabilityCalibrationTool\languages\probability_calibration_tool_zh_CN.qm
```

这个目录与程序解压目录分离。

所以：

```text
删除主程序解压目录
```

不等于：

```text
删除已安装语言包
```

---

## 5. 必须使用 Canonical Filename

当前代码只接受标准文件名：

```text
probability_calibration_tool_zh_CN.qm
```

以下名称不能被视作正式别名：

```text
probability_calibration_tool_zh.qm
zh_CN.qm
zh.qm
renamed_zh_CN.qm
probability_calibration_tool_zh_CN.qm.qm
```

语言包发现不能依赖：

```text
扫描所有 *.qm
→ 猜哪个是中文包
```

---

## 6. 官方翻译源

简体中文正式翻译源：

```text
translations\probability_calibration_tool_zh_CN.ts
```

当前 TS 定义：

```text
source language = en
target language = zh_CN
```

维护流程应始终理解为：

```text
English source strings
        ↓
zh_CN translations
        ↓
compile
        ↓
probability_calibration_tool_zh_CN.qm
```

---

## 7. `.ts` 与 `.qm`

`.ts`：

```text
可维护的翻译源
```

主要包含：

```text
context
source
translation
locale metadata
```

`.qm`：

```text
Qt Runtime 使用的编译 translation catalog
```

普通用户运行应用需要安装：

```text
.qm
```

而不是：

```text
.ts
```

Release Language Pack 应提供编译后的 canonical `.qm`。

---

## 8. 语言偏好存储

语言偏好不写入：

```text
probability.db
```

而保存在：

```text
%LOCALAPPDATA%\ProbabilityCalibrationTool\settings.ini
```

使用 QSettings：

```text
IniFormat
```

当前 preference key：

```text
localization/preferred_language
```

因此：

```text
业务数据库
```

与：

```text
UI Language Preference
```

是独立的持久化数据。

---

## 9. QSettings 行为

当前语言设置使用 QSettings，并关闭隐式 fallback settings location。

设置写入还要求进行明确同步和后续验证。

本地化代码不能假设：

```text
setValue()
```

调用返回就一定意味着设置已经可靠保存。

---

## 10. 默认 English 不主动写设置

如果：

```text
settings.ini 不存在
```

或：

```text
localization/preferred_language key 不存在
```

启动时：

```text
preferred language = English
preference state = DEFAULT
```

但读取流程不应为了记录默认值而自动：

```text
创建 settings.ini
写入 en
```

因此仅第一次启动应用，不应该因为默认 English 产生不必要的 preference write。

---

## 11. 合法 Preference Values

当前合法持久化值只有：

```text
en
zh_CN
```

必须精确匹配。

例如：

```text
zh
zh-CN
zh_TW
" en "
banana
空字符串
```

均不是合法 preference value。

无效值启动时：

```text
Effective Language → English
```

但程序不会因为发现无效 preference 就自动重写 settings。

---

## 12. Preference 与 Pack Locale Normalization 不同

需要区分：

### Preference

必须精确为：

```text
zh_CN
```

因此：

```text
zh-CN
```

不是合法 saved preference。

### `.qm` Locale Metadata Preflight

语言包 metadata 在验证时可以进行有限 normalization：

```text
trim whitespace
"-" → "_"
```

所以 `.qm` metadata：

```text
zh-CN
```

可以标准化为：

```text
zh_CN
```

后再进行 locale comparison。

不能把这两个规则混为一谈。

---

## 13. Preference Read Failure

如果 `settings.ini` 存在，但发生：

```text
AccessError
FormatError
其它读取错误
```

当前启动行为：

```text
Effective Language → English
```

并记录：

```text
settings read failure
```

但不会自动：

```text
清空 settings.ini
覆盖原文件
写入 en
```

读取错误不能变成未经用户授权的设置修复。

---

## 14. App Pack Preflight

简体中文语言包不能只凭：

```text
文件存在
```

就认为可用。

当前 preflight 会区分：

```text
VALID
MISSING
LOAD_FAILED
EMPTY_CATALOG
MISSING_LOCALE_METADATA
LOCALE_MISMATCH
CATALOG_SENTINEL_MISSING
```

只有：

```text
VALID
```

才能让简体中文成为正式 available language。

---

## 15. Preflight：文件存在

首先要求 canonical path：

```text
languages\probability_calibration_tool_zh_CN.qm
```

确实存在并且是文件。

否则：

```text
MISSING
```

---

## 16. Preflight：精确加载

QTranslator 必须从指定 canonical path 成功加载。

不能依赖 Qt 自己寻找：

```text
相似名字
备用文件名
其它路径中的 catalog
```

如果 canonical file 本身无法加载：

```text
LOAD_FAILED
```

---

## 17. Preflight：Catalog 非空

如果 `.qm` 技术上可以打开，但：

```text
translator.isEmpty()
```

则：

```text
EMPTY_CATALOG
```

一个空 catalog 不属于有效应用语言包。

---

## 18. Preflight：Locale Metadata

读取语言包 locale metadata。

标准化后必须：

```text
zh_CN
```

如果 metadata 缺失：

```text
MISSING_LOCALE_METADATA
```

如果 locale 不匹配：

```text
LOCALE_MISMATCH
```

---

## 19. Preflight：Catalog Sentinel

合法应用语言包还必须包含本项目指定的 translation sentinel。

当前 sentinel：

```text
context = Localization
source = Language
```

如果不存在：

```text
CATALOG_SENTINEL_MISSING
```

这样可以避免一个：

```text
locale 看起来是 zh_CN
但实际上属于另一个应用
```

的 `.qm` 被误认为 Probability Calibration Tool language pack。

---

## 20. Preflight 不能安装 Translator

Preflight 只负责：

```text
验证
```

不能产生：

```text
QCoreApplication global translation side effect
```

正式 translator installation 只发生在本地化 initialization 阶段。

因此：

```text
preflight()
```

执行完毕后，不应因为验证动作本身就改变当前 UI 语言。

---

## 21. Available Languages

English 永远：

```text
available
```

只有当：

```text
zh_CN app pack preflight = VALID
```

时：

```text
zh_CN
```

才进入当前 available language set。

语言包：

```text
Missing
Corrupt
Wrong locale
Wrong catalog
```

时，Language UI 不应允许把它作为正常可保存的中文选择。

---

## 22. Preferred Language 与 Effective Language

必须区分：

```text
preferred_language
```

和：

```text
effective_language
```

例如：

```text
saved preference = zh_CN
language pack missing
```

则：

```text
preferred_language = zh_CN
effective_language = en
```

即：

> 用户仍然偏好中文，但本次启动无法安全加载中文，因此实际运行 English。

---

## 23. Startup Language Decision

典型决策：

| Saved Preference | zh_CN Pack | 本次 Effective Language |
| --- | --- | --- |
| 无 | 任意 | English |
| `en` | 任意 | English |
| invalid | 任意 | English |
| read error | 任意 | English |
| `zh_CN` | Missing | English |
| `zh_CN` | Invalid | English |
| `zh_CN` | Valid | 简体中文 |

---

## 24. Missing Pack 不修改 Preference

如果用户已经保存：

```text
zh_CN
```

之后语言包被删除：

```text
本次启动 → English
```

但不会：

```text
preferred_language → en
```

这样当用户重新安装有效 `.qm` 后：

```text
下次启动
→ 可以重新使用 zh_CN
```

---

## 25. Invalid Pack 也不修改 Preference

如果 canonical `.qm`：

```text
损坏
为空
locale 错误
catalog 错误
```

本次：

```text
Effective Language → English
```

但：

```text
saved zh_CN preference
```

继续保留。

一次语言包故障不能永久删除用户偏好。

---

## 26. Invalid Preference 不自动修复

如果 settings 保存：

```text
banana
```

启动：

```text
English
```

但不会自动：

```text
banana → en
```

只有用户在 Language UI 中明确保存 English，才正式写入：

```text
en
```

---

## 27. Restart-Only

当前语言切换正式采用：

```text
restart-only
```

用户在运行中保存新的语言：

```text
只修改 preference
```

不会：

```text
立即安装或移除 translator
重建所有现有 Widgets
实时切换当前窗口语言
```

新语言：

```text
下次 application start 生效
```

---

## 28. `restart_required`

概念上：

```text
restart_required
=
preferred_language != effective_language
```

例如本次应用以 English 启动：

```text
effective = en
```

用户保存：

```text
preferred = zh_CN
```

则：

```text
restart_required = true
```

当前 process 仍继续使用 English。

---

## 29. 为什么不支持 Hot Switching

当前 translator 生命周期绑定：

```text
整个 UI process
```

而不是单个 DesktopSession。

运行时强制 hot switch 需要可靠重新翻译：

```text
Main Window
Safety Window
Modals
Errors
Warnings
Buttons
Tables
Session replacement UI
```

当前产品没有这项复杂需求。

因此正式策略保持：

```text
Save
→ Restart
```

---

## 30. Language Preference Save

保存 preference 不是简单：

```text
QSettings.setValue()
→ 成功
```

当前流程需要：

```text
读取原值
        ↓
写入 selected language
        ↓
sync
        ↓
检查 QSettings status
        ↓
使用 fresh reader 再读
        ↓
验证实际保存值
        ↓
才更新 LocalizationContext
```

---

## 31. 保存 zh_CN 前重新 Preflight

即使程序启动时：

```text
zh_CN pack = VALID
```

用户真正点击保存中文前，仍重新验证当前 canonical pack。

因为程序运行期间文件可能：

```text
被删除
被替换
被损坏
```

如果此时 preflight 不再有效：

```text
拒绝保存新的 zh_CN preference
```

---

## 32. Availability 在当前 Process 中只允许降级

如果中文 pack：

```text
startup 时 valid
```

后来运行过程中变成 invalid：

```text
zh_CN 可以从 available set 中移除
```

但如果 startup 时 pack 不存在，后来用户手工把 `.qm` 放进去：

```text
当前 process 不自动 promotion
```

需要：

```text
重新启动应用
```

重新执行 localization initialization。

---

## 33. 保存相同的 Healthy Preference

如果：

```text
当前已保存 preference = en
用户再次确认 en
```

且 preference 本身健康：

```text
不需要重复写 Settings
```

同样适用于已保存且健康的 `zh_CN`。

---

## 34. DEFAULT English 与 SAVED English

第一次启动：

```text
effective = en
preference state = DEFAULT
```

如果用户后来明确进入 Language Dialog 并保存 English：

```text
localization/preferred_language = en
```

之后状态属于：

```text
SAVED_VALID
```

因此：

```text
默认 English
```

和：

```text
用户明确选择 English
```

是两个不同 preference state。

---

## 35. Save Failure

可能的失败包括：

```text
PACK_INVALID
SETTINGS_ACCESS_ERROR
SETTINGS_FORMAT_ERROR
VERIFY_MISMATCH
```

保存失败时：

```text
LocalizationContext
```

不得先假装已经切换为新 preference。

内存中的：

```text
preferred_language
preference_state
fallback state
```

继续保持原权威值。

---

## 36. Settings Best-Effort Restore

如果新的设置写入已经开始，但后续：

```text
sync
readback
verification
```

失败，程序会尽可能恢复之前的 preference value。

如果旧 key 不存在：

```text
尝试移除新增 key
```

如果旧 key 存在：

```text
尝试恢复旧 raw value
```

这是：

```text
best-effort settings repair
```

不是 SQLite 式 ACID transaction。

---

## 37. Unrelated Settings 必须保留

修改：

```text
localization/preferred_language
```

不能通过：

```text
settings.clear()
```

删除其它 settings。

本地化 preference 只能修改自身负责的 key。

---

## 38. App Translator 与 Qt Translator

简体中文启动可能使用两类 translator。

### App Translator

```text
probability_calibration_tool_zh_CN.qm
```

翻译 Probability Calibration Tool 自己的 source strings。

### Qt Framework Translator

例如：

```text
qtbase_zh_CN.qm
```

用于 Qt 自身拥有的标准 UI 文本。

二者不能混为一谈。

---

## 39. Qt Framework Translation 可以降级

如果：

```text
App zh_CN Pack = VALID
```

但：

```text
Qt framework translation unavailable
```

应用自身仍然可以：

```text
Effective Language = zh_CN
```

只是少量 Qt-owned text 可能继续显示 English。

这是允许的 degraded state。

---

## 40. App Translator Failure 必须回 English

如果正式安装应用自己的 zh_CN translator 失败：

```text
Effective Language → English
```

而不是继续声称：

```text
zh_CN active
```

同时应清理可能已经安装的相关 translator，避免形成半翻译状态。

---

## 41. Localization 初始化发生在正常 Runtime UI 之前

Production startup 大致：

```text
QApplication
        ↓
AppPaths
        ↓
Localization Initialization
        ↓
StartupService
        ↓
DesktopHost
```

所以：

```text
Main Window
Safety Window
Startup notice
ALREADY_RUNNING presentation
```

都可以使用启动时已经确定的 language context。

---

## 42. Localization 是 Process-Level Lifetime

LocalizationContext 与 translator：

```text
属于当前 UI process lifetime
```

而不是：

```text
DesktopSession lifetime
```

因此成功 Restore 后即使：

```text
旧 Session dispose
新 Session 创建
Window 重建
```

当前 process 的 effective language 仍保持不变。

---

## 43. Restore 不触发语言重新选择

数据库 Restore：

```text
不重新读取 settings.ini
不重新决定语言
不执行 hot switch
```

本次 process 继续使用 startup 时确定的：

```text
effective_language
```

直到下一次程序启动。

---

## 44. Localization Fail-Open to English

Localization initialization 是当前少数允许：

```text
fail open
```

的启动能力。

如果 localization 初始化本身发生未预期异常：

```text
记录日志
        ↓
创建 English fallback context
        ↓
继续 Startup
```

原因是：

> 语言系统故障本身不应该使本地业务数据库无法访问。

---

## 45. Localization Fail-Open 不能推广到数据安全

以下情况：

```text
Database corruption
Application invariant failure
Snapshot corruption
Restore validation failure
```

不能因为 Localization 可以 fallback English，就同样：

```text
忽略错误继续运行
```

数据安全仍遵循：

```text
fail closed
```

---

## 46. English Fallback Context

Initialization 出现未预期异常时，English fallback context：

```text
不尝试自动修 settings.ini
不尝试修改 language pack
不继续反复安装 translator
```

而是建立：

```text
English
```

安全 presentation baseline。

---

## 47. Half-Installed Translator Cleanup

如果 localization initialization 在 translator 安装途中失败：

```text
已经尝试安装的 translator
```

必须尽可能移除。

不能：

```text
初始化失败
→ bootstrap fallback English
→ 但部分中文 translator 仍挂在 QApplication
```

---

## 48. Startup Notices

语言系统可以向用户说明本次为什么没有使用其首选语言。

例如：

```text
Preferred pack missing
Preferred pack invalid
Invalid saved preference
Settings read error
App translator install failed
Localization initialization failed
```

Notice 只是：

```text
解释当前 fallback
```

不是自动修改 preference 的授权。

---

## 49. Language Dialog

Language UI 应明确区分：

```text
Preferred language
Current language
Available languages
```

这样用户可以理解：

```text
我想用中文
```

与：

```text
本次启动实际上只能使用 English
```

之间的区别。

---

## 50. Language Names

当前语言名称显示：

```text
English
简体中文
```

即使当前 UI 是 English：

```text
简体中文
```

仍可以使用其语言自称。

---

## 51. Language Provenance

Language Dialog 应继续让用户能够区分：

```text
English
→ Built-in

简体中文
→ External language pack
```

因为二者的 availability contract 不同。

---

## 52. Localization 只能改变 Presentation

Localization 可以改变：

```text
Window title
Button
Label
Error text
Warning text
Character display name
Status presentation
```

但不能改变：

```text
RoundStatus
WorkflowState
ErrorCode
SafeErrorCode
Schema
Probability
EV
Model Version
Transaction result
```

---

## 53. 翻译文本不得成为业务状态

数据库不能保存：

```text
status = "已完成"
```

然后依赖当前语言判断状态。

必须保存语言无关的正式业务值，例如：

```text
completed
pending
voided
```

中文只负责 presentation。

---

## 54. Character Identity 与翻译分离

例如：

```text
character_id = 1
```

无论 UI 显示：

```text
Isaac
```

还是：

```text
以撒
```

都表示同一个 Character。

Display translation 不能改变数据库 identity。

---

## 55. 简体中文关键术语

当前关键术语应保持一致：

| English | 简体中文 |
| --- | --- |
| Round | 单局 |
| New Round | 新一局 |
| Pre-run inputs | 局前预测输入 |
| Post-run | 局后处理 |
| Maintenance | 维护 |
| Regime | 历史阶段 |
| Current regime | 当前历史阶段 |
| Start New Regime | 开始新的历史阶段 |
| Historical Correction | 历史记录更正 |
| Recovery | 未完成单局恢复 |
| Restore | 备份恢复 |
| Normal Restore | 常规备份恢复 |
| Emergency Restore | 紧急备份恢复 |
| Subjective probability | 主观概率 |
| Historical probability | 历史概率 |
| Include | 计入历史 |
| Exclude | 不计入历史 |
| Win | 胜 |
| Loss | 负 |

特别要求：

```text
Regime
→ 历史阶段
```

不要随意改成：

```text
模式
```

同时：

```text
Recovery
```

与：

```text
Restore
```

必须保持不同中文概念。

---

## 56. Qt Translation Key

Qt translation lookup 依赖：

```text
context
+
source string
```

所以修改 English source text：

```text
不仅是英文文案改动
```

还可能导致现有：

```text
TS translation
```

失去匹配。

---

## 57. Context 也是 Translation Contract

例如 translation context：

```text
Localization
Analysis
Errors
```

如果代码重构导致 context 改名：

```text
必须重新维护 TS inventory
```

不能只确认 Python source 能运行。

---

## 58. Placeholder

例如：

```text
Preferred language: %1
```

翻译必须保留：

```text
%1
```

如果 source 使用：

```text
%1
%2
```

translation 必须保持相同 placeholder signature。

不能：

```text
删除
增加
改错编号
```

---

## 59. 不要硬编码动态值

错误：

```text
首选语言：English
```

如果正式 source 是：

```text
Preferred language: %1
```

正确翻译应该仍保留：

```text
首选语言：%1
```

动态值由程序填充。

---

## 60. Error Translation

错误翻译只能翻译：

```text
经过批准的 safe user-facing source
```

不能因为“中文解释更清楚”就在翻译中加入：

```text
Raw SQL
Exception
内部路径
Traceback
```

从而绕过 Safe Error Presentation 合同。

---

## 61. Translation 不改变 Severity

Localization 可以改变：

```text
Warning
Error
Information
```

显示文本。

但真正：

```text
severity
Runtime disposition
Workflow state
```

仍由程序逻辑决定。

---

## 62. Bilingual Business Parity

English 与简体中文必须执行：

```text
相同业务行为
```

Localization 不能改变：

```text
Probability
Workflow transition
Correction
Recovery
Restore
Error classification
```

实际结果。

---

## 63. 主程序与中文语言包分离

当前正式 Packaging Contract：

```text
Main Windows Package
→ English built-in

Simplified Chinese
→ Separate external language pack
```

主程序 ZIP 不应包含应用专属：

```text
probability_calibration_tool_zh_CN.qm
```

---

## 64. Qt Translation 不等于 App Translation

主 PyInstaller package 中可能存在：

```text
_internal\PySide6\translations\
```

及 Qt framework catalogs。

这不意味着：

```text
Probability Calibration Tool zh_CN app pack
```

已经内置。

必须区分：

```text
Qt-owned translation
```

和：

```text
Application translation
```

---

## 65. Language Pack Release Asset

正式简体中文 asset 命名模式：

```text
ProbabilityCalibrationTool-LanguagePack-zh_CN-<version>.zip
```

当前推荐 ZIP 只包含：

```text
probability_calibration_tool_zh_CN.qm
```

不包含：

```text
.ts
Source code
Database
Logs
Settings
Python runtime
```

---

## 66. Language Pack Version Policy

推荐用户：

> 使用与当前应用 Release 对应的语言包。

但当前实现没有正式：

```text
language-pack package version metadata handshake
```

因此不能声称：

```text
应用会检测 1.1 / 1.2 pack version 并自动拒绝 mismatch
```

除非未来真正实现。

---

## 67. 为什么仍推荐版本匹配

旧 `.qm` 与新应用混用可能导致：

```text
新 source strings untranslated
旧 entries unused
Context drift
Terminology drift
```

所以 Release 应继续：

```text
App Version
↔
Matching Language Pack Version
```

一起发布。

---

## 68. Release-Specific Hash

某个 `.qm` 或 Language Pack ZIP 的：

```text
size
SHA-256
```

属于具体 Release artifact。

不应把当前版本 hash 写死进本文档。

应该记录在：

```text
Release Notes
Release manifest
Release evidence
```

中。

---

## 69. Translation Maintenance Flow

正式流程：

```text
新增/修改 English source
        ↓
更新 TS inventory
        ↓
完成 zh_CN translation
        ↓
检查 terminology
        ↓
检查 placeholder
        ↓
compile QM
        ↓
Localization tests
        ↓
Manual bilingual UI QA
        ↓
Release language-pack asset
```

具体命令见：

```text
DEVELOPMENT.zh-CN.md
```

---

## 70. English 必须继续作为 Source Language

当前架构：

```text
English source
+
zh_CN external translation
```

因此 production source 不应逐步改成：

```text
直接硬编码中文 source strings
```

否则：

```text
English built-in baseline
```

会被破坏。

---

## 71. 新 UI String 必须进入本地化维护

新增：

```text
Button
Dialog
Warning
Startup Page
Safety UI
```

时，应检查其用户可见字符串是否正确进入 translation catalog。

不要让中文 UI 因为新功能长期出现未经管理的混合语言。

---

## 72. Diagnostic Log 不要求本地化

开发者日志：

```text
Traceback
Internal diagnostics
Startup debug
```

不属于普通 user-facing translation scope。

不需要为了追求 translation coverage 把所有 log message 加入 `.ts`。

---

## 73. Internal Values 不翻译

例如：

```text
zh_CN
saved_valid
preferred_pack_missing
loaded
```

等内部 enum / protocol value 保持语言无关。

只翻译：

```text
用户真正看到的 presentation
```

---

## 74. 本地化测试应保护的核心不变量

至少继续保证：

```text
English 永远内置可用

只支持明确注册的语言

Missing preference 默认 English 且不主动写设置

Preference 只接受正式值

Invalid preference 不自动重写

Settings read failure 不自动重写

zh_CN pack 必须使用 canonical filename

Pack 必须通过完整 preflight

Preflight 不安装 translator

保存 zh_CN 前重新 preflight

Save failure 不修改内存 authority

Unrelated settings 保留

语言切换 restart-only

保存 preference 不立即改变 effective language

Qt framework translation failure 可降级

App translator install failure 回 English

Localization initialization failure 回 English

半安装 translator 清理

Restore / Session replacement 不改变 process language

English / zh_CN business parity

Placeholder 保持

Safe Error contract 保持

App zh_CN pack 与 Main ZIP 分离
```

---

## 75. 新增语言时的影响面

如果未来正式支持：

```text
繁体中文
日语
其它 locale
```

至少需要同步修改：

```text
Language enum / registry
Preference validation
Language discovery
Pack naming
Preflight
Language Dialog
Translation source
Packaging
Tests
User Guide
Localization Guide
Release assets
```

不能只：

```text
把另一个 .qm 放进 languages
```

就声称正式支持。

---

## 76. Hot Switching 属于架构变化

如果未来希望：

```text
无需重启立即切换语言
```

必须重新设计：

```text
Translator ownership
Widget retranslation
Modal lifetime
Safety Window
DesktopSession replacement
Error Presentation
Tests
```

这不是一个简单 UI enhancement。

---

## 77. 严格 Language-Pack Version 验证也属于新协议

如果未来增加：

```text
App 2.0
只能加载 Pack 2.0
```

则需要真正引入：

```text
Pack metadata
Compatibility rule
Failure presentation
Tests
Release tooling
```

当前不存在这一 protocol。

---

## 78. 最终模型

当前本地化架构可以概括为：

```text
English source
      │
      ├──────────────→ English built-in
      │
      ↓
zh_CN TS
      ↓
compile
      ↓
zh_CN QM
      ↓
external languages directory

settings.ini
preferred_language
      │
      ↓
application startup
      │
      ├── preferred zh_CN + valid pack
      │       ↓
      │   install translator
      │       ↓
      │     zh_CN
      │
      └── otherwise
              ↓
           English
```

运行中修改 preference：

```text
Save Preference
        ↓
Current process language unchanged
        ↓
Restart Required
        ↓
Next startup
        ↓
New Effective Language
```

---

## 结论

Probability Calibration Tool 当前采用：

```text
English built-in

optional external zh_CN QM

restart-only language preference

safe fallback to English
```

本地化系统的核心合同是：

```text
Preference 不被静默改写

语言包必须经过明确验证

Invalid / Missing Pack 安全回 English

Qt framework translation 可以独立降级

业务数据库不保存本地化状态文本

Translation 不改变业务行为

Restore / Session replacement 不改变当前 process language

语言系统异常不能破坏核心数据访问能力
```

因此 Localization 属于：

```text
Presentation capability
```

而不是：

```text
Business-state capability
```

只要这一边界继续成立，维护或扩展翻译就不会改变 Probability、Workflow、Database、Recovery 或 Restore 的核心业务合同。
