# Probability Calibration Tool 用户指南

## 关于本指南

本指南面向 Probability Calibration Tool 的普通使用者，主要说明程序各个功能应该如何操作、界面中的主要选项分别代表什么，以及在常见情况下应该如何处理。

Probability Calibration Tool 当前用于《The Binding of Isaac（以撒的结合）》抖音直播间积分玩法中的概率记录、分析与校准。

本指南重点回答“怎么使用程序”，不会详细展开数学公式、数据库结构、状态机、事务语义等内部实现。

如果需要了解数学模型、数据库结构、Workflow、事务语义、Recovery、Historical Correction、Backup / Restore 等内部实现，请参阅 [技术参考](TECHNICAL_REFERENCE.zh-CN.md)。

## 下载、解压与第一次启动

### 下载正式发布包

普通用户应从项目的 GitHub Releases 页面下载正式发布包。

Windows x64 主程序文件名格式为：

`ProbabilityCalibrationTool-<version>-Windows-x64.zip`

如果需要简体中文界面，还可以另外下载对应版本的语言包：

`ProbabilityCalibrationTool-LanguagePack-zh_CN-<version>.zip`

普通用户不需要下载 GitHub 自动生成的：

- `Source code (zip)`
- `Source code (tar.gz)`

这些是源码归档，不是可以直接运行的 Windows 程序。

### 解压程序

下载主程序 ZIP 后，应先将整个压缩包完整解压。

解压后，程序目录中至少会包含：

`ProbabilityCalibrationTool.exe`

以及：

`_internal`

`ProbabilityCalibrationTool.exe` 依赖 `_internal` 中的运行时文件，因此请保持原有目录结构不变。

不要：

- 只把 `ProbabilityCalibrationTool.exe` 单独移动到其他位置；
- 删除 `_internal`；
- 随意移动 `_internal` 中的文件；
- 直接在压缩包内部运行程序。

如果需要移动程序，请移动整个解压后的 `ProbabilityCalibrationTool` 文件夹。

### 第一次启动

完成解压后，双击：

`ProbabilityCalibrationTool.exe`

即可启动程序。

正式发布包已经包含运行程序所需的 Python 运行时和相关组件，因此普通用户不需要另外安装：

- Python；
- uv；
- PySide6；
- Qt；
- SciPy；
- 其他开发环境。

程序采用免安装形式，不需要运行安装程序，也不需要通过命令行启动。

### 第一次启动时的界面语言

Probability Calibration Tool 的内置默认界面语言为：

`English`

如果没有安装任何外部语言包，程序会正常使用 English 界面。

如果需要简体中文，可以另外安装 Simplified Chinese 语言包。完整步骤见本指南后面的“界面语言与中文语言包”章节。

### 管理员权限

正常使用 Probability Calibration Tool 不需要以管理员身份运行。

建议直接以普通用户权限启动程序。

### 程序文件与用户数据是分开的

程序本体位于你解压出来的文件夹中。

用户数据则保存在：

