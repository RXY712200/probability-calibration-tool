# 第三方软件与许可证说明

Probability Calibration Tool 使用并可能在 Windows 发行包中重新分发若干第三方软件。

Probability Calibration Tool 自身采用 [MIT License](LICENSE)。该许可证只适用于本项目有权授权的代码、文档和翻译内容，不会替代、修改或重新许可任何第三方组件。

第三方组件仍分别受其各自的许可证、版权声明和其他适用条款约束。

不同版本的发行包中实际包含的第三方组件可能发生变化。正式发布新版本前，应根据最终打包产物重新核对本文件及随包提供的第三方许可证材料。

## 运行时第三方组件

### Python

**用途：** 提供打包后应用所需的 Python 运行环境。

**许可证：** Python Software Foundation License，以及 Python 发行物中适用于其所包含第三方组件的其他许可证与声明。

Windows 发行包可能包含 Python 运行时文件，例如 Python DLL、标准库和相关运行组件。

正式二进制发行时，应保留适用于实际重新分发内容的 Python 许可证和相关声明。

---

### PySide6 / Shiboken6 / Qt

**用途：** 图形用户界面及 Qt 运行时。

**许可证：** Qt for Python / PySide6 / Shiboken6 及 Qt 组件受其上游项目提供的相应许可证约束，包括适用情况下的 LGPL-3.0、GPL-3.0 或商业许可条款。

Probability Calibration Tool 的 Windows 发行包会重新分发应用运行所需的部分 Qt / PySide6 组件。

正式发行时，应根据最终打包产物保留适用于这些组件的许可证文本、版权声明及第三方 notices。

Qt 和 Qt for Python 自身也可能包含或使用其他第三方软件。本文件不替代这些上游许可证材料。

---

### SciPy

**用途：** 数值与统计计算，包括历史概率模型所需的统计分布计算。

**许可证：** BSD-3-Clause。

SciPy 的二进制发行物还可能包含受其他兼容许可证约束的第三方代码或库。

正式发行时，应同时保留：

- SciPy 自身的许可证；
- 实际重新分发的 SciPy 构建中要求保留的 bundled third-party notices。

---

### NumPy

**用途：** SciPy 及相关数值计算所依赖的运行时组件。

**许可证：** BSD-3-Clause。

NumPy 的二进制发行物也可能包含第三方组件及相应许可证材料。

正式发行时，应保留最终打包版本中适用的版权声明、许可证条件和免责声明。

---

### SQLite

**用途：** Probability Calibration Tool 的本地 SQLite 数据库运行支持。

**许可证状态：** SQLite 核心代码属于 Public Domain。

Windows 发行包中可能通过 Python 运行时或相关打包组件包含 SQLite 运行库。

---

### PyInstaller Runtime / Bootloader

**用途：** 将 Probability Calibration Tool 构建为可独立运行的 Windows 桌面应用。

PyInstaller 及其 bootloader 受 PyInstaller 上游项目自身的许可证和例外条款约束。

使用 PyInstaller 构建 Probability Calibration Tool 不会自动改变 Probability Calibration Tool 自身的 MIT License；但最终发行包仍必须遵守所有被重新分发第三方组件各自的许可证要求。

## 开发环境依赖

源代码仓库还使用一些只服务于开发、测试、静态检查或构建流程的工具，例如：

- PyInstaller
- pytest
- Ruff

这些工具出现在开发环境或 `pyproject.toml` 中，不代表它们的完整开发工具本体一定被重新分发在最终 Windows 用户发行包中。

最终用户发行物的第三方许可证清单应以**实际打包进去的组件**为准，而不能仅根据开发依赖列表推断。

## 简体中文翻译

本项目维护的简体中文翻译源：

`translations\probability_calibration_tool_zh_CN.ts`

以及由其生成的：

`probability_calibration_tool_zh_CN.qm`

属于 Probability Calibration Tool 自身项目内容，除非某个具体翻译条目另有明确的第三方来源说明。

因此，本项目自行编写的翻译内容原则上随 Probability Calibration Tool 的 MIT License 发布。

## 《The Binding of Isaac》相关名称

Probability Calibration Tool 使用《The Binding of Isaac》中的角色名称及相关文字术语，用于说明本工具所面向的游戏和记录对象。

Probability Calibration Tool 不因此主张对这些第三方名称、商标、游戏素材或其他相关知识产权拥有所有权，也不表示这些内容受本项目 MIT License 重新许可。

本项目不应被理解为《The Binding of Isaac》的官方产品、官方插件或经其权利方授权的产品，除非未来另有明确、可验证的授权说明。

Probability Calibration Tool 自身的许可证只适用于项目作者有权进行许可的项目内容。

## 二进制发行

正式 Windows 发行包除了应用运行文件外，还应根据实际重新分发的第三方组件携带适用的许可证和 notices。

典型结构可以是：

```text
ProbabilityCalibrationTool\
    ProbabilityCalibrationTool.exe
    _internal\
    LICENSE
    THIRD_PARTY_NOTICES.md
    licenses\
        ...