`%LOCALAPPDATA%\ProbabilityCalibrationTool\`

因此，程序文件夹和用户数据目录并不是同一个位置。

关于数据库、备份、设置、日志以及迁移电脑的详细说明，请参阅后面的“数据保存、备份与迁移”章节。

## 界面结构概览

Probability Calibration Tool 的主界面围绕“一局事件”的完整生命周期设计。

日常使用时，最常接触的是：

- `New Round`
- 局前预测输入
- 分析结果
- 局后处理

除此之外，程序还提供：

- `Maintenance`
- `Historical Correction`
- `Restore`
- `Interface Language...`

用于处理历史阶段、更正、备份恢复和界面语言等功能。

### New Round

`New Round` 是日常开始一局记录的主要入口。

在这里可以：

- 选择当前角色；
- 选择是否参考历史数据；
- 输入主观概率；
- 输入胜方赔率；
- 输入负方赔率；
- 执行 `Calculate`。

正常情况下，每一局都从这里开始。

### 局前预测输入

局前预测输入用于记录当前一局在正式分析之前的原始判断。

主要内容包括：

- `Character`
- `Use history` / `Do not use history`
- `Subjective probability`
- `Win odds`
- `Lose odds`

这些数据应该在当前一局结果尚未确定时填写。

其中，主观概率应尽量反映用户在查看当前局正式历史分析之前的原始判断。

### 分析结果

点击 `Calculate` 并成功完成计算后，程序会显示正式分析结果。

分析区域主要包括：

- `Subjective Analysis`
- `Historical Analysis — independent model`
- 概率与不确定性区间
- Win-side EV / S
- Lose-side EV / S
- Break-even thresholds
- Odds combination
- 计算时间和历史数据截止时间等信息

历史分析是否显示，取决于：

- 当前是否选择参考历史数据；
- 当前历史数据是否达到程序规定的统计条件。

主观分析与历史分析始终是两个独立模型。

### 局后处理

当前一局结束后，需要在局后处理区域记录实际结果。

主要包括：

- `Win`
- `Loss`
- `Include`
- `Exclude`
- `Confirm Save`

这里决定：

1. 当前一局最终是 Win 还是 Loss；
2. 当前记录是否计入后续历史统计。

`Exclude` 不会删除这一局，只是不让这一局参与后续历史统计。

### Maintenance

`Maintenance` 用于查看和维护当前角色相关的历史信息。

这里主要涉及：

- 当前角色；
- 当前历史阶段；
- 当前阶段的开始信息；
- 当前阶段原因；
- 当前阶段中计入历史的样本数量；
- 开始新的历史阶段。

为了避免历史信息影响用户当前一局的主观判断，在正式计算之前，Maintenance 中会限制某些具有方向性的历史信息。

### Historical Correction

`Historical Correction` 用于更正已经完成的历史记录。

它适合处理例如：

- 最终结果记录错误；
- 原本应该 Include，却误选成 Exclude；
- 原本应该 Exclude，却误选成 Include。

更正不会简单地无痕覆盖原记录。

程序会保留更正关系和相应的审计信息。

具体操作步骤见后面的“历史记录更正”章节。

### Restore

`Restore` 用于从有效备份恢复程序数据。

它与未完成单局的 `Recovery` 不是同一个功能：

- `Recovery`：继续之前没有完成的一局；
- `Restore`：使用备份恢复数据库。

只有在确实需要恢复数据时才应使用 Restore。

### Interface Language...

`Interface Language...` 用于选择界面语言。

当前程序：

- 内置 `English`
- 可通过外部语言包使用 `Simplified Chinese`

语言选择确认后，需要重新启动程序才会生效。

中文语言包的完整安装方法见后面的“界面语言与中文语言包”章节。

### 功能入口速查

日常记录：

`New Round`
→ 输入局前预测
→ `Calculate`
→ 查看分析
→ 记录结果
→ `Confirm Save`

历史维护：

`Maintenance`

已完成记录更正：

`Historical Correction`

数据库备份恢复：

`Restore`

界面语言：

`Interface Language...`

## 完成一局的标准流程

本章说明 Probability Calibration Tool 最常见的一次完整使用流程。

正常情况下，一局记录按照以下顺序进行：

`选择角色`
→ `选择是否参考历史`
→ `输入主观概率与赔率`
→ `Calculate`
→ `查看分析`
→ `等待结果`
→ `Win / Loss`
→ `Include / Exclude`
→ `Confirm Save`

### 1. 开始新一局

进入 `New Round`。

首先选择当前这一局对应的角色。

程序会按照所选角色分别维护相应的历史记录，因此应确保角色选择正确。

### 2. 选择是否参考历史数据

选择：

- `Use history`
- `Do not use history`

#### Use history

表示当前这一局希望在完成正式计算后，同时查看该角色对应的历史概率分析。

如果当前历史数据尚未达到程序规定的统计条件，即使选择了 `Use history`，程序也不会把尚不成熟的历史数据作为正式概率结论显示。

#### Do not use history

表示当前这一局不使用历史模型进行正式分析。

这不会删除已有历史记录，也不会影响历史数据本身。

### 3. 输入主观概率

填写 `Subjective probability`。

这里应填写你在当前这一局开始时，对结果作出的真实概率判断。

例如：

`65%`

表示你认为当前这一局发生 Win 的概率约为 65%。

主观概率应尽量在查看当前局正式历史分析之前填写。

程序这样设计，是为了尽量保留用户原始判断，避免历史信息反过来影响主观概率输入。

### 4. 输入赔率

填写：

- `Win odds`
- `Lose odds`

这两个输入分别用于当前 Win 侧和 Loss 侧的赔率分析。

请按照当前直播间积分玩法实际显示的赔率填写。

赔率会参与后续的 EV / S、盈亏平衡阈值和赔率组合状态等分析。

### 5. 检查输入

在点击 `Calculate` 之前，建议快速检查：

- 角色是否正确；
- 是否正确选择 `Use history` / `Do not use history`；
- 主观概率是否输入正确；
- Win odds 是否正确；
- Lose odds 是否正确。

可以使用 `Tab` 在界面中的可操作项之间快速切换。

### 6. 点击 Calculate

确认输入后，点击：

`Calculate`

计算成功后，程序会保存当前未完成单局及其分析快照，然后显示正式分析结果。

从这一刻开始，这一局已经进入正式记录流程。

### 7. 查看主观概率分析

程序会显示 `Subjective Analysis`。

这里的分析基于你刚才输入的主观概率和赔率。

可能看到的信息包括：

- Probability
- Uncertainty interval
- Win-side EV / S
- Lose-side EV / S
- Break-even thresholds
- Odds combination

这些项目具体应该如何理解，会在后面的“分析结果”章节中逐项说明。

### 8. 查看历史概率分析

如果当前选择了 `Use history`，并且历史数据满足程序要求，界面还会显示：

`Historical Analysis — independent model`

历史分析来自当前角色、当前历史阶段中符合条件的历史记录。

它与主观分析是两个独立模型。

程序不会把：

`主观概率 + 历史概率`

自动平均、加权或合成为一个综合概率。

如果没有显示正式历史概率分析，并不一定代表程序出现问题。

常见原因包括：

- 当前选择了 `Do not use history`；
- 当前角色的历史样本不足；
- 历史概率的不确定性仍然过高。

### 9. 等待当前一局结束

完成 Calculate 后，等待实际结果产生。

在结果尚未确定之前，不要提前填写 Win 或 Loss。

### 10. 记录实际结果

当前一局结束后，在局后处理区域选择：

- `Win`
- `Loss`

选择实际发生的结果。

### 11. 选择 Include 或 Exclude

然后决定这条记录是否参与后续历史统计。

#### Include

选择 `Include`：

> 当前记录会被保留，并计入后续对应角色和历史阶段的历史统计。

#### Exclude

选择 `Exclude`：

> 当前记录仍然会被保存，但不会计入后续历史统计。

因此：

> **Exclude 不等于删除。**

例如当前一局存在明显的异常情况，导致你认为它不适合作为正常历史样本时，可以选择 Exclude，同时仍然保留完整记录。

### 12. Confirm Save

确认：

- Win / Loss 正确；
- Include / Exclude 正确；

之后点击：

`Confirm Save`

程序会完成当前一局的正式保存。

当前记录随后成为已完成历史记录。

### 13. 开始下一局

本局完成后，即可重新进入新的 `New Round` 流程。

然后再次：

`选择角色`
→ `输入局前预测`
→ `Calculate`
→ `记录最终结果`
→ `Confirm Save`

如此重复记录后，程序会逐渐积累对应角色的历史数据。

### 使用时最重要的几个原则

- 主观概率应尽量反映你在查看正式历史分析之前的真实判断。
- 不要因为历史数据存在，就认为历史模型一定已经具有足够统计可靠性。
- `Subjective Analysis` 与 `Historical Analysis` 是两个独立结果。
- `Exclude` 只是“不计入历史统计”，不会删除本局记录。
- 当前一局已经完成 `Calculate` 后，如果发现局前输入有误，应使用正式的修改与重新计算流程，而不是把它当成一局新的记录。

## 局前预测输入

在点击 `Calculate` 之前，需要完成当前一局的局前预测输入。

主要包括：

- `Character`
- `Use history` / `Do not use history`
- `Subjective probability`
- `Win odds`
- `Lose odds`

这些输入共同构成当前一局正式分析的基础。

### Character

`Character` 用于选择当前这一局对应的《The Binding of Isaac（以撒的结合）》角色。

程序会按照角色分别维护相应的历史记录和历史阶段，因此角色选择会直接影响：

- 当前一局归属于哪个角色；
- 当前一局完成后计入哪个角色的历史数据；
- 选择 `Use history` 时读取哪一个角色的历史模型。

在点击 `Calculate` 之前，应确认角色与当前直播间实际对局一致。

如果角色选择错误，不应故意把错误记录继续完成。已经完成的错误历史记录应通过后续的 `Historical Correction` 流程处理。

### Use history / Do not use history

这一选项决定当前一局在正式计算后是否尝试显示历史概率分析。

#### Use history

选择 `Use history` 表示：

> 当前一局除了主观概率分析之外，还希望参考当前角色、当前历史阶段对应的历史概率模型。

需要注意：

> **Use history 不代表程序一定会显示一个历史概率。**

历史模型只有在已有数据达到程序规定的统计条件后，才会作为正式历史概率分析显示。

如果历史数据尚未成熟，程序不会为了给出一个数字而强行生成可靠性不足的历史结论。

#### Do not use history

选择 `Do not use history` 表示：

> 当前一局只使用当前输入进行主观概率分析，不在正式分析中使用历史概率模型。

这一选择：

- 不会删除历史数据；
- 不会清空当前角色的历史记录；
- 不会关闭以后其他单局的历史功能；
- 只影响当前这一局是否参考历史模型。

### Subjective probability

`Subjective probability` 是用户对当前这一局发生 `Win` 的主观概率判断。

允许输入的原始范围为：

`0% – 100%`

例如：

- `50%`：认为 Win 与 Loss 大致各占一半；
- `70%`：认为 Win 的可能性约为 70%；
- `20%`：认为 Win 的可能性较低，对应 Loss 的主观概率约为 80%。

这里填写的应该是：

> **你针对当前这一局本身作出的判断。**

而不是：

- 当前角色过去的历史胜率；
- 程序之前显示过的历史概率；
- 单纯把赔率反推出来的概率；
- 为了让分析结果“更好看”而人为调整的数字。

Probability Calibration Tool 会保留用户实际输入的主观概率。

对于数学计算中的极端边界值，程序内部会按照既定数学规则进行处理；这不会改变用户原始输入记录。

具体的边界处理和主观概率模型公式，请参阅技术参考文档。

### 为什么要先填写主观概率

Probability Calibration Tool 的一个核心设计原则是：

> **先记录当前判断，再查看正式历史分析。**

如果用户先看到当前角色的历史方向或历史概率，再决定自己这一局填多少，就容易使所谓“主观概率”实际上受到历史模型影响。

因此，程序在正式计算之前会限制部分可能影响判断的方向性历史信息。

这样长期积累下来的主观预测记录才更适合用于后续校准。

### Win odds

`Win odds` 是当前直播间积分玩法中 Win 一侧对应的赔率。

应按照当前一局实际显示的赔率填写，而不是使用自己估计的赔率。

Win odds 会与用户输入的主观概率一起参与：

- Win-side EV / S；
- 盈亏平衡阈值；
- 赔率组合状态；

等相关分析。

### Lose odds

`Lose odds` 是当前直播间积分玩法中 Loss 一侧对应的赔率。

同样应按照当前一局实际显示的赔率填写。

Lose odds 会参与：

- Lose-side EV / S；
- 盈亏平衡阈值；
- 赔率组合状态；

等相关分析。

### 赔率输入时的注意事项

填写赔率时，建议确认：

- Win odds 与 Lose odds 没有填反；
- 没有遗漏小数位；
- 使用的是当前这一局实际显示的赔率；
- 没有因为上一局赔率相同而默认继续沿用错误数据。

如果在 `Calculate` 之前发现输入错误，可以直接修正。

如果已经成功完成 `Calculate` 后才发现局前输入有误，应使用 `Modify` / `Recalculate` 流程进行修改。

### Calculate 前的快速检查

在正式计算之前，建议依次检查：

1. `Character`
2. `Use history` / `Do not use history`
3. `Subjective probability`
4. `Win odds`
5. `Lose odds`

可以使用 `Tab` 快速在这些可操作项之间移动焦点。

## Calculate 与分析结果

完成局前预测输入后，点击：

`Calculate`

程序会对当前一局进行正式计算。

计算成功后，当前一局及其分析快照会被保存，然后界面显示正式分析结果。

从这一刻开始，当前输入已经成为这一局正式记录的一部分。

### Subjective Analysis

`Subjective Analysis` 是基于用户当前一局输入的主观概率和赔率得到的分析。

它反映的是：

> 如果以当前输入的主观概率作为判断基础，那么当前 Win / Loss 两侧分别处于什么分析状态。

这一部分不依赖历史概率来修改用户自己的判断。

即使同时显示了 Historical Analysis，两套分析仍然彼此独立。

### Probability

`Probability` 表示当前分析所使用的概率。

在 Subjective Analysis 中，它来自用户本局输入的主观概率及程序规定的数学处理规则。

在 Historical Analysis 中，它来自当前角色、当前历史阶段中符合条件的历史记录所建立的历史模型。

不要把两个区域中的 Probability 理解成同一个来源。

### Uncertainty interval

`Uncertainty interval` 用于表示概率估计周围仍然存在的不确定范围。

它的作用是提醒用户：

> 一个显示为 70% 的概率，并不意味着程序认为真实概率一定精确等于 70%。

区间越宽，通常表示当前概率判断存在越大的不确定性。

区间越窄，则表示分析给出的概率范围更加集中。

Subjective Analysis 和 Historical Analysis 的不确定性区间来自各自独立的模型，因此不能直接把其中一个模型的区间套到另一个模型上。

具体计算方法和边界规则见技术参考文档。

### Win-side EV / S

`Win-side EV / S` 表示当前 Win 一侧在对应概率和赔率条件下的分析结果。

它用于帮助判断：

> 在当前概率假设下，Win 一侧的赔率与概率之间是什么关系。

程序会根据当前概率、不确定性范围和 Win odds 生成相应结果。

这里显示的是分析信息，而不是程序替用户作出的自动选择。

EV / S 的精确定义、计算公式以及各状态的判定条件见技术参考文档。

### Lose-side EV / S

`Lose-side EV / S` 与 Win-side EV / S 对应，但分析的是 Loss 一侧。

它使用：

- 当前概率模型；
- Loss 一侧对应的概率关系；
- Lose odds；

生成相应分析结果。

Win-side 与 Lose-side 应分别阅读，不应仅根据其中一侧的结果推断另一侧一定相反。

具体计算规则见技术参考文档。

### Break-even thresholds

`Break-even thresholds` 表示在当前赔率条件下，对应一侧达到盈亏平衡所需要的概率阈值。

可以把它理解为：

> 当自己的概率判断与这一阈值进行比较时，可以看出当前概率判断和赔率要求之间的距离。

程序会分别处理 Win 和 Loss 两侧相应的阈值。

需要注意，Win 与 Loss 的概率表达方向并不完全相同，因此不要简单把界面上两个阈值当成同一个数字的正反面。

精确换算方式见技术参考文档。

### Odds combination

`Odds combination` 用于描述当前 Win odds 和 Lose odds 组合起来之后所形成的整体赔率状态。

它不是第三套概率模型，也不会产生新的“综合概率”。

这一项主要帮助用户识别：

> 当前两侧赔率组合本身是否形成了需要注意的特殊分析区域或状态。

如果界面显示相应提示或 warning，应把它理解为赔率组合层面的分析信息，而不是数据库错误或程序故障。

具体状态分类及判定条件见技术参考文档。

### Historical Analysis — independent model

如果当前一局选择了：

`Use history`

并且当前角色的历史数据已经达到程序要求，界面会显示：

`Historical Analysis — independent model`

这一名称中的：

`independent model`

非常重要。

历史分析来自当前角色、当前历史阶段中符合条件的历史记录。

它不会：

- 修改用户已经输入的主观概率；
- 自动替代 Subjective Analysis；
- 与主观概率自动平均；
- 与主观概率自动加权；
- 生成一个所谓的最终综合概率。

因此，一个正常的结果完全可能是：

`Subjective probability = 70%`

而：

`Historical probability = 60%`

程序会把两个结果分别展示，而不会自动生成：

`65%`

应该由用户自己理解两套不同信息来源之间的差异。

### 为什么没有显示正式历史概率？

选择 `Use history` 并不保证当前一局一定能够显示正式 Historical Analysis。

常见原因包括：

1. 当前角色的历史样本还不够多；
2. 虽然已经存在一定数量的历史记录，但历史模型的不确定性仍然过高；
3. 当前历史阶段刚刚开始，能够用于该阶段的记录还不足；
4. 部分历史记录被设置为 Exclude，因此不会进入有效历史样本。

程序只有在历史数据满足规定的统计条件后，才会把历史模型作为正式概率分析显示。

这是有意的设计，并不代表程序发生故障。

精确的历史模型成熟条件见技术参考文档。

### Calculated locally

`Calculated locally` 表示当前这份分析在本机完成计算的时间。

它用于帮助确认：

> 这份分析是什么时候生成的。

### Data through locally

`Data through locally` 表示当前历史分析所使用的数据截止到什么时间。

这一项主要用于帮助区分：

- 当前这份分析是什么时候计算的；
- 历史模型实际包含的数据截止到什么时候。

对于 Subjective Analysis 和 Historical Analysis，应根据界面实际显示的信息理解相应时间字段。

### 建议的阅读顺序

第一次查看分析结果时，可以按照下面的顺序阅读：

1. 先看 `Subjective Analysis` 中的 Probability；
2. 再看对应的 `Uncertainty interval`；
3. 查看 Win-side EV / S；
4. 查看 Lose-side EV / S；
5. 查看 Break-even thresholds；
6. 查看 Odds combination；
7. 如果存在 `Historical Analysis — independent model`，再单独查看历史概率及其不确定性；
8. 最后比较主观模型和历史模型之间是否存在明显差异。

需要始终记住：

> **比较两个模型，不等于合并两个模型。**

Probability Calibration Tool 的设计目标是把不同信息来源清楚地展示出来，而不是替用户隐藏它们之间的差异。

### 不要根据分析结果回头篡改原始判断

完成 `Calculate` 后，如果只是因为看到 Historical Analysis 与自己的主观概率不同，不应使用 `Modify` 去把主观概率改成更接近历史结果。

`Modify` / `Recalculate` 的用途是修正真正的局前输入错误，例如：

- 概率输错；
- 赔率输错；
- 角色选错等需要合法修正的情况。

它不是用来在看到分析结果以后重新塑造原始判断的工具。

保持这一点，长期积累的主观概率记录才具有更好的校准价值。

## Modify / Recalculate

如果当前一局已经成功完成 `Calculate`，但后来发现局前输入存在错误，可以使用：

`Modify`

进入修改流程。

### Modify 是做什么的

`Modify` 用于修正当前这一局已经填写过的局前输入。

例如：

- 角色选错；
- 主观概率输入错误；
- Win odds 输入错误；
- Lose odds 输入错误；
- 其他允许重新填写的局前信息存在实际输入错误。

进入 Modify 后，当前这一局仍然是原来的同一局，不会因为修改而自动创建一条新的独立记录。

### 修改后为什么还要 Recalculate

进入 Modify 后，用户可以修正局前输入。

但是：

> **修改输入本身，不代表新的分析结果已经正式生效。**

必须点击：

`Recalculate`

并且重新计算成功后，程序才会基于修改后的输入生成新的正式分析结果。

因此流程是：

`Modify`
→ `修改输入`
→ `Recalculate`
→ `新的正式分析结果`

而不是：

`Modify`
→ `修改输入`
→ `立即自动替换旧分析`

这样可以避免界面上的输入状态和正式保存的分析结果之间出现不一致。

### Recalculate 成功后

成功完成 `Recalculate` 后：

- 当前一局仍然保持为同一条单局记录；
- 修改后的局前输入成为当前正式输入；
- 程序生成新的正式分析结果；
- 当前分析快照会对应新的正式计算结果。

用户之后应继续等待当前一局的最终结果，并完成正常的局后处理流程。

### Modify 不应该用来做什么

`Modify` 的用途是修正真正的输入错误。

不建议在已经看到正式分析结果之后，仅仅因为：

- 历史概率和自己的主观概率不同；
- EV / S 结果不符合自己的预期；
- 想让分析结果看起来更有利；

就回头修改原始主观概率。

这样会破坏“先记录判断，再观察历史”的设计原则，也会降低长期主观概率记录的校准价值。

### 如果只是最终结果填错了怎么办

如果当前一局已经完成保存，之后才发现：

- Win / Loss 记错；
- Include / Exclude 记错；

不应该使用 Modify / Recalculate。

这种情况应使用：

`Historical Correction`

进行历史记录更正。

也就是说：

- **局前输入错误** → `Modify / Recalculate`
- **已经完成后的结果记录错误** → `Historical Correction`

### 快速判断该用哪个功能

还没完成当前一局，发现局前输入错了：

`Modify / Recalculate`

当前一局已经完成，发现最终结果或 Include / Exclude 错了：

`Historical Correction`

## 局后处理

当前一局已经完成 `Calculate`，并且实际结果已经产生后，需要在局后处理区域记录最终结果。

局后处理主要包括：

- `Win`
- `Loss`
- `Include`
- `Exclude`
- `Confirm Save`
- `Cancel`

### Win / Loss

首先选择当前一局实际发生的结果：

- `Win`
- `Loss`

这里记录的是实际结果，而不是之前的主观判断。

例如：

- 即使局前主观概率认为 Win 的可能性很高，但实际结果是 Loss，也应该选择 `Loss`；
- 即使局前主观概率认为 Win 的可能性很低，但实际结果是 Win，也应该选择 `Win`。

程序需要保存真实结果，才能使后续历史统计和概率校准有意义。

### Include

选择：

`Include`

表示：

> 当前这一局会被正式保存，并计入后续对应角色和当前历史阶段的历史统计。

正常、具有代表性的对局通常应选择 Include。

### Exclude

选择：

`Exclude`

表示：

> 当前这一局仍然会被完整保存，但不会计入后续历史统计。

因此：

> **Exclude 不等于删除。**

Exclude 的作用是保留这局发生过的事实，同时避免它影响后续历史模型。

例如，如果某一局存在明显异常情况，使它不适合作为正常历史样本，可以选择 Exclude。

是否应该 Exclude 应根据实际情况判断，而不是因为某一局结果“不符合预期”就排除。

### Confirm Save

确认以下内容无误后：

- Win / Loss；
- Include / Exclude；

点击：

`Confirm Save`

程序会正式完成当前一局。

完成后：

- 当前一局成为已完成记录；
- 如果选择 Include，它会参与后续历史统计；
- 如果选择 Exclude，它仍然保留，但不会进入有效历史样本；
- 当前这一局不再处于未完成状态。

### Cancel

`Cancel` 用于取消当前正在进行的确认操作，并返回上一状态。

Cancel 不等于删除当前一局，也不代表已经完成保存。

如果只是发现：

- Win / Loss 还没选对；
- Include / Exclude 还需要重新确认；

可以先 Cancel，修正后再重新进行保存确认。

### 保存前建议检查

点击 `Confirm Save` 前，建议确认：

1. 当前实际结果是 Win 还是 Loss；
2. 当前记录是否应该 Include；
3. 如果选择 Exclude，是否确实是因为这局不适合作为正常历史样本，而不是因为结果不符合自己的预期。

如果已经完成保存后才发现最终结果或 Include / Exclude 记录错误，应使用：

`Historical Correction`

而不是重新创建一局来抵消原记录。

### 局后处理的两个独立决定

局后处理实际上需要分别回答两个问题：

**问题 1：这一局实际发生了什么？**

`Win / Loss`

**问题 2：这一局是否应该参与后续历史统计？**

`Include / Exclude`

这两个决定含义不同，不应混在一起理解。

## Include / Exclude

`Include` 和 `Exclude` 用于决定：

> 当前这一局是否参与后续历史统计。

它们不会改变这一局已经发生的实际结果，也不会决定这条记录是否存在。

### Include

选择：

`Include`

表示：

> 当前这一局会被保留，并作为有效历史样本参与后续统计。

如果当前对局属于正常、具有代表性的直播间积分玩法环境，并且没有明显异常情况，通常应选择 Include。

### Exclude

选择：

`Exclude`

表示：

> 当前这一局仍然会被完整保存，但不会作为有效样本参与后续历史统计。

因此：

> **Exclude 不是删除。**

程序仍然会保留这一局的记录，只是在建立后续历史模型时不把它计入有效历史样本。

### 什么时候可能考虑 Exclude

Exclude 应用于：

> 当前这一局存在明确原因，使它不再适合作为正常历史样本。

例如，当前对局的环境、规则或其他关键条件出现了明显异常，使这一局和正常情况下的对局缺乏可比性。

是否 Exclude，应该根据这一局本身是否具有统计代表性来判断。

### 不应该因为结果而 Exclude

不要仅仅因为：

- 这一局输了；
- 这一局结果和自己的主观判断相反；
- 这一局让历史胜率下降；
- 这一局让历史模型结果变得不符合预期；

就选择 Exclude。

否则会人为挑选样本，使历史数据失去原本的统计意义。

同样，也不应该因为某一局结果“很好”就特意保留，而把不喜欢的结果排除。

### Include / Exclude 与 Win / Loss 是两件事

局后处理实际上包含两个互相独立的问题：

#### 实际结果是什么？

`Win / Loss`

#### 这一局是否应该进入历史统计？

`Include / Exclude`

例如，一局完全正常但实际结果是 Loss：

`Loss + Include`

是完全合理的。

一局实际结果是 Win，但存在明确异常情况：

`Win + Exclude`

也可能是合理的。

因此，Include / Exclude 不应该被理解成：

`好结果 / 坏结果`

而应该理解成：

`适合作为历史样本 / 不适合作为历史样本`

### Exclude 后会发生什么

如果当前一局选择 Exclude：

- 本局记录仍然存在；
- 本局的局前输入仍然保留；
- 本局的分析结果和分析快照仍然保留；
- 本局的最终 Win / Loss 结果仍然保留；
- 但这一局不会进入后续有效历史样本。

这样既可以保留完整记录，又可以避免明显异常样本影响历史模型。

### 如果 Include / Exclude 选错了

如果当前一局还没有完成正式保存，可以在确认保存之前修正选择。

如果已经完成保存之后才发现：

- 本来应该 Include，却误选成 Exclude；
- 本来应该 Exclude，却误选成 Include；

应该使用：

`Historical Correction`

进行正式更正。

不要通过重新创建一局来“抵消”原记录。

### 与 Historical Regime 的区别

`Exclude` 和 `Historical Regime` 解决的是不同问题。

`Exclude`：

> 处理某一条具体记录是否适合作为历史样本。

`Historical Regime`：

> 处理一整个时期的环境已经发生变化，后续记录不应该继续和过去阶段混在一起统计。

因此，如果只是某一局异常，通常考虑 Include / Exclude。

如果直播间玩法环境发生了持续性的明显变化，则更应该考虑是否开启新的历史阶段，而不是把之后的每一局都逐条 Exclude。

## Maintenance

`Maintenance` 用于查看和维护当前角色相关的历史信息。

它主要用于：

- 查看当前角色；
- 查看当前历史阶段；
- 查看当前历史阶段的开始时间；
- 查看当前历史阶段的原因；
- 查看当前阶段中已经计入历史统计的样本数量；
- 在需要时开始新的历史阶段。

Maintenance 不是用于完成当前一局预测的主界面，也不是用来直接修改已经完成历史记录的入口。

### 为什么有些历史信息不会提前显示

Probability Calibration Tool 的一个核心原则是：

> **先记录当前判断，再查看可能影响判断的历史信息。**

因此，在当前一局尚未成功完成 `Calculate` 之前，Maintenance 会限制可能影响用户主观判断的定量或方向性历史信息。

例如，程序不会在这一阶段提前展示会明显影响判断的历史概率、胜负方向或类似统计结果。

这样做的目的是避免用户在输入当前一局主观概率之前，先被历史结果锚定。

### Calculate 前可以看到什么

在正式计算之前，Maintenance 允许显示不具有明显方向性的维护信息，例如：

- 当前角色；
- 当前历史阶段；
- 当前阶段开始时间；
- 当前阶段的原因；
- 当前阶段中计入历史统计的样本数量。

这些信息可以帮助用户确认自己当前处于哪个历史阶段，但不会直接告诉用户历史结果倾向 Win 还是 Loss。

### Maintenance 与 Historical Correction 的区别

`Maintenance`：

> 用于维护角色和历史阶段等结构性信息。

`Historical Correction`：

> 用于更正已经完成的具体历史记录。

如果只是想更正某一局的：

- Win / Loss；
- Include / Exclude；

应使用 `Historical Correction`，而不是 Maintenance。

### Maintenance 与 Restore 的区别

`Maintenance` 不用于恢复数据库备份。

如果需要从备份恢复数据，应使用：

`Restore`

### 什么时候应该进入 Maintenance

常见情况包括：

- 想确认当前角色处于哪个历史阶段；
- 想查看当前阶段是什么时候开始的；
- 想查看当前阶段为什么建立；
- 想确认当前阶段已经积累了多少计入历史的样本；
- 认为直播间积分玩法环境已经发生持续性变化，准备开始新的历史阶段。

### 不要为了查看历史方向而绕过正常流程

Maintenance 的限制是程序设计的一部分。

如果当前一局还没有完成正式计算，不应通过其他方式提前查看当前角色的方向性历史统计，再回来填写主观概率。

否则会破坏“先记录判断，再观察历史”的设计原则，也会降低长期主观概率记录的校准价值。

## Historical Regime（历史阶段）

`Historical Regime` 用于把同一个角色在不同环境时期产生的历史记录分开管理。

它解决的问题不是：

> 某一局是否异常。

而是：

> 一整段时期的环境已经发生持续性变化，新的对局不应该继续和旧时期的数据混在一起统计。

### 为什么需要历史阶段

直播间积分玩法中的实际环境可能发生变化。

例如：

- 玩法规则发生持续性调整；
- 赔率机制发生长期变化；
- 对局条件发生明显变化；
- 其他会持续影响结果分布的关键环境因素发生改变。

如果新环境和旧环境已经缺乏足够可比性，却仍然把所有历史记录混在一起统计，历史模型可能会失去代表性。

因此，程序允许为对应角色开始新的历史阶段。

### Current Regime

`Current Regime` 表示当前角色正在使用的历史阶段。

新的正常记录会归入当前历史阶段。

历史分析也会根据当前阶段中符合条件的历史记录建立。

### Start New Regime

当确认当前环境已经发生持续性、结构性的变化时，可以使用：

`Start New Regime`

开始新的历史阶段。

创建新阶段时，应根据程序要求填写相应原因。

原因应该尽量说明：

> 为什么从这一时点开始，新的对局不再适合继续与之前阶段的数据混合统计。

### 开始新阶段后，旧数据会发生什么

开始新的 Historical Regime：

> **不会删除旧历史数据。**

旧阶段中的记录仍然保留。

程序只是把之后的新记录归入新的历史阶段，并让当前阶段的历史统计基于新阶段的数据逐步重新积累。

因此：

`Start New Regime`

不是：

`Clear History`

也不是：

`Delete Old Data`

### 新阶段刚开始时为什么可能没有历史分析

一个新的历史阶段刚建立时，通常还没有足够的有效历史样本。

因此，即使选择：

`Use history`

也可能暂时没有正式 Historical Analysis。

随着当前阶段中被 Include 的记录逐渐增加，并达到程序规定的统计条件后，历史模型才会重新成为可用的正式分析。

这是正常现象。

### Historical Regime 与 Exclude 的区别

两者解决的是不同层级的问题。

#### Exclude

用于处理：

> 某一条具体记录是否适合作为历史样本。

例如，一局出现明确异常，但整体环境没有改变。

这时可以考虑：

`Exclude`

#### Start New Regime

用于处理：

> 从某个时间点开始，整个环境已经发生持续性变化。

这时不应该把之后每一局都逐条 Exclude，而应该考虑建立新的历史阶段。

可以简单理解为：

`单局异常`
→ `Exclude`

`长期环境变化`
→ `Start New Regime`

### 不要频繁开启新阶段

Historical Regime 不应该因为：

- 连续输了几局；
- 连续赢了几局；
- 历史概率暂时变得不符合预期；
- 想让统计结果重新开始；

就随意开启。

否则会把本应属于同一统计环境的数据人为切碎，使每个阶段都长期缺少足够样本。

只有当存在明确、持续、结构性的环境变化时，才应该考虑建立新的历史阶段。

### 新阶段与旧阶段的关系

历史阶段之间是连续的历史分段，而不是相互覆盖。

程序会保留：

- 旧阶段；
- 旧阶段中的历史记录；
- 新阶段；
- 新阶段之后产生的新记录。

这样既能保留完整历史，又能让当前统计尽量只反映当前环境。

## Historical Correction（历史记录更正）

`Historical Correction` 用于更正已经完成保存的历史记录。

它适合处理：

- `Win / Loss` 记录错误；
- 原本应该 `Include`，却误选成 `Exclude`；
- 原本应该 `Exclude`，却误选成 `Include`。

如果只是当前一局尚未完成，并且局前输入存在错误，应使用：

`Modify / Recalculate`

而不是 Historical Correction。

### 哪些内容可以更正

Historical Correction 只用于修正已经完成记录中的局后信息。

可以更正的内容包括：

- 最终结果：`Win / Loss`
- 是否计入历史：`Include / Exclude`
- 更正原因

原来的局前预测输入和正式分析快照不会因为 Historical Correction 被重新计算。

也就是说，历史更正的目标是：

> 修正“这局后来实际发生了什么、是否应该计入历史”。

而不是重新塑造当时已经记录下来的预测判断。

### 为什么不能直接覆盖旧记录

Probability Calibration Tool 不会把原历史记录直接无痕修改成新的内容。

进行 Historical Correction 后，程序会保留原记录，并建立一条与原记录存在明确更正关系的新记录。

这样做的目的，是让历史变化保持可追溯。

用户之后仍然能够知道：

- 原来记录了什么；
- 后来为什么进行了更正；
- 更正后的正式结果是什么。

因此：

> **Historical Correction 是审计式更正，不是直接覆盖。**

### 更正原因

进行 Historical Correction 时，需要填写更正原因。

更正原因用于说明：

> 为什么原来的已完成记录需要被修正。

例如：

- 最终结果误选；
- Include / Exclude 选错；
- 保存后才发现局后记录错误。

原因应尽量简洁、真实，并能够让之后查看记录的人理解这次更正为什么发生。

### 更正后的记录

完成 Historical Correction 后：

- 原记录仍然保留；
- 原记录会被标记为已经被后续记录替代；
- 新记录成为这次更正后的正式记录；
- 原来的预测输入和分析快照仍然被保留；
- 更正后的 Win / Loss 或 Include / Exclude 会用于后续相应统计。

程序不会把原来的历史过程完全抹掉。

### 哪些情况不应该使用 Historical Correction

不要使用 Historical Correction 来处理：

- 因为后来觉得自己当时的主观概率“不够好”；
- 因为历史分析后来发生变化；
- 因为想重新调整已经保存的预测；
- 因为某一局结果不符合自己的预期；
- 因为想人为改善历史统计结果。

Historical Correction 只应用于：

> 已经完成记录中的真实记录错误。

### Historical Correction 与 Modify / Recalculate 的区别

#### Modify / Recalculate

处理：

> 当前一局尚未完成时发现的局前输入错误。

例如：

- 角色选错；
- 主观概率输错；
- Win odds 输错；
- Lose odds 输错。

#### Historical Correction

处理：

> 当前一局已经完成保存以后发现的局后记录错误。

例如：

- Win / Loss 记错；
- Include / Exclude 记错。

可以简单记成：

`局前输入错误`
→ `Modify / Recalculate`

`已完成后的结果记录错误`
→ `Historical Correction`

### 基本更正流程

`Historical Correction`
→ `选择需要更正的已完成记录`
→ `修改允许更正的局后信息`
→ `填写更正原因`
→ `确认更正`

完成后，程序会保留原记录及其更正关系。

## Recovery（未完成单局恢复）

`Recovery` 用于继续处理之前已经开始、但尚未完成保存的一局。

例如：

- 程序在一局尚未完成时被关闭；
- Windows 意外重启；
- 程序发生异常退出；
- 当前一局已经完成 `Calculate`，但还没有记录最终结果并完成保存。

重新启动 Probability Calibration Tool 后，程序可能会检测到一条尚未完成的单局记录，并进入 Recovery 流程。

### Recovery 恢复的是什么

Recovery 恢复的是：

> **之前已经存在的同一条未完成记录。**

它不会因为程序重新启动而自动创建一条新的局。

恢复后，程序会继续使用原来已经保存的：

- 当前单局记录；
- 原有 Round；
- 已保存的分析快照；
- 已经完成的正式计算状态。

用户随后可以继续完成原来那一局尚未完成的操作。

### 为什么程序能够恢复

Probability Calibration Tool 在成功完成正式计算时，会先保存当前未完成单局及其分析快照。

因此，即使程序之后在当前一局完成之前退出，重新启动时仍然可以识别这条尚未结束的记录。

Recovery 的目的，是避免因为程序退出而：

- 丢失已经完成的正式分析；
- 被迫重新创建一局；
- 产生重复的历史记录。

### Recovery 后应该做什么

恢复成功后，应根据当前一局实际所处的状态继续操作。

例如，如果：

- 正式分析已经完成；
- 实际结果后来已经产生；

那么可以继续完成：

`Win / Loss`
→ `Include / Exclude`
→ `Confirm Save`

不需要重新创建 New Round。

### 不要重新创建一局来代替 Recovery

如果程序已经识别到一条未完成记录，应优先继续这条记录。

不要因为程序曾经退出，就手动把同一个实际对局重新记录成另一条 New Round。

否则可能造成：

- 同一实际对局被记录两次；
- 原有未完成记录仍然存在；
- 历史记录出现重复或不一致。

### Recovery 与 Restore 不是一回事

这两个功能名称容易混淆，但实际用途完全不同。

#### Recovery

用于：

> 继续一条已经存在、尚未完成的单局记录。

它处理的是“当前这一局还没做完”。

#### Restore

用于：

> 从程序维护的有效备份中恢复数据库。

它处理的是“数据文件需要恢复”。

因此：

`未完成的一局`
→ `Recovery`

`数据库需要从备份恢复`
→ `Restore`

### Recovery 不会做什么

Recovery 不会：

- 创建一条全新的历史记录来替代原记录；
- 把已经完成的历史记录重新变成未完成状态；
- 从备份文件替换当前数据库；
- 修改原来已经保存的预测输入；
- 自动改变已经保存的正式分析结果。

它的目标只是：

> **继续之前那条尚未完成的单局。**

### 如果 Recovery 失败

如果程序检测到未完成记录，但无法安全恢复，可能会进入相应的错误或数据安全流程。

此时不要通过手动修改数据库文件来强行解决。

应按照程序提供的恢复或数据安全提示处理。

更详细的异常恢复情况见后面的 `Data Safety / Emergency` 章节。

## Restore（备份恢复）

`Restore` 用于从程序维护的有效备份中恢复用户数据库。

它适合处理：

> 当前数据库发生问题，需要把程序数据恢复到某个已经保存并验证过的备份状态。

Restore 不是日常单局操作，也不是用于继续一条未完成记录的功能。

### Restore 会做什么

执行有效的 Restore 后，程序会使用选定并通过验证的备份数据库替换当前正在使用的数据库。

可以简单理解为：

`当前数据库`
→ `替换为备份中的数据库状态`

因此，如果恢复的是一个较早的备份：

> **数据库会回到该备份形成时所保存的状态。**

该备份之后才产生、但没有包含在备份中的记录，不会凭空继续存在于恢复后的数据库中。

因此，在执行 Restore 之前，应确认自己确实需要恢复到该备份状态。

### 程序为什么要先验证备份

Probability Calibration Tool 不会把任意文件直接当成有效数据库进行恢复。

备份需要通过程序规定的验证，确认其数据库结构和完整性满足恢复要求后，才能作为有效恢复来源。

这样可以降低以下风险：

- 使用损坏的备份替换当前数据库；
- 使用结构不兼容的数据文件；
- 把明显不完整的数据恢复成当前正式数据库。

具体的数据库验证规则将在技术参考文档中说明。

### Normal Restore

`Normal Restore` 用于在程序仍然可以正常进入相应恢复流程时，从有效备份恢复数据库。

通常只有在明确需要回退数据状态时才应该使用。

恢复之前，应认真确认所选择的备份。

### Emergency Restore

`Emergency Restore` 用于普通恢复流程无法正常使用、程序进入相应数据安全或紧急恢复状态时。

它属于异常情况下的数据恢复机制，而不是另一种日常 Restore 方式。

如果程序没有进入相应的紧急数据安全流程，一般不需要主动寻找或使用 Emergency Restore。

### Restore 与 Recovery 的区别

这是整个恢复系统中最重要的区别之一。

#### Recovery

处理：

> 一条已经开始但还没有完成的单局。

Recovery 继续的是原来那一局。

#### Restore

处理：

> 整个数据库需要从一个有效备份恢复。

Restore 会改变当前数据库所代表的数据状态。

因此：

`未完成单局`
→ `Recovery`

`数据库需要回退到备份状态`
→ `Restore`

> **Restore ≠ Recovery**

### Restore 与 Historical Correction 的区别

如果数据库本身没有问题，只是某一条已经完成的历史记录记错了：

例如：

- Win / Loss 错误；
- Include / Exclude 错误；

应该使用：

`Historical Correction`

而不是 Restore。

Restore 不应该被当作修改单条历史记录的手段。

可以简单区分为：

`单条已完成记录错误`
→ `Historical Correction`

`未完成单局`
→ `Recovery`

`数据库需要从备份恢复`
→ `Restore`

### 执行 Restore 前应该确认什么

在执行 Restore 之前，应至少确认：

1. 当前问题确实需要恢复整个数据库；
2. 不是一条记录可以通过 Historical Correction 解决的问题；
3. 不是一条未完成记录应该通过 Recovery 继续的问题；
4. 选择的是自己真正想恢复到的备份；
5. 能接受数据库恢复到该备份所代表的时间点和数据状态。

Restore 属于数据级操作，不建议在没有明确原因时尝试。

### 不要手工替换数据库文件

如果程序提供了正式 Restore 流程，应优先使用程序自己的恢复功能。

不建议：

- 手工删除当前数据库；
- 随意复制未知数据库覆盖当前数据；
- 修改 SQLite 数据库内容；
- 把未验证的数据文件当作正式备份使用。

正式 Restore 流程存在的目的之一，就是在替换当前数据库之前完成必要的验证和安全检查。

### Restore 完成后

成功恢复后，程序会基于恢复后的数据库继续运行。

此时看到的：

- 历史记录；
- 未完成记录状态；
- 历史阶段；
- 分析快照；
- 其他数据库内容；

都会以恢复后的数据库状态为准。

如果恢复后发现内容比恢复前更早，应首先确认：

> 所选择的备份本身是否就是较早时间创建的备份。

这不一定代表 Restore 失败。

### 应该使用哪个恢复功能？

| 情况 | 应使用的功能 |
| --- | --- |
| 当前一局还没完成，程序之前退出了 | `Recovery` |
| 某条已完成记录的结果记错了 | `Historical Correction` |
| 当前数据库需要恢复到有效备份 | `Restore` |
| 普通恢复流程无法正常进行，并进入程序的数据安全紧急流程 | `Emergency Restore` |

## Data Safety / Emergency 情况

Probability Calibration Tool 在检测到数据状态异常、未完成单局无法正常恢复，或普通恢复流程无法安全继续时，可能进入相应的数据安全或紧急恢复界面。

这些界面不是日常使用流程的一部分。

如果程序进入：

- `Data Safety`
- `Recovery Error`
- `Emergency Recovery`
- `Emergency Restore`

应优先按照程序当前提供的安全流程处理，而不是手工修改数据库文件。

### Data Safety

`Data Safety` 是程序的数据安全界面。

它用于在程序发现当前数据状态需要额外检查或恢复处理时，阻止用户继续按照普通单局流程操作。

进入 Data Safety 并不代表所有数据一定已经丢失。

它表示：

> 程序认为当前状态不适合继续按正常流程运行，需要先处理数据安全问题。

此时不建议：

- 手工删除数据库；
- 随意覆盖数据文件；
- 修改 SQLite 表内容；
- 通过创建新局绕过当前异常状态；
- 反复复制未知备份尝试覆盖。

应优先使用程序提供的恢复流程。

### Recovery Error

`Recovery Error` 表示程序检测到未完成单局，但无法按照正常 Recovery 流程安全继续。

这与普通的：

`Recovery`

不同。

普通 Recovery 的目标是继续之前那条未完成单局。

Recovery Error 则表示：

> 当前未完成记录或相关状态存在问题，程序不能直接把它当作正常未完成单局继续。

此时不应手动重新创建一条相同 New Round 来“顶替”原记录。

程序可能需要进入进一步的数据安全或紧急恢复流程。

### Emergency Recovery

`Emergency Recovery` 用于普通未完成单局恢复无法安全完成时的紧急恢复场景。

它仍然属于：

> 未完成单局恢复体系。

而不是数据库备份恢复体系。

因此需要继续区分：

`Recovery / Emergency Recovery`
→ 处理未完成单局

`Restore / Emergency Restore`
→ 处理数据库备份恢复

Emergency Recovery 只有在程序进入相应异常状态时才具有意义，不应作为日常功能使用。

### Emergency Restore

`Emergency Restore` 用于普通数据库恢复流程无法正常进行，但程序仍需要从经过验证的备份中恢复数据的异常场景。

它属于：

> 数据库恢复体系。

与普通 `Restore` 的核心目标相同，都是恢复数据库状态，但 Emergency Restore 面向的是普通恢复路径已经无法安全使用的情况。

不要因为想回退一条记录、重新选择 Win / Loss 或修改 Include / Exclude，就使用 Emergency Restore。

这些问题应分别使用正常的单局或历史更正流程。

### Normal 与 Emergency 的区别

可以简单理解为：

| 类型 | 正常流程 | 异常流程 |
| --- | --- | --- |
| 未完成单局 | `Recovery` | `Emergency Recovery` |
| 数据库备份恢复 | `Restore` | `Emergency Restore` |

Emergency 功能不是“更高级版本”的普通功能。

它只用于程序检测到正常恢复路径无法安全继续的异常情况。

### 遇到 Data Safety 时的基本原则

如果程序进入 Data Safety 或 Emergency 流程，建议遵循：

1. 不手工修改数据库；
2. 不删除当前用户数据目录；
3. 不用新的 New Round 试图绕过未完成记录；
4. 不把未知 SQLite 文件直接覆盖当前数据库；
5. 优先按照程序提供的 Recovery / Restore 路径处理；
6. 如果仍然无法恢复，应保留当前数据目录和日志，再进行故障排查。

### 保留日志和数据

如果出现无法自行解决的数据安全问题，不建议第一时间删除：

`%LOCALAPPDATA%\ProbabilityCalibrationTool\`

因为其中可能包含：

- 当前数据库；
- 备份；
- 日志；
- 程序设置；
- 恢复问题所需要的诊断信息。

在排查完成之前，保留这些文件通常比直接删除更有价值。

如果需要把日志或数据库交给其他人协助排查，应先确认其中是否包含自己不希望共享的数据。

## 界面语言与中文语言包

Probability Calibration Tool 的界面语言分为：

- 内置语言；
- 外部语言包。

当前程序内置：

`English`

当前提供的外部语言包：

`Simplified Chinese (zh_CN)`

### English 是内置语言

English 直接包含在主程序中。

因此：

- 不需要安装 English 语言包；
- 删除外部语言包不会影响 English；
- 如果没有可用的外部语言包，程序仍然可以正常使用 English 界面。

English 是程序的默认界面语言。

### Simplified Chinese 是外部语言包

简体中文不直接打包在主程序中，而是通过独立的 `.qm` 文件提供。

正式简体中文语言包中的核心文件为：

`probability_calibration_tool_zh_CN.qm`

语言包需要安装到：

`%LOCALAPPDATA%\ProbabilityCalibrationTool\languages\`

如果 `languages` 文件夹不存在，可以自行创建。

### 安装简体中文语言包

1. 前往项目的 GitHub Releases。
2. 下载与当前主程序版本对应的：

   `ProbabilityCalibrationTool-LanguagePack-zh_CN-<version>.zip`

3. 解压语言包。
4. 得到：

   `probability_calibration_tool_zh_CN.qm`

5. 将该文件复制到：

   `%LOCALAPPDATA%\ProbabilityCalibrationTool\languages\`

最终应类似：

`%LOCALAPPDATA%\ProbabilityCalibrationTool\languages\probability_calibration_tool_zh_CN.qm`

6. 启动 Probability Calibration Tool。
7. 打开：

   `Interface Language...`

8. 选择：

   `Simplified Chinese`

9. 点击：

   `Confirm`

10. 关闭程序并重新启动。

重新启动后，界面会使用简体中文。

### 为什么需要重新启动

Probability Calibration Tool 的界面语言采用：

> **确认选择后，在下一次启动时生效**

的方式。

因此，在 `Interface Language...` 中选择另一种语言并确认后，当前已经打开的窗口不会立即全部切换语言。

需要关闭并重新启动程序，新的界面语言才会正式生效。

这属于正常设计，不是程序没有保存语言设置。

### 切换回 English

如果希望恢复 English：

1. 打开 `Interface Language...`
2. 选择 `English`
3. 点击 `Confirm`
4. 关闭并重新启动程序

English 不依赖任何外部语言包。

因此，即使已经删除简体中文 `.qm` 文件，也仍然可以继续使用 English。

### 语言包版本应与程序版本对应

建议始终使用：

> **与当前主程序来自同一个 Release 的语言包。**

例如：

`主程序版本 X`
→ `使用版本 X Release 中提供的 zh_CN 语言包`

不建议混用不同版本。

原因是新版本程序可能：

- 增加新的界面文本；
- 修改已有文本；
- 增加新的窗口或提示；
- 调整翻译上下文。

旧语言包即使能够被程序读取，也可能缺少较新程序需要的翻译。

因此：

> **能够加载，不等于语言包与当前版本完全兼容。**

### 如果语言包没有安装

如果选择了 Simplified Chinese，但程序找不到可用的简体中文语言包，程序应继续使用可用的内置 English 界面，而不是因为缺少语言包而无法启动。

此时应检查：

1. `.qm` 文件是否已经解压；
2. 文件名是否为：

   `probability_calibration_tool_zh_CN.qm`

3. 文件是否放在：

   `%LOCALAPPDATA%\ProbabilityCalibrationTool\languages\`

4. 是否误把 ZIP 本身直接放进 `languages`；
5. 是否把语言包放到了程序 EXE 所在目录，而不是用户数据目录；
6. 是否使用了与当前程序版本对应的语言包。

修正后重新启动程序。

### 如果语言包损坏或无效

如果外部语言包本身无法正常加载，程序不应该依赖这个损坏的语言包继续运行。

在这种情况下，程序会优先保证可以使用内置 English 界面继续启动。

用户可以：

1. 关闭程序；
2. 删除或替换有问题的 `.qm` 文件；
3. 从对应 GitHub Release 重新下载语言包；
4. 将新的 `.qm` 文件重新放入 `languages`；
5. 再次启动程序。

### 不要修改语言包文件名

当前简体中文语言包使用固定文件名：

`probability_calibration_tool_zh_CN.qm`

不建议自行重命名。

程序需要按照规定的位置和语言包名称识别相应语言资源。

### 语言包与程序文件是分开的

主程序位于：

> 用户自行解压的 Probability Calibration Tool 程序目录

语言包位于：

`%LOCALAPPDATA%\ProbabilityCalibrationTool\languages\`

因此：

- 移动整个程序文件夹不会自动移动语言包；
- 删除程序文件夹不会自动删除已经安装的语言包；
- 重新下载同一程序后，本地语言包可能仍然保留。

这与程序的数据库、设置和其他用户数据采用独立用户目录保存的设计一致。

### 语言问题速查

| 情况 | 处理方式 |
| --- | --- |
| 第一次启动是 English | 正常，English 是内置默认语言 |
| 想使用简体中文 | 安装对应版本的 zh_CN `.qm`，然后在 Interface Language 中选择中文并重启 |
| 选择中文后当前窗口没变化 | 正常，需要重新启动程序 |
| 重启后仍然是 English | 检查语言包文件名、安装路径和文件有效性 |
| 中文包损坏或缺失 | 程序可回退使用内置 English |
| 想切回 English | 选择 English，确认并重启 |
| 升级主程序后 | 建议同时使用新版本 Release 对应的语言包 |

## 键盘与快捷操作

Probability Calibration Tool 可以使用键盘在界面中的可操作控件之间移动焦点。

### Tab

按：

`Tab`

可以将焦点移动到当前界面中的下一个可操作项。

在连续填写一局数据时，可以使用 Tab 在输入框、选项和按钮之间快速切换，减少鼠标操作。

例如，在局前预测输入区域中，可以通过 Tab 依次移动到后续可操作控件。

### 使用建议

如果习惯键盘输入，可以采用：

`输入内容`
→ `Tab`
→ `输入下一项`
→ `Tab`
→ `继续操作`

这种方式完成一局中的大部分表单填写。

具体焦点顺序取决于当前界面的可操作控件和程序状态。

### 关于其他快捷键

本指南只记录已经确认存在并具有实际用途的快捷操作。

如果后续版本增加新的显式快捷键，会在这里继续补充。

## 数据保存、备份与迁移

Probability Calibration Tool 将：

- 程序本体；
- 用户长期数据；

分开保存。

因此，移动或删除程序文件夹，并不等于移动或删除用户数据。

### 程序本体在哪里

程序本体位于用户自己解压正式发布 ZIP 的位置。

例如，解压后的目录中会包含：

`ProbabilityCalibrationTool.exe`

以及：

`_internal`

这一整个目录属于程序文件。

如果只是希望把程序从一个位置移动到另一个位置，应移动整个 `ProbabilityCalibrationTool` 文件夹，而不是只移动 EXE。

### 用户数据在哪里

Probability Calibration Tool 的用户数据位于：

`%LOCALAPPDATA%\ProbabilityCalibrationTool\`

这里保存程序长期使用过程中产生或使用的数据，例如：

- 单局记录；
- 历史数据；
- 分析快照；
- 本地备份；
- 程序设置；
- 日志和诊断信息；
- 外部语言包。

因此：

> **程序目录与用户数据目录不是同一个位置。**

### 删除程序不会自动删除用户数据

如果只删除：

> 解压后的 `ProbabilityCalibrationTool` 程序文件夹

并不会自动删除：

`%LOCALAPPDATA%\ProbabilityCalibrationTool\`

中的用户数据。

因此以后重新下载并运行兼容版本的程序时，原来的用户数据仍可能继续存在。

这也是为什么 Probability Calibration Tool 更准确地说是：

> **免安装发布包**

而不是“所有数据都跟随 EXE 的完全便携模式”。

### 如果想彻底删除程序

如果只是希望删除程序本体：

> 删除解压后的程序文件夹即可。

如果希望连自己的 Probability Calibration Tool 用户数据也一起彻底删除，则还需要另外处理：

`%LOCALAPPDATA%\ProbabilityCalibrationTool\`

中的数据。

在删除用户数据目录之前，应先确认：

- 不再需要历史记录；
- 不再需要数据库；
- 不再需要本地备份；
- 不再需要设置和语言包。

删除用户数据后，程序自身的 Restore 功能也无法从已经被删除的本地备份中恢复这些数据。

### 自动备份不是系统重装备份

Probability Calibration Tool 会维护本地备份。

这些备份主要用于：

> 程序数据本身出现问题时进行恢复。

但如果：

- Windows 系统盘损坏；
- 重装 Windows 时清除了用户目录；
- 硬盘发生故障；
- 整个 `%LOCALAPPDATA%` 被删除；

保存在同一台电脑上的本地备份也可能一起丢失。

因此，如果历史数据具有长期保存价值，建议另外保存一份独立副本。

例如保存到：

- 另一块硬盘；
- U 盘；
- 其他自己信任的备份位置。

### 手动备份用户数据

如果需要在系统操作之前保存自己的 Probability Calibration Tool 数据，建议先：

1. 正常关闭 Probability Calibration Tool；
2. 确认程序已经退出；
3. 找到：

   `%LOCALAPPDATA%\ProbabilityCalibrationTool\`

4. 将需要保存的用户数据复制到另一个安全位置。

如果希望尽量完整地保存当前用户环境，可以备份整个 `ProbabilityCalibrationTool` 用户数据目录。

这样不仅可以保留历史数据，也可以同时保留其中的设置、语言资源和其他用户文件。

### 为什么备份前建议关闭程序

在程序运行期间，数据库和其他运行数据可能正在被使用。

因此进行手动文件级备份时，建议先关闭程序，再复制用户数据。

这样可以避免在程序仍然使用相关文件时进行不必要的文件操作。

程序自身提供的自动备份和 Restore 则按照程序自己的数据安全机制处理。

### 重装 Windows 前

如果准备重装 Windows，并且希望保留 Probability Calibration Tool 数据，不应只保存：

- 程序 ZIP；
- `ProbabilityCalibrationTool.exe`；
- 整个程序解压目录。

这些主要是程序文件。

还需要另外备份：

`%LOCALAPPDATA%\ProbabilityCalibrationTool\`

中的用户数据。

否则重新下载程序以后，虽然程序本身仍然可以运行，但原来的历史记录可能已经不在电脑上。

### 更换电脑

更换电脑时，需要分别考虑：

#### 程序本体

可以在新电脑上重新从 GitHub Releases 下载正式发布包。

没有必要把旧电脑上的 EXE 单独复制过去。

#### 用户数据

如果希望继续使用以前积累的记录，则需要另外迁移原来的用户数据。

建议：

1. 在旧电脑上关闭 Probability Calibration Tool；
2. 备份原来的用户数据；
3. 在新电脑上安装或解压兼容版本的 Probability Calibration Tool；
4. 再按照经过确认的数据迁移方式恢复相应用户数据。

如果源程序版本和目标程序版本存在较大差异，应优先确认数据兼容性，而不是直接覆盖未知版本的数据文件。

### 程序升级通常不需要删除用户数据

更新 Probability Calibration Tool 时，通常只需要：

1. 下载新的正式发布包；
2. 解压新的程序文件；
3. 使用新版本程序。

用户长期数据位于独立的 `%LOCALAPPDATA%` 目录，因此程序本体升级和用户数据本身是分开的。

但是：

> 不应为了“干净升级”而随意删除用户数据目录。

如果某个版本需要特殊的数据迁移步骤，应以该版本 Release 和相关文档中的说明为准。

### Restore 与手动文件备份

程序自身的：

`Restore`

用于：

> 从经过程序验证的数据库备份恢复当前数据库。

而手动复制整个用户数据目录主要用于：

> Windows 重装、换电脑、长期离线备份等更大范围的数据保存。

两者用途并不完全相同。

如果只是数据库出现问题，应优先使用程序正式提供的 Restore 流程，而不是手工覆盖 SQLite 数据库文件。

### 不要手工编辑数据库

用户数据中包含程序使用的数据库。

不建议通过：

- SQLite 编辑器；
- 文本编辑器；
- 第三方数据库管理工具；

直接修改其中的数据。

如果需要：

- 更正已经完成的记录；
- 恢复未完成单局；
- 从备份恢复数据库；

应分别优先使用程序提供的：

- `Historical Correction`
- `Recovery`
- `Restore`

这样可以保留程序规定的数据关系和安全检查。

### 数据隐私

数据库、备份和日志可能包含自己的历史使用记录。

如果需要将它们：

- 上传到 GitHub Issue；
- 发送给其他开发者；
- 提供给 AI 或其他人排查问题；

应先确认其中是否包含自己不希望共享的信息。

不要因为文件位于程序数据目录中，就默认其中所有内容都适合公开。

### 我想做什么？

| 目的 | 应处理的内容 |
| --- | --- |
| 把程序移动到另一个文件夹 | 移动整个程序解压目录 |
| 删除程序，但保留历史数据 | 只删除程序目录 |
| 完全删除程序和自己的数据 | 删除程序目录，并在确认后另外删除用户数据目录 |
| 数据库出现问题 | 优先使用 `Restore` |
| 一条未完成记录需要继续 | 使用 `Recovery` |
| 已完成记录结果记错 | 使用 `Historical Correction` |
| 重装 Windows | 另外备份用户数据目录 |
| 更换电脑并保留历史记录 | 重新下载程序，并迁移用户数据 |
| 长期防止硬盘或系统故障导致数据丢失 | 将用户数据另外备份到独立位置 |

## 常见问题与故障排查

### 为什么我选择了 Use history，却没有看到 Historical Analysis？

选择 `Use history` 只表示当前一局希望参考历史模型，并不代表历史模型一定已经满足正式显示条件。

常见原因包括：

- 当前角色的有效历史样本还不够；
- 当前历史阶段刚开始；
- 虽然已有一些记录，但历史模型的不确定性仍然过高；
- 部分记录选择了 `Exclude`，因此不会计入有效历史样本。

这通常是正常设计，而不是程序故障。

程序只有在历史数据达到规定的统计条件后，才会显示正式 Historical Analysis。

### 为什么 Calculate 前看不到历史胜率或历史方向？

这是程序有意设计的限制。

Probability Calibration Tool 遵循：

> **先记录判断，再观察历史。**

在当前一局成功完成 `Calculate` 之前，程序会限制可能明显影响用户主观判断的方向性历史信息。

这样可以减少历史结果对当前主观概率输入的干扰。

### 为什么主观概率和历史概率不一样？

这是完全正常的。

两者来自不同的信息来源：

- `Subjective Analysis` 来自用户针对当前一局作出的主观判断；
- `Historical Analysis` 来自当前角色、当前历史阶段中的有效历史记录。

程序不会要求两个模型得出相同结果，也不会自动把它们平均或合并。

例如：

`Subjective probability = 70%`

`Historical probability = 60%`

可以同时正常存在。

### 为什么程序没有给我一个最终的“综合概率”？

这是产品设计的一部分。

Probability Calibration Tool 有意保持：

`Subjective Analysis`

与：

`Historical Analysis`

彼此独立。

程序不会自动：

- 平均；
- 加权；
- 覆盖；
- 合并；

两套概率。

这样可以让用户分别看到自己的当前判断和历史统计信息，而不是隐藏两者之间的差异。

### 我输入了 0% 或 100%，为什么程序仍然可以计算？

主观概率的原始输入允许：

`0% – 100%`

程序会保留用户实际输入的原始值。

对于数学计算中的极端边界，内部会按照既定规则进行安全处理。

这不会把用户原来记录的 0% 或 100% 偷偷修改成另一个输入值。

具体数学规则见技术参考文档。

### Exclude 会把这一局删除吗？

不会。

`Exclude` 表示：

> 当前这一局仍然完整保存，但不参与后续历史统计。

它不会删除：

- 当前单局记录；
- 主观概率；
- 赔率；
- 分析快照；
- Win / Loss 结果。

只是这条记录不会作为有效历史样本参与后续 Historical Analysis。

### 什么时候应该使用 Exclude？

Exclude 适合处理：

> 某一条具体记录存在明确异常，使它不适合作为正常历史样本。

不应该仅仅因为：

- 这一局输了；
- 结果与自己的判断不同；
- 历史概率因此下降；
- 统计结果变得不符合预期；

就选择 Exclude。

如果不是单局异常，而是整个直播间积分玩法环境已经发生持续性变化，应考虑 Historical Regime，而不是不断 Exclude 后续记录。

### Start New Regime 会删除以前的历史记录吗？

不会。

开启新的 Historical Regime：

> 只会开始一个新的历史阶段。

以前阶段中的记录仍然保留。

新的历史记录会逐渐在新阶段中重新积累，当前历史模型主要依据当前阶段中的有效记录建立。

### 为什么开始新 Regime 后历史分析又没有了？

新的历史阶段刚开始时，可用样本通常很少。

因此即使以前已经积累了很多历史数据，新阶段仍然需要重新积累属于当前阶段的有效样本。

在达到程序规定的统计条件之前，没有正式 Historical Analysis 是正常现象。

### Calculate 之后发现主观概率或赔率输错了怎么办？

如果当前一局还没有完成保存，应使用：

`Modify`
→ 修正输入
→ `Recalculate`

不要重新创建一个 New Round 来代替原来的这一局。

成功 Recalculate 后，当前一局仍然是原来的同一条记录，只是正式输入和分析结果得到合法更新。

### 为什么 Modify 后还要 Recalculate？

因为：

> 修改输入本身，并不等于新的正式分析已经完成。

只有成功执行：

`Recalculate`

以后，修改后的输入和对应的新分析结果才成为当前一局新的正式状态。

这样可以避免输入已经变化，但界面仍然显示旧分析结果的数据不一致。

### 已经完成保存以后，发现 Win / Loss 记错了怎么办？

使用：

`Historical Correction`

不要再创建一条相反结果的新记录来“抵消”原来的记录。

Historical Correction 用于更正：

- Win / Loss；
- Include / Exclude；

并保留原记录和更正关系。

### Historical Correction 能修改我当时填写的主观概率或赔率吗？

不能用它来重新塑造已经完成记录的局前预测。

Historical Correction 的职责是修正已经完成后的局后信息，例如：

- 实际 Win / Loss 记录错误；
- Include / Exclude 记录错误。

当时已经保存的预测输入和分析快照会继续作为原始记录保留。

### 程序意外退出后，我是不是要重新记录这一局？

不一定。

如果程序已经成功保存了当前未完成单局和分析快照，重新启动后可能进入：

`Recovery`

Recovery 会继续：

> 原来的同一条未完成记录。

不要在程序已经提供 Recovery 的情况下，又手工新建一个相同的 New Round，否则可能产生重复记录。

### Recovery 和 Restore 有什么区别？

这是两个完全不同的功能。

`Recovery`

> 继续之前尚未完成的一局。

`Restore`

> 从有效备份恢复整个数据库。

可以简单记成：

`一局没做完`
→ `Recovery`

`数据库需要从备份恢复`
→ `Restore`

### Historical Correction 和 Restore 有什么区别？

如果只是某一条已完成记录记错：

→ `Historical Correction`

如果整个数据库需要恢复到某个备份状态：

→ `Restore`

不要为了修正一条 Win / Loss 就恢复整个数据库。

### 为什么程序进入了 Data Safety？

Data Safety 表示：

> 程序认为当前数据状态不适合继续按照普通流程运行，需要先处理数据安全问题。

这并不自动意味着数据已经全部丢失。

进入 Data Safety 后，不建议：

- 手工删除数据库；
- 修改 SQLite 数据；
- 随意覆盖备份；
- 创建新局绕过异常状态。

应优先使用程序提供的 Recovery / Restore / Emergency 流程。

### Recovery Error 是什么意思？

它表示：

> 程序发现了未完成记录，但无法按照正常 Recovery 流程安全继续。

这时不要重新创建相同的一局来顶替原记录，也不要手工修改数据库。

应继续按照程序的数据安全流程处理。

### Emergency Recovery 和 Emergency Restore 有什么区别？

`Emergency Recovery`

> 属于未完成单局恢复体系。

`Emergency Restore`

> 属于数据库备份恢复体系。

可以记成：

| 情况 | 功能 |
| --- | --- |
| 正常继续未完成单局 | `Recovery` |
| 未完成单局恢复异常 | `Emergency Recovery` |
| 正常从备份恢复数据库 | `Restore` |
| 普通数据库恢复流程异常 | `Emergency Restore` |

Emergency 功能只用于异常情况，不是日常功能的“加强版”。

### 为什么第一次启动程序是 English？

这是正常的。

Probability Calibration Tool 内置的默认界面语言是：

`English`

Simplified Chinese 通过独立外部语言包提供。

如果需要中文，需要另外安装对应版本的 zh_CN 语言包。

### 我已经选择 Simplified Chinese，为什么界面没有马上变成中文？

语言切换需要重新启动程序后生效。

正常流程是：

`Interface Language...`
→ `Simplified Chinese`
→ `Confirm`
→ 关闭程序
→ 重新启动

当前已经打开的窗口不会立即整体切换语言。

### 重启以后仍然是 English 怎么办？

检查：

1. 是否已经解压语言包；
2. 是否得到：

   `probability_calibration_tool_zh_CN.qm`

3. 文件是否放在：

   `%LOCALAPPDATA%\ProbabilityCalibrationTool\languages\`

4. 是否误把 ZIP 本身放进了 `languages`；
5. 文件名是否被修改；
6. 是否使用了与主程序对应版本的语言包。

如果语言包缺失或无法正常加载，程序仍然可以使用内置 English 界面。

### 为什么只移动 EXE 后程序打不开？

正式发布包采用目录式打包。

`ProbabilityCalibrationTool.exe`

需要与：

`_internal`

保持原有目录结构。

不要只把 EXE 单独复制出去。

如果需要移动程序，请移动整个：

`ProbabilityCalibrationTool`

文件夹。

### 删除程序文件夹以后，为什么数据还在？

这是正常设计。

程序本体和用户数据分开保存。

程序本体：

> 位于你解压 ZIP 的位置。

用户数据：

`%LOCALAPPDATA%\ProbabilityCalibrationTool\`

因此：

> 删除程序文件夹 ≠ 删除用户数据。

如果希望彻底删除自己的数据，需要另外处理用户数据目录。

### 重装 Windows 前只保存程序 ZIP 可以吗？

如果希望保留历史记录，不可以只保存程序 ZIP。

程序可以以后重新下载。

真正需要另外保护的是：

`%LOCALAPPDATA%\ProbabilityCalibrationTool\`

中的用户数据。

系统重装前，应先备份自己的用户数据。

### 我可以直接用 SQLite 工具修改数据库吗？

不建议。

Probability Calibration Tool 已经提供：

- `Historical Correction`
- `Recovery`
- `Restore`

等正式的数据处理流程。

直接修改 SQLite 数据可能破坏：

- 记录之间的关系；
- 分析快照；
- 更正关系；
- 恢复状态；
- 数据完整性。

如果遇到程序没有提供正常处理方式的问题，应先保留数据库和日志进行排查，而不是直接编辑数据库。

### 遇到无法解决的问题时应该保留什么？

在排查完成之前，不要急着删除：

`%LOCALAPPDATA%\ProbabilityCalibrationTool\`

建议保留：

- 当前用户数据；
- 本地备份；
- 日志；
- 相关程序版本信息。

这些内容可能用于判断问题发生在哪里。

如果需要把数据库或日志提供给其他人协助排查，应先确认其中是否存在自己不希望共享的信息。
