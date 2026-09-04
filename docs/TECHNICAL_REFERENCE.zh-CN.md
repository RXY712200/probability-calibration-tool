# Probability Calibration Tool 技术参考

本文档描述 Probability Calibration Tool 当前正式实现的技术行为，包括数学模型、信息隔离、Workflow、SQLite 持久化、Recovery、Historical Correction、Backup / Restore、启动安全和运行时边界。

本文面向后续维护源码的开发者，以及需要在不首先通读全部源码的情况下理解产品核心合同的人。

普通用户的操作方式请参阅 [用户指南](USER_GUIDE.zh-CN.md)。

`SPEC_1.0.md` 是 1.0 的历史设计与验收基线；本文档描述当前正式实现。若本文档、源码和自动化测试之间出现冲突，不应直接假定其中任意一方正确，而应停止修改并结合源码、测试和历史规格确认预期合同。

## 1. 系统概览

Probability Calibration Tool 是一个 Windows 本地桌面工具，用于《The Binding of Isaac（以撒的结合）》抖音直播间积分玩法中的重复二元结果记录、概率分析与概率校准。

当前产品不是通用可配置概率平台，也不是游戏 MOD、直播间插件或自动参与工具。

主要技术栈：

```text
Windows 11 x64
Python 3.13
PySide6 / Qt
SQLite
SciPy
uv
pytest
Ruff
PyInstaller onedir
```

当前 SQLite：

```text
PRAGMA user_version = 1
```

数据库固定包含六张业务表：

```text
characters
history_regimes
rounds
round_analysis_snapshots
character_stats
meta
```

系统包含两个相互独立的概率模型：

```text
Subjective Model
Historical Model
```

其中：

- Subjective Model 根据用户局前输入的主观概率计算；
- Historical Model 根据同一 Character、同一 Historical Regime 中符合条件的已完成历史 Round 计算；
- 两个模型在数学上相互独立；
- Historical Model 是否向用户显示，还受到 Anti-Anchoring 信息隔离合同限制。

典型单局生命周期：

```text
DRAFT
  ↓
Calculate
  ↓
pending Round + committed Snapshot
  ↓
PENDING_LOCKED
  ↓
Win / Loss
Include / Exclude
  ↓
CONFIRM_SAVE
  ↓
completed Round
```

几个容易混淆的概念必须严格区分：

```text
Modify / Recalculate
    修改尚未完成的当前 prediction revision

Historical Correction
    更正已经 completed 的局后事实，并建立审计 replacement chain

Recovery
    恢复当前 live database 中未完成的 pending Round

Restore
    使用 verified backup 替换整个 live database

Regime
    对历史数据进行阶段分段，不删除旧历史
```

应用本身内置 English。

简体中文使用外部：

```text
probability_calibration_tool_zh_CN.qm
```

语言包。

语言切换为 restart-only。

---

## 2. 产品合同与核心不变量

以下规则属于当前正式产品合同。修改这些规则通常不能仅视为普通内部重构。

### 2.1 两个模型独立

Subjective Model 与 Historical Model 不互相修改输入或结果。

Historical probability 不会反向修改用户输入的 Subjective probability。

Subjective probability 也不会作为 Historical posterior 的 prior。

### 2.2 Subjective raw value 必须保留

用户可以输入：

```text
0 ... 100
```

数据库必须保存原始：

```text
p_h_raw
```

数学计算时再将其限制到：

```text
1 ... 99
```

不能把原始 `0` 自动改存为 `1`，也不能把 `100` 自动改存为 `99`。

### 2.3 Historical Model 使用 Jeffreys Beta

Historical probability 当前采用 Jeffreys prior：

```text
alpha = wins + 0.5
beta  = losses + 0.5
```

并计算 95% credible interval。

### 2.4 Historical readiness 是独立 Gate

Historical Model 只有同时满足：

```text
sample size >= 20
AND
credible interval width <= 0.25
```

才进入：

```text
VALID
```

状态。

否则根据是否存在历史分别为：

```text
NO_HISTORY
INSUFFICIENT
```

不能把：

```text
“有历史”
```

等价解释成：

```text
“Historical Analysis 可以正式参考”
```

### 2.5 Anti-Anchoring

在一次成功 Calculate 之前，正常 UI 不得向用户暴露方向性或定量历史信息。

例如不能提前显示：

```text
wins
losses
win rate
Historical probability
credible interval
EV
```

Maintenance 在 Calculate 前只允许显示非方向性信息，例如：

```text
Character
Current regime
Started locally
Reason
Included sample count
```

### 2.6 Calculate 必须先持久化再展示

成功 Calculate 必须先在同一事务中持久化：

```text
pending Round
+
RoundAnalysisSnapshot
```

并成功 commit。

只有 commit 成功之后，Application 才能构造正式 Locked Analysis View 给 UI。

因此：

```text
“用户看到分析”
```

意味着这一版 prediction 已经具有 durable database identity。

### 2.7 Modify 使用同一个 Round ID

当前 pending Round 的 Modify / Recalculate：

```text
不创建新 Round
```

而是：

```text
same round_id
same created_at
revision_count += 1
```

并更新同一个 Snapshot record。

### 2.8 未 Recalculate 的 Candidate 不属于持久事实

PENDING_EDIT 中用户修改的输入只存在于内存。

只有 Recalculate 成功后才成为新的 committed prediction revision。

程序在 PENDING_EDIT 中崩溃时，未提交 Candidate 可以丢失；此前 committed prediction 必须保持安全。

### 2.9 Result knowledge 会关闭 Prediction revision

用户一旦正式选择：

```text
Win
Loss
```

当前 Round 的 prediction revision 必须关闭。

之后不能再 Modify / Recalculate。

Recovery 后同样采用保守规则，将 prediction revision 直接锁死。

### 2.10 Include 不等于删除

```text
Exclude
```

只表示这个 completed Round 不参与后续 Historical Model。

Round 本身仍保留在数据库中。

### 2.11 Regime 不等于删除历史

Start New Regime：

```text
结束旧 Regime
创建新 Regime
```

旧 Round、旧 Snapshot 和旧 Stats 都继续保留。

不同 Regime 的 Historical samples 不混合。

### 2.12 Completed history 不允许原地覆盖

已经 completed 的历史事实不能通过直接 UPDATE 抹掉原错误值。

Historical Correction 必须：

```text
Original A
completed → voided

Replacement B
completed
supersedes_round_id = A
```

形成审计链。

### 2.13 Correction 只能改局后事实

Historical Correction 当前只允许更正：

```text
result
include_character_history
reason
```

不能通过 Correction 修改：

```text
Character
Regime
Subjective probability
Odds
reference_history
Prediction Snapshot
```

### 2.14 Correction 不重新计算 Snapshot

Replacement B 必须复制 A 的 Snapshot，仅替换：

```text
round_id
```

不能因为 Correction 发生在更晚时间，就使用当时的新历史重新运行 Core。

### 2.15 Recovery 继续原 Round

Recovery 必须继续：

```text
同一个 pending Round
同一个 Snapshot
同一个 round_id
```

并且：

```text
不运行 Core
不生成 ID
不取得新 calculation time
不写数据库
```

### 2.16 Recovery 不等于 Restore

Recovery：

```text
读取当前 live database
继续未完成单局
```

Restore：

```text
使用 backup 替换 live database
```

二者不能互换术语。

### 2.17 Restore 必须验证 Candidate

Backup 文件不能仅凭：

```text
.db
```

扩展名成为合法 Restore source。

Restore candidate 必须经过：

```text
SQLite health
Schema compatibility
Application invariants
Stats validation / repair
```

等检查。

### 2.18 Stats 是 Derived Cache

`character_stats` 是可以从 `rounds` 确定性重建的派生缓存。

Historical Model 本身直接读取 eligible Round records，不以 Stats cache 作为模型输入权威。

### 2.19 Snapshot 不是 Cache

`round_analysis_snapshots` 保存当时 prediction 的分析事实。

它不能因为：

```text
模型升级
历史变化
Stats repair
```

而被自动重新计算覆盖。

### 2.20 用户错误不能泄露内部诊断

正常用户错误 presentation 不应直接显示：

```text
Traceback
Raw SQL
内部绝对路径
Python exception class
```

未预期异常应生成 Error ID，并将完整诊断写入日志。

### 2.21 Safety state 优先于继续运行

对于无法证明数据库仍然可信的状态：

```text
Source invariant failure
Multiple pending
Corrupt database
Invalid Restore result
```

系统必须 fail closed，而不是为了“继续能用”猜测修复业务事实。

---

## 3. Subjective Model

实现主要位于：

```text
src\probability_calibration_tool\core\subjective.py
src\probability_calibration_tool\core\model_specs.py
```

当前：

```text
SUBJECTIVE_MODEL_VERSION = 1
```

### 3.1 输入合同

Subjective raw probability 必须是：

```text
int
0 <= p_h_raw <= 100
```

Python `bool` 虽然是 `int` 的子类，但必须拒绝。

因此：

```text
True
False
```

不能作为：

```text
1
0
```

概率输入。

### 3.2 Mathematical Clamp

计算时：

```text
p_h_used = min(max(p_h_raw, 1), 99)
```

因此：

```text
p_h_raw = 0
→ p_h_used = 1

p_h_raw = 100
→ p_h_used = 99
```

随后：

```text
p = p_h_used / 100
```

数据库仍保留原始 `p_h_raw`。

### 3.3 冻结常量

当前：

```text
SUBJECTIVE_MIN_PROBABILITY      = 0.01
SUBJECTIVE_LOW_BREAKPOINT       = 0.45
SUBJECTIVE_MID_HIGH_BREAKPOINT  = 0.55
SUBJECTIVE_HIGH_BREAKPOINT      = 0.85
SUBJECTIVE_VERY_HIGH_BREAKPOINT = 0.95
SUBJECTIVE_MAX_PROBABILITY      = 0.99
```

对应 factor：

```text
1.5
2.0
1.4
1.2
```

### 3.4 Logit Interval

定义：

```text
z = ln(p / (1 - p))
```

根据 `p` 得到 logit half-width：

```text
d(p)
```

最终：

```text
p_min = sigmoid(z - d)
p_max = sigmoid(z + d)
```

其中：

```text
sigmoid(x) = 1 / (1 + exp(-x))
```

### 3.5 `d(p)` 分段

当前定义：

```text
0.01 <= p <= 0.45
    d = ln(1.5)

0.45 < p < 0.55
    在 ln(1.5) 与 ln(2.0) 之间线性插值

0.55 <= p <= 0.85
    d = ln(2.0)

0.85 < p < 0.95
    从 ln(2.0) 线性下降到 ln(1.4)

0.95 <= p <= 0.99
    从 ln(1.4) 线性下降到 ln(1.2)
```

### 3.6 代表性 Golden Values

当前重要参考值包括：

| Raw | Used | Probability | Lower | Upper |
| ---: | ---: | ---: | ---: | ---: |
| 0 | 1 | 0.01 | 0.006688963211 | 0.014925373134 |
| 40 | 40 | 0.40 | 0.307692307692 | 0.500000000000 |
| 45 | 45 | 0.45 | 0.352941176471 | 0.551020408163 |
| 50 | 50 | 0.50 | 0.366025403784 | 0.633974596216 |
| 55 | 55 | 0.55 | 0.379310344828 | 0.709677419355 |
| 75 | 75 | 0.75 | 0.600000000000 | 0.857142857143 |
| 85 | 85 | 0.85 | 0.739130434783 | 0.918918918919 |
| 90 | 90 | 0.90 | 0.843224034813 | 0.937733035972 |
| 95 | 95 | 0.95 | 0.931372549020 | 0.963768115942 |
| 99 | 99 | 0.99 | 0.988023952096 | 0.991652754591 |
| 100 | 99 | 0.99 | 0.988023952096 | 0.991652754591 |

这些数值属于当前 Model Version 1 的 Golden behavior。

如果未来修改 clamp、breakpoint、factor 或 interval 算法，应重新评估：

```text
SUBJECTIVE_MODEL_VERSION
Golden Tests
Snapshot compatibility
Technical Reference
```

---

## 4. Historical Model

主要实现：

```text
src\probability_calibration_tool\core\historical.py
src\probability_calibration_tool\core\model_specs.py
```

当前：

```text
HISTORY_MODEL_VERSION = 1
HISTORY_GATE_VERSION = 1
```

### 4.1 输入合同

输入：

```text
wins
losses
```

必须是：

```text
非负整数
```

同样拒绝 Python `bool`。

定义：

```text
n = wins + losses
```

### 4.2 无历史

当：

```text
n = 0
```

结果：

```text
status = NO_HISTORY
ready = false
```

下列 numerical fields：

```text
posterior probability
credible interval
interval width
```

均为空。

### 4.3 Jeffreys Posterior

当 `n > 0`：

```text
alpha = wins + 0.5
beta  = losses + 0.5
```

posterior mean：

```text
(wins + 0.5) / (n + 1)
```

当前 credible level：

```text
0.95
```

区间使用 Beta distribution：

```text
2.5% quantile
97.5% quantile
```

### 4.4 Readiness Gate

当前：

```text
HISTORY_MIN_SAMPLE_SIZE = 20
HISTORY_MAX_INTERVAL_WIDTH = 0.25
```

只有：

```text
n >= 20
AND
interval_width <= 0.25
```

才：

```text
ready = true
status = VALID
```

否则：

```text
status = INSUFFICIENT
```

### 4.5 代表性参考值

```text
wins = 18
losses = 2
n = 20
```

当前 interval width 仍约为：

```text
0.2624807693
```

因此：

```text
INSUFFICIENT
```

而：

```text
wins = 19
losses = 1
```

posterior：

```text
0.9285714286
```

95% credible interval：

```text
0.7891813638
...
0.9945509674
```

width：

```text
0.2053696037
```

所以：

```text
VALID
```

其它重要参考：

```text
20 / 0
posterior = 0.9761904762
VALID

50 / 50
posterior = 0.5
interval ≈ 0.4031739509 ... 0.5968260491
VALID
```

### 4.6 `n < 20` 永远不 Ready

即使 19 局全部获胜：

```text
19 / 0
```

credible interval 已经很窄，也不能越过：

```text
minimum sample size
```

Gate。

因此 readiness 是：

```text
sample-size condition
AND
uncertainty-width condition
```

不是二者任选其一。

### 4.7 Model 与 Gate 分开版本化

如果未来只改变：

```text
n >= 20
→ n >= 30
```

但 Jeffreys posterior 本身不变，则：

```text
HISTORY_GATE_VERSION
```

需要重新评估。

如果改变：

```text
Jeffreys prior
Beta estimator
credible interval algorithm
```

则属于：

```text
HISTORY_MODEL_VERSION
```

变化。

---

## 5. Odds、EV、S、Break-Even 与 Odds Combination

当前赔率解释为：

```text
gross-return decimal odds
```

例如：

```text
2.50
```

表示总返还倍数 2.5，而不是净盈利 2.5。

当前：

```text
ODDS_ANALYSIS_VERSION = 1
FLOAT_EPSILON = 1e-12
```

### 5.1 Odds Syntax

正式语法：

```text
[0-9]+(?:\.[0-9]+)?
```

必须完整匹配。

因此允许：

```text
1
2
2.5
0002.50
```

拒绝：

```text
+2
-2
1e3
2,5
２.５
 2.5
2.5 
```

赔率必须：

```text
>= 1
```

### 5.2 Break-Even Threshold

Win-side odds：

```text
O_w
```

其 Win probability break-even：

```text
1 / O_w
```

Lose-side odds：

```text
O_l
```

其 Loss-event break-even：

```text
1 / O_l
```

若转成 Win probability：

```text
1 - 1 / O_l
```

### 5.3 Subjective Win-Side EV

设主观 probability interval：

```text
[p_min, p_max]
```

Win-side EV：

```text
EV_win(p) = p * O_w - 1
```

因此：

```text
EV_win_min = p_min * O_w - 1
EV_win_max = p_max * O_w - 1
```

### 5.4 Subjective Lose-Side EV

Loss probability：

```text
1 - p
```

因此：

```text
EV_lose(p) = (1 - p) * O_l - 1
```

对应 interval：

```text
EV_lose_min = (1 - p_max) * O_l - 1
EV_lose_max = (1 - p_min) * O_l - 1
```

### 5.5 Robust EV State

当前状态依据整个 probability interval 与：

```text
FLOAT_EPSILON
```

分类。

概念上包括：

```text
整个 interval 都为正
整个 interval 都为负
跨越 break-even
临界状态
```

不能仅根据 midpoint EV 判断整个 uncertainty interval 的状态。

### 5.6 S 指标

`S` 是基于：

```text
logit threshold
```

与 Subjective interval half-width `d` 构造的 margin index。

它不是：

```text
Probability
Posterior
EV
```

也不能被用户解释成“获胜概率”。

赔率：

```text
O = 1
```

时对应 S：

```text
None
```

### 5.7 Historical Odds Analysis

只有：

```text
HistoryModelStatus.VALID
```

时，Historical odds analysis 才正式计算。

它以 Historical Beta posterior 为基础，计算：

```text
Historical EV
posterior probability of exceeding break-even threshold
```

如果 Historical Model：

```text
NO_HISTORY
INSUFFICIENT
```

这些字段保持不可用。

### 5.8 Odds Combination

定义：

```text
T = 1 / O_w + 1 / O_l
```

分类：

```text
|T - 1| <= epsilon
    CRITICAL

T > 1 + epsilon
    NORMAL_OVERLAP

T < 1 - epsilon
    DOUBLE_POSITIVE_WINDOW
```

`DOUBLE_POSITIVE_WINDOW` 只描述赔率组合结构。

它不是第三个概率模型，也不意味着实际两边必然同时具有正 EV。

### 5.9 Model Relation

系统还根据 Subjective 与 Historical analysis 形成模型关系分类。

如果 Historical Model 不可用：

```text
history_unavailable
```

而不是强行将缺失历史解释成：

```text
agreement
disagreement
```

### 5.10 Snapshot 必须保存分析版本

Round Snapshot 持久化：

```text
subjective_model_version
history_model_version
history_gate_version
odds_analysis_version
```

以及该次分析的 EV、S、Break-Even、Historical status 和 model relation。

以后即使模型升级，旧 Snapshot 仍然能够说明：

> 当时使用哪个版本的数学合同得到了什么结果。
---

## 6. Anti-Anchoring：历史信息隔离

Anti-Anchoring 的目标是：

> 在用户正式提交局前 prediction 之前，不让 Historical information 影响 Subjective prediction。

这里不仅要求 Subjective Model 与 Historical Model 在数学上独立，还要求用户在信息层面尽量保持独立。

### 6.1 Calculate 前禁止方向性历史信息

在一次成功 Calculate 之前，正常 UI 不得显示：

```text
wins
losses
win rate
Historical probability
credible interval
Historical EV
Historical direction
```

也不能通过：

```text
Maintenance
tooltip
status bar
summary card
其它普通页面
```

间接泄露这些信息。

### 6.2 Maintenance 的允许信息

Calculate 前，Maintenance 只允许提供非方向性的历史维护信息。

当前 Maintenance DTO 包含：

```text
character_id
display_name
active_regime_number
regime_started_at
regime_reason
included_sample_count
```

对应 UI 可以显示：

```text
Character
Current regime
Started locally
Reason
Included samples
```

其中：

```text
included_sample_count
```

只说明当前 Historical Regime 中有多少条 eligible historical observations。

它不能进一步拆成：

```text
wins
losses
win percentage
```

### 6.3 Historical Display State

Historical Analysis 的展示状态可概括为：

```text
HIDDEN
NO_HISTORY
INSUFFICIENT
VISIBLE
```

`VISIBLE` 需要同时满足：

```text
reference_history = true
HistoryModelStatus = VALID
存在 durable history exposure authority
```

如果用户选择：

```text
Do not use history
```

则 Historical display 保持：

```text
HIDDEN
```

即使数据库中实际存在大量历史样本。

### 6.4 Calculate 与 Exposure Authority

成功 Calculate 时，Application 在同一个事务中：

```text
读取 eligible history
        ↓
构造 Snapshot
        ↓
创建 pending Round
        ↓
保存 Snapshot
        ↓
commit
```

如果：

```text
reference_history = true
AND
Historical status = VALID
```

则 Round 同时持久化：

```text
history_exposed = true
history_exposed_at = now
```

否则：

```text
history_exposed = false
history_exposed_at = NULL
```

只有 commit 成功后，UI 才能展示正式 Historical numeric analysis。

### 6.5 为什么 Exposure Authority 要持久化

仅仅看到 Snapshot 中：

```text
HistoryModelStatus = VALID
```

还不足以证明：

> 用户当时已经被允许看到这些历史数值。

因此系统额外保存：

```text
history_exposed
history_exposed_at
```

作为 durable information-exposure audit。

Recovery 后也必须继续尊重这组审计字段。

### 6.6 Builder Fail Closed

如果：

```text
reference_history = true
Snapshot = VALID
```

但：

```text
history_exposed = false
```

Application 不会因为 Snapshot 中已经有数值就直接显示。

这属于数据不变量矛盾，应：

```text
fail closed
```

而不是释放 Historical numeric information。

### 6.7 Recalculate 后 Exposure 是 Sticky 的

如果某次 committed prediction 已经：

```text
history_exposed = true
```

后续 Recalculate 不会把这段事实抹掉。

即使新 revision 的 Historical 状态或输入发生变化：

```text
history_exposed
```

仍表示：

> 这个 Round 的用户曾经已经看到过正式 Historical numeric analysis。

对应：

```text
history_exposed_at
```

保持第一次 exposure 的时间。

### 6.8 Subjective Independence Compromise

如果用户已经看过 Historical numeric analysis，之后仍然允许修改 prediction，则系统需要区分：

```text
修改是否可能破坏 Subjective information independence
```

当前审计字段：

```text
subjective_independence_compromised
```

用于记录这一事实。

### 6.9 哪些修改会 Compromise

在已经 exposure History 后，如果用户 Modify 并改变：

```text
character_id
p_h_raw
```

则新的 committed revision 标记：

```text
subjective_independence_compromised = true
```

因为用户可能已经利用看到的历史信息重新调整 Subjective prediction 或更换分析对象。

### 6.10 Odds-Only 修改不自动 Compromise

如果 exposure 后只修改：

```text
win_odds
lose_odds
```

而 Character 与 Subjective raw probability 不变，当前实现不会仅因为赔率变化把：

```text
subjective_independence_compromised
```

改成 true。

### 6.11 Result Selection 会关闭修改

用户一旦选择：

```text
Win
Loss
```

就表明实际结果已经知道。

此后 prediction revision 必须关闭。

因此不能：

```text
知道结果
→ Modify
→ Recalculate
```

### 6.12 Recovery 使用更保守规则

程序崩溃后，数据库只能证明：

```text
pending Round
Snapshot
```

仍存在。

它无法证明崩溃前用户是否已经看到实际结果，因为：

```text
result choice
```

在 Confirm Save 前只存在内存。

所以 Recovery 成功后：

```text
prediction revision locked = true
```

即使数据库中的：

```text
result = NULL
```

也不能恢复 Modify 权限。

### 6.13 数学独立与信息独立

必须区分：

```text
Mathematical independence
```

与：

```text
Information independence
```

前者表示：

```text
Subjective Model
Historical Model
```

公式上互不混合。

后者表示：

> 用户形成 Subjective prediction 时，是否已经接触 Historical information。

Anti-Anchoring 主要保护第二种独立性。

---

## 7. Workflow State Machine

Workflow 管理当前单局的交互状态。

当前状态：

```text
DRAFT
CALCULATING
PENDING_LOCKED
PENDING_EDIT
CONFIRM_SAVE
COMPLETING
RECOVERY
RECOVERY_ERROR
COMPLETED_NOTICE
```

这些是：

```text
in-memory WorkflowState
```

不能与数据库中的：

```text
RoundStatus
```

混为一谈。

数据库 RoundStatus 只有：

```text
pending
completed
voided
```

### 7.1 DRAFT

新 Workflow 初始状态：

```text
DRAFT
```

此时：

```text
无 committed analysis
无 post-run result
无 include choice
prediction revision unlocked
```

用户可以输入局前预测数据。

### 7.2 `set_inputs()`

局前 inputs 只允许在：

```text
DRAFT
PENDING_EDIT
```

中设置。

在 `PENDING_EDIT` 中，这些只是：

```text
candidate inputs
```

还没有成为 committed prediction revision。

### 7.3 Calculate

在：

```text
DRAFT
```

调用 Calculate：

```text
DRAFT
  ↓
CALCULATING
  ↓
RoundService.calculate()
```

成功后：

```text
PENDING_LOCKED
```

失败则回到原来的：

```text
DRAFT
```

并且不能留下部分 committed prediction。

### 7.4 PENDING_LOCKED

表示：

> 当前 Round 已存在 committed prediction + Snapshot。

它不自动意味着：

```text
prediction 永远不能修改
```

如果 revision 尚未关闭，仍可进入：

```text
Modify
```

### 7.5 Modify

只有：

```text
PENDING_LOCKED
AND
prediction revision unlocked
```

时可以 Modify。

Modify 会：

```text
清除内存中的 result
清除内存中的 include
进入 PENDING_EDIT
```

但数据库中的旧 committed Round / Snapshot：

```text
仍然保持权威
```

直到 Recalculate 成功。

### 7.6 PENDING_EDIT

这一状态中的修改：

```text
只存在内存
```

数据库仍保存上一版成功 committed prediction。

如果程序在此时退出或崩溃：

```text
candidate edits 可以丢失
旧 committed prediction 必须保持
```

### 7.7 Recalculate

在 `PENDING_EDIT` 中：

```text
PENDING_EDIT
  ↓
CALCULATING
  ↓
RoundService.recalculate()
```

成功后：

```text
same round_id
revision_count += 1
Snapshot 更新
PENDING_LOCKED
```

失败则回到：

```text
PENDING_EDIT
```

并保留旧 committed revision。

### 7.8 Result Choice

只有：

```text
PENDING_LOCKED
```

允许选择：

```text
Win
Loss
```

选择结果后：

```text
prediction revision locked = true
```

这一锁不可通过 Back 清除。

### 7.9 Include Choice

同样只有：

```text
PENDING_LOCKED
```

允许选择：

```text
Include
Exclude
```

单独选择 Include / Exclude：

```text
不会关闭 prediction revision
```

真正关闭 revision 的是：

```text
result selection
```

或：

```text
Recovery
```

### 7.10 CONFIRM_SAVE

当：

```text
result 已选择
AND
include 已选择
```

进入：

```text
CONFIRM_SAVE
```

此时这两个局后选择仍然只是：

```text
memory state
```

数据库 Round 仍为：

```text
pending
result = NULL
include = NULL
```

### 7.11 Back

从：

```text
CONFIRM_SAVE
```

执行 Back：

```text
→ PENDING_LOCKED
```

并保留：

```text
result
include
prediction revision lock
```

所以 Back 只是退出最终确认页，不撤销已经知道结果这一事实。

### 7.12 Confirm Save

```text
CONFIRM_SAVE
  ↓
COMPLETING
  ↓
RoundService.complete_pending()
```

成功：

```text
COMPLETED_NOTICE
```

失败：

```text
CONFIRM_SAVE
```

数据库必须保持失败前的权威状态。

### 7.13 COMPLETED_NOTICE

表示当前 Round 已经：

```text
completed
```

UI 可以显示保存完成提示。

Dismiss 后 Workflow 清理当前 Round memory：

```text
→ DRAFT
```

并重新开放下一局 prediction revision。

### 7.14 Void Pending

在允许的 pending 状态下，当前 Round 可以被正式 Void。

持久化：

```text
pending
→ voided
```

并保留：

```text
Round
Snapshot
audit
```

随后 Workflow 清理：

```text
→ DRAFT
```

### 7.15 Recovery Inspect

Recovery inspection 只允许从：

```text
DRAFT
```

进行。

结果：

```text
0 pending
→ DRAFT

1 pending
→ RECOVERY

2+ pending
→ RECOVERY_ERROR
```

### 7.16 RECOVERY

表示：

> 找到了一个可继续的 durable pending Round，但尚未正式加载其 committed analysis。

用户点击 Continue 后：

```text
RecoveryService.continue_pending()
```

读取同一个：

```text
Round
Snapshot
```

成功后：

```text
PENDING_LOCKED
prediction revision locked = true
result = None
include = None
```

### 7.17 RECOVERY_ERROR

多个 pending Round 不允许：

```text
自动挑第一条
自动挑最新一条
让用户随便选
```

这属于数据安全异常。

Workflow 进入：

```text
RECOVERY_ERROR
```

并且不构造 analysis。

### 7.18 Illegal Transition

任何不允许的状态转换应：

```text
抛 InvalidWorkflowTransitionError
```

并保证：

```text
Workflow state 不被部分改变
数据库不被意外修改
```

### 7.19 Persistent Lifecycle

数据库层 Round 生命周期只有：

```text
不存在
  ↓ Calculate
pending
  ↓ Complete
completed
```

或：

```text
pending
  ↓ Void
voided
```

Recalculate：

```text
pending → pending
```

Historical Correction 则属于 completed history 的独立审计操作，不是普通 Workflow transition。

---

## 8. Transaction 与 Persistence Semantics

事务边界由 Application use case 和 UnitOfWork 管理。

Repository 不独立 commit。

### 8.1 UnitOfWork

进入：

```text
UnitOfWork.__enter__()
```

后：

```text
创建 SQLite connection
BEGIN
repositories 共用同一个 connection
```

`commit()`：

```text
connection.commit()
```

成功后立即：

```text
BEGIN
```

开启新的事务。

退出 UnitOfWork 时：

```text
rollback 当前仍未提交的事务
close connection
```

注意：

> `__exit__()` 的 rollback 只撤销当前未提交事务，不会撤销此前已经成功 commit 的事务。

### 8.2 Repository 不拥有 Commit

Repository 可以：

```text
SELECT
INSERT
UPDATE
DELETE
```

但不能决定：

```text
什么时候整个业务操作算成功
```

业务事务边界由 Application Service 控制。

### 8.3 SQLite Connection Configuration

当前普通连接使用：

```text
isolation_level = None
row_factory = sqlite3.Row

PRAGMA foreign_keys = ON
PRAGMA journal_mode = DELETE
PRAGMA synchronous = EXTRA
```

普通业务 UnitOfWork 使用：

```text
BEGIN
```

Fresh Schema initialization 使用：

```text
BEGIN IMMEDIATE
```

### 8.4 Calculate Transaction

Calculate 在事务外先验证 prediction input。

进入 UnitOfWork 后：

```text
检查全局 pending guard
        ↓
读取 active Regime
        ↓
取得 UTC now
        ↓
读取 eligible historical rounds
        ↓
构造完整 Snapshot
        ↓
生成新 round_id
        ↓
绑定 Snapshot round_id
        ↓
决定 exposure audit
        ↓
INSERT Round
        ↓
INSERT Snapshot
        ↓
commit
```

只有 commit 后才：

```text
构造 LockedAnalysisView
```

### 8.5 为什么 Round 先于 Snapshot Insert

Snapshot：

```text
round_id
```

通过 Foreign Key 指向：

```text
rounds
```

并且：

```text
foreign_keys = ON
```

所以新 Round 必须在同一事务中先 Insert，再 Insert Snapshot。

这不影响原子性，因为两者直到 commit 前都不会成为正式持久化结果。

### 8.6 Calculate Failure

如果发生：

```text
Snapshot insert failure
commit failure
其它 transaction failure
```

必须得到：

```text
Round 不存在
Snapshot 不存在
正式 analysis 不展示
```

即：

```text
database before-state preserved
```

### 8.7 Historical Query 与 Write 同事务

Calculate 使用的 Historical sample 与创建 pending Round / Snapshot 发生在同一个明确事务中。

因此：

```text
History input
Snapshot
Round
```

属于同一 calculation boundary。

### 8.8 Historical Model 直接读取 `rounds`

Historical input 来自：

```text
RoundRepository.eligible_history(...)
```

查询：

```text
same character
same regime
status = completed
include_character_history = true
```

而不是：

```text
character_stats
```

cache。

### 8.9 Snapshot Cutoff

构造 Snapshot 时：

```text
history_data_through_at = now
```

如果存在 eligible historical rows：

```text
last_included_historical_round_id
```

取按稳定 chronology 排序后的最后一条。

### 8.10 Recalculate Transaction

Recalculate：

```text
验证 candidate inputs
        ↓
BEGIN
        ↓
确认唯一 pending Round
        ↓
读取旧 Round
        ↓
读取旧 Snapshot
        ↓
确认目标 Character / Regime
        ↓
取得新 now
        ↓
重新读取 eligible history
        ↓
重新构造 Snapshot
        ↓
决定 sticky exposure / compromise audit
        ↓
UPDATE same Round
        ↓
UPDATE same Snapshot
        ↓
commit
```

成功后：

```text
same round_id
same created_at
revision_count += 1
```

### 8.11 Recalculate Failure

Recalculate 的关键 rollback 合同：

> 如果新的 revision 没有成功 commit，旧 committed prediction revision 必须完整保留。

包括：

```text
旧 Round
旧 Snapshot
旧 revision_count
旧 exposure audit
旧 compromise audit
```

都不能被部分覆盖。

### 8.12 Complete Transaction

Complete：

```text
验证 result/include bool
        ↓
BEGIN
        ↓
确认 pending Round
        ↓
确认 Snapshot
        ↓
UPDATE Round:
    status = completed
    result
    include
    completed_at
    last_updated_at
        ↓
如果 include = true:
    rebuild Stats
        ↓
commit
```

Round completion 与相应 Stats rebuild：

```text
同一事务
```

### 8.13 为什么先 Completed 再 Rebuild Stats

Stats rebuild 的 source query 只计算：

```text
completed
AND
include = true
```

因此需要先在当前事务中把 Round 改为 completed。

SQLite 同一事务中的后续查询可以看到自己的未提交写入，所以 Stats rebuild 会包含刚刚完成的 Round。

### 8.14 Exclude Completion

如果：

```text
include = false
```

Round 仍然：

```text
completed
```

但不会进入 eligible history。

因为 eligible set 没有变化，当前完成操作不会执行 Stats rebuild。

### 8.15 Void Transaction

Void Pending：

```text
确认 pending Round
确认 Snapshot
        ↓
UPDATE status = voided
voided_at
void_reason
last_updated_at
        ↓
commit
```

Snapshot 保留。

Stats 不需要因为 pending Void 改变。

### 8.16 Transaction Failure 边界

当前 rollback guarantee 的准确含义是：

> 对尚未成功 commit 的当前事务，失败必须 rollback。

不能夸大成：

> 即使 SQLite COMMIT 已经真正成功，但 Python 在 commit 后发生任意系统级异常，也能够神奇地撤销已经落盘的数据。

对于已经跨过真正 durable commit 或 filesystem replacement 的情况，系统使用的是：

```text
post-commit / post-replacement safety handling
```

而不是普通 transaction rollback。

### 8.17 Transaction 核心不变量

必须保持：

```text
Repository 不 commit
Application/UoW 拥有事务边界

History read 与 prediction write 同事务

新 Round + Snapshot 同事务

正式 analysis 只在 commit 后展示

Recalculate 不创建新 Round

Recalculate failure 保留旧 revision

Completion + Included Stats rebuild 同事务

Exclude 不删除 Round

Void 保留 Snapshot 与 audit
```

---

## 9. SQLite Database Schema 与 Records

当前：

```text
PRAGMA user_version = 1
```

固定六张表：

```text
characters
history_regimes
rounds
round_analysis_snapshots
character_stats
meta
```

### 9.1 时间存储

所有业务 datetime：

```text
必须是 timezone-aware
```

持久化时统一标准化为 UTC，并序列化成：

```text
YYYY-MM-DDTHH:MM:SS.ffffffZ
```

Naive datetime 必须拒绝。

### 9.2 `characters`

用于保存冻结 Character identity。

主要字段：

```text
character_id
internal_code
display_name
tainted
pair_row
active
```

约束包括：

```text
character_id primary key
internal_code unique
tainted ∈ {0,1}
pair_row ∈ 1..17
active ∈ {0,1}
unique(pair_row, tainted)
```

当前 seed：

```text
34 Characters
```

Character ID 是稳定业务 identity，不因翻译变化。

### 9.3 Character ID

当前 1–34：

```text
1  Isaac
2  Magdalene
3  Cain
4  Judas
5  ???
6  Eve
7  Samson
8  Azazel
9  Lazarus
10 Eden
11 The Lost
12 Lilith
13 Keeper
14 Apollyon
15 The Forgotten
16 Bethany
17 Jacob & Esau

18 Tainted Isaac
19 Tainted Magdalene
20 Tainted Cain
21 Tainted Judas
22 Tainted ???
23 Tainted Eve
24 Tainted Samson
25 Tainted Azazel
26 Tainted Lazarus
27 Tainted Eden
28 Tainted Lost
29 Tainted Lilith
30 Tainted Keeper
31 Tainted Apollyon
32 Tainted Forgotten
33 Tainted Bethany
34 Tainted Jacob
```

不存在：

```text
Tainted Esau
```

这一单独 Character。

### 9.4 `history_regimes`

主要字段：

```text
regime_id
character_id
regime_number
started_at
ended_at
active
reason
```

主要约束：

```text
regime_number >= 1
active ∈ {0,1}
unique(character_id, regime_number)
```

并通过 partial unique index：

```text
ux_history_regimes_active
```

保证数据库层每个 Character 最多一个 active Regime。

Active Regime 必须：

```text
ended_at = NULL
```

Inactive Regime 必须具有：

```text
ended_at
```

### 9.5 `rounds`

`rounds` 是核心业务与审计事实表。

主要字段包括：

```text
round_id

created_at
calculated_at
last_updated_at
completed_at
voided_at
void_reason

character_id
history_regime_id

reference_history

p_h_raw

win_odds_raw
lose_odds_raw

win_odds
lose_odds

status
revision_count

result
include_character_history

history_exposed
history_exposed_at

subjective_independence_compromised

supersedes_round_id
```

### 9.6 Raw Odds 与 Parsed Odds 同时保存

例如用户输入：

```text
0002.50
```

数据库保留：

```text
win_odds_raw = "0002.50"
```

同时保存用于数学分析的 numeric value：

```text
win_odds = 2.5
```

因此：

```text
原始输入语法
```

与：

```text
数学值
```

均可审计。

### 9.7 Round Status Shape

合法：

```text
pending
completed
voided
```

Pending：

```text
result = NULL
include = NULL
completed_at = NULL
voided_at = NULL
```

Completed：

```text
result != NULL
include != NULL
completed_at != NULL
voided_at = NULL
```

Voided 支持两种合法形态：

```text
voided pending
```

即：

```text
post-run facts 全空
```

以及 Correction 后的：

```text
voided completed original
```

即：

```text
原 result/include/completed_at 继续保留
```

不能出现半空半有的混合形态。

### 9.8 Global Pending Constraint

partial unique index：

```text
ux_rounds_pending
```

保证正常数据库中全局最多一个：

```text
status = pending
```

Round。

### 9.9 `revision_count`

首次 Calculate：

```text
revision_count = 0
```

每次成功 Recalculate：

```text
revision_count += 1
```

它不是：

```text
Snapshot revision history table
```

当前数据库只保存：

```text
当前 committed prediction revision
```

而不是每次 Recalculate 的所有历史版本。

### 9.10 Exposure Shape

数据库要求：

```text
history_exposed = true
↔
history_exposed_at != NULL
```

`subjective_independence_compromised` 作为 durable audit 字段由 Application 业务规则维护。

### 9.11 Correction Link

```text
supersedes_round_id
```

是 self-FK，表示：

```text
当前 Round
```

替代：

```text
某个旧 completed Round
```

不能：

```text
自己 supersede 自己
```

并通过：

```text
ux_rounds_supersedes
```

保证同一 source Round 最多被一个 replacement supersede。

因此：

```text
chain 可以继续
branch 不允许
```

### 9.12 `round_analysis_snapshots`

每个 Round：

```text
恰好一个 Snapshot
```

Snapshot primary key 同时是：

```text
round_id
```

并 Foreign Key 到：

```text
rounds
```

### 9.13 Snapshot 的 Subjective Fields

主要包括：

```text
p_h_used
subjective_probability
subjective_interval_lower
subjective_interval_upper
subjective_logit_half_width
subjective_model_version
```

其中：

```text
1 <= p_h_used <= 99
```

并要求：

```text
0 < lower < probability < upper < 1
d > 0
```

### 9.14 Snapshot 的 Historical Fields

包括：

```text
historical_sample_size
historical_wins
historical_losses

historical_probability
historical_interval_lower
historical_interval_upper
historical_interval_width

historical_model_status
historical_ready

history_model_version
history_gate_version

history_data_through_at
last_included_historical_round_id
```

### 9.15 Historical Status Shape

`NO_HISTORY`：

```text
sample_size = 0
ready = false

posterior / interval = NULL
last historical ID = NULL

Historical EV / posterior thresholds = NULL
model relation = history_unavailable
```

`INSUFFICIENT`：

```text
sample_size >= 1
ready = false

posterior / interval 存在
Historical EV / posterior thresholds = NULL
model relation = history_unavailable
```

`VALID`：

```text
sample_size >= 1
ready = true

posterior / interval 存在
Historical EV / posterior thresholds 存在
model relation 不得是 history_unavailable
```

数据库当前并没有额外强制：

```text
INSUFFICIENT / VALID
→ last_included_historical_round_id 必须非 NULL
```

这一关联通常由 Application 正常写入，并由 Application invariant 进一步检查。

### 9.16 Snapshot 是当前 Prediction Revision

普通 Recalculate：

```text
UPDATE same snapshot row
```

不会新增：

```text
snapshot_revision_2
```

等历史记录。

Historical Correction 则复制原 Snapshot 到 replacement Round，保留原 prediction analysis。

### 9.17 `character_stats`

主要字段：

```text
character_id
history_regime_id

included_games
wins
losses

last_included_round_id
updated_at
stats_version
```

约束：

```text
included_games >= 0
wins >= 0
losses >= 0

included_games = wins + losses
```

并要求：

```text
included_games = 0
↔
last_included_round_id = NULL
```

### 9.18 Stats 是 Cache

Stats 可以根据：

```text
rounds
```

中：

```text
same Character
same Regime
completed
include = true
```

的记录重新构建。

Historical Model Calculate 本身不依赖这个 Cache。

### 9.19 `meta`

`meta` 用于基础设施 metadata。

初始化时写入：

```text
schema_initialized = "1"
```

不能把 `meta` 当作随意添加业务字段、绕过正式 Schema versioning 的后门。

### 9.20 主要 Index

当前显式 index 包括：

```text
ux_history_regimes_active
ux_rounds_pending
ux_rounds_supersedes
ix_rounds_calculated_at
ix_rounds_eligible_history
```

### 9.21 Foreign-Key Retention

业务关系总体使用：

```text
ON DELETE RESTRICT
```

而不是 cascade 删除整段历史。

设计倾向是：

```text
保留审计事实
通过状态表达变化
```

### 9.22 Fresh Schema Initialization

从真正不存在的 v0 database 初始化 v1：

```text
BEGIN IMMEDIATE
        ↓
创建 tables / indexes
        ↓
seed 34 Characters
        ↓
每个 Character 创建 Regime 1
        ↓
每个 Regime 创建 zero Stats
        ↓
写 meta
        ↓
PRAGMA user_version = 1
        ↓
commit
```

任何失败：

```text
整个初始化 rollback
```

不能留下 partial schema / seed。

### 9.23 Fresh DB 初始状态

正常初始化完成：

```text
34 Characters
34 active Regimes
34 zero Stats

0 Rounds
0 Snapshots
```

### 9.24 Reopen v1

重新打开已有：

```text
user_version = 1
```

数据库：

```text
不重新 seed
不覆盖现有数据
```

### 9.25 Newer Schema

如果：

```text
user_version > supported version
```

必须拒绝：

```text
UnsupportedNewerSchema
```

不能：

```text
自动降级
删除未知字段
改回 user_version = 1
```

### 9.26 Migration Infrastructure

项目已经具有 Migration infrastructure。

但当前正式 Schema：

```text
v1
```

并没有生产中的 v2 migration。

所以当前不能声称：

```text
任意旧数据库都会自动升级到最新版本
```

只有正式注册的 migration path 才能执行。

---

## 10. Historical Regime 与 Character Stats

Historical Regime 用于：

> 把同一个 Character 的历史数据分成彼此独立的阶段。

它不是：

```text
清空历史
删除历史
模型版本
```

### 10.1 Eligible Historical Round

一条 Round 要成为当前 Historical sample，必须同时满足：

```text
same character_id
same history_regime_id
status = completed
include_character_history = true
```

不同 Regime 的历史绝不能混合。

### 10.2 Start New Regime

`start_new_regime(character_id, reason)` 的核心流程：

```text
验证 reason
        ↓
BEGIN
        ↓
检查全局是否有 pending Round
        ↓
读取目标 Character 当前 active Regime
        ↓
取得 now
        ↓
结束旧 Regime
        ↓
创建新 Regime
        ↓
创建 zero Stats
        ↓
commit
```

### 10.3 Pending 全局阻止 Regime Switch

只要数据库中存在：

```text
任何 pending Round
```

就不能切换：

```text
任何 Character
```

的 Regime。

不是只阻止 pending Round 所属 Character。

这是一个：

```text
global pending guard
```

### 10.4 Old Regime

旧 Regime：

```text
active = false
ended_at = now
```

其：

```text
reason
Stats
Rounds
Snapshots
```

继续保留。

### 10.5 New Regime

新 Regime：

```text
regime_number = old + 1
started_at = now
ended_at = NULL
active = true
```

并生成新的：

```text
regime_id
```

### 10.6 New Regime Stats

新 Regime 同一事务创建：

```text
included_games = 0
wins = 0
losses = 0
last_included_round_id = NULL
stats_version = current
```

因此切换后第一局若参考历史：

```text
Historical sample size = 0
```

不会继承旧 Regime 的数据。

### 10.7 Regime Switch Atomicity

如果以下任一步失败：

```text
结束旧 Regime
创建新 Regime
创建 zero Stats
commit
```

整个切换必须 rollback。

不能出现：

```text
旧 Regime 已关闭
但新 Regime 不存在
```

或：

```text
新 Regime 已存在
但 Stats 不存在
```

的半完成状态。

### 10.8 Regime Reason

Reason：

```text
可选
```

但如果提供：

```text
必须是 text
```

当前技术合同不在这里声明额外长度限制，除非未来源码正式加入并同步文档。

### 10.9 Stats Rebuild Source

Stats rebuild 只查询：

```text
rounds
```

并采用与 Historical eligibility 相同的核心条件：

```text
same Character
same Regime
completed
included
```

然后计算：

```text
included_games
wins
losses
last_included_round_id
```

### 10.10 Last Included Round

Stats 中的：

```text
last_included_round_id
```

取当前 eligible records chronology 的最后一条。

Historical chronology 使用：

```text
calculated_at ASC
round_id ASC
```

因此 Stats 找“最后一条”时使用反向排序：

```text
calculated_at DESC
round_id DESC
```

### 10.11 Stats Rebuild 是确定性的

即使：

```text
Stats 缺失
Stats counts 错误
Stats version 过期
```

只要 source Round facts 完整，Stats 就可以重新构建。

这也是 Startup 允许自动 repair Stats，而不允许自动猜测修 Round / Snapshot 的原因。

### 10.12 Historical Calculate 不信任 Stats Cache

Historical Calculate 直接读取：

```text
eligible Round records
```

然后传递：

```text
wins
losses
```

给 Historical Core。

所以即使 Stats cache 漂移：

```text
不会直接污染当前 Historical Model input
```

集成测试同时验证 Stats cache 可以独立从 `rounds` 重建。

### 10.13 Maintenance 与 Stats

Maintenance 读取：

```text
active Regime
+
对应 Stats
```

形成：

```text
included_sample_count
```

如果 active Regime 没有对应 Stats：

```text
ApplicationInvariantError
```

而不是临时显示：

```text
0
```

把异常状态隐藏掉。

### 10.14 Stats 更新触发

当前主要触发点：

```text
Start New Regime
    → 创建 zero Stats

Complete + Include
    → rebuild target Stats

Complete + Exclude
    → 不 rebuild，因为 eligible set 不变

Historical Correction
    → rebuild source Character / Regime Stats
```

### 10.15 Correction Old Regime

如果更正的是：

```text
旧 inactive Regime
```

中的 completed history：

```text
只 rebuild 该旧 Regime Stats
```

不会错误修改当前新 active Regime 的 Stats。

### 10.16 Current Stats 与 Old Snapshot 可以不同

随着后来发生：

```text
更多 Round
Correction
Regime changes
```

当前 Stats 可能变化。

旧 Snapshot 保存的是：

```text
当时 analysis
```

因此：

```text
当前 Stats
≠
旧 Snapshot historical values
```

是正常情况。

不能为了让两者看起来一致，自动重写旧 Snapshot。

### 10.17 Regime、Correction、Exclude 的区别

```text
Regime
    分隔历史阶段

Correction
    更正已经完成的局后事实

Exclude
    保留 completed Round，但不让它进入 Historical sample
```

三者解决不同问题。

### 10.18 Regime 也不是 Model Version

```text
Regime number
history_model_version
stats_version
```

彼此独立。

不能因为模型版本升级就自动假定：

```text
必须增加 Regime number
```

也不能因为 Start New Regime 就修改模型版本。

### 10.19 Regime / Stats 核心不变量

必须保持：

```text
每个 active Character 正常情况下恰好一个 active Regime

数据库最多一个 active Regime / Character

每个 Regime 有独立 Stats

新 Regime 从 zero Stats 开始

旧 Round 不重新分配到新 Regime

旧 Snapshot 不因为 Regime Switch 改写

Historical eligibility 同时绑定 Character + Regime

Stats 从 Round source facts 重建

Excluded / pending / voided 不进入 eligible history

Correction 后重建对应 source Regime Stats

Pending Round 全局阻止 Regime Switch

Maintenance 不通过 Stats 泄露 wins/losses
```
---

## 11. Historical Correction：完整审计模型

Historical Correction 用于更正已经完成的 Round 的局后事实。

它不是：

```text
普通 Modify / Recalculate
数据库直接 UPDATE completed row
删除错误历史
```

其设计目标是：

> 保留原错误记录，同时创建一条新的 replacement record 表达更正后的正式事实。

### 11.1 Correction Preconditions

Correction 开始前必须满足：

```text
当前没有 pending Round
目标 Round 存在
目标 Round status = completed
目标 Round 拥有 Snapshot
```

新的：

```text
result
include
```

必须是合法 Boolean。

Correction reason：

```text
必填
```

并且必须是 text。

### 11.2 Correction 只修改局后事实

允许更正：

```text
result
include_character_history
correction reason
```

不能修改：

```text
character_id
history_regime_id
reference_history
p_h_raw
win_odds_raw
lose_odds_raw
win_odds
lose_odds
calculated_at
revision_count
history_exposed
subjective_independence_compromised
Prediction Snapshot
```

如果这些局前事实本身存在问题，Historical Correction 不是处理它们的接口。

### 11.3 Safety Backup 是强制前置条件

真正修改 completed history 前，Correction 必须先创建：

```text
pre_history_correction
```

verified Safety Backup。

如果 Safety Backup 失败：

```text
Correction 必须停止
```

不能降级为：

```text
显示 warning
然后继续修改历史
```

### 11.4 为什么 Backup 在事务之前

Safety Backup 保存的是：

> Correction 执行前完整 live database 的恢复点。

因此：

```text
验证 source
        ↓
verified Safety Backup
        ↓
真正 Correction transaction
```

而不是在 Correction commit 后才补做。

### 11.5 Source Revalidation

Safety Backup 需要时间。

在：

```text
初次读取 source
```

和：

```text
真正进入 Correction transaction
```

之间，source 理论上可能发生变化。

因此事务开始后会重新读取：

```text
Original Round
Original Snapshot
```

并与 preflight source 比较。

如果 source 已经变化：

```text
Correction 必须终止
```

不能继续基于已经过期的确认上下文进行 replacement。

### 11.6 Original A

假设原完成记录：

```text
A
status = completed
```

Correction 后 A：

```text
status = voided

voided_at = correction_time
void_reason = correction reason
last_updated_at = correction_time
```

但 A 原来的：

```text
result
include
completed_at
prediction fields
audit fields
Snapshot
```

继续保留。

也就是说 A 表达：

> 这条 completed history 曾经真实存在，但后来由于 Historical Correction 被正式作废。

### 11.7 Replacement B

同时创建：

```text
B
```

新的：

```text
round_id
```

并设置：

```text
status = completed
supersedes_round_id = A.round_id
```

新的局后事实：

```text
result = corrected result
include = corrected include
```

### 11.8 B 的时间字段

Replacement B：

```text
created_at = correction_time
completed_at = correction_time
last_updated_at = correction_time
```

但：

```text
calculated_at
```

从 A 原样复制。

因为 Correction：

```text
没有重新运行 prediction
```

所以不能把 correction time 假装成新的 calculation time。

### 11.9 B 复制 Prediction Facts

B 从 A 复制：

```text
character_id
history_regime_id

reference_history

p_h_raw

raw odds
numeric odds

calculated_at
revision_count

history_exposed
history_exposed_at

subjective_independence_compromised
```

这些字段表达同一次原始 prediction。

### 11.10 Snapshot Copy

B 的 Snapshot：

```text
复制 A Snapshot
```

除：

```text
round_id
```

之外，分析内容保持一致。

因此保留：

```text
Subjective analysis
Historical analysis
EV
S
Break-Even
model versions
history_data_through_at
last_included_historical_round_id
```

全部原始值。

### 11.11 Correction 不运行 Core

Historical Correction 不调用：

```text
Subjective Core
Historical Core
Odds Core
```

因为它不是一次新的 prediction。

这条规则同时保护：

```text
历史 cutoff
模型版本
当时的 Historical sample
Anti-Anchoring audit
```

### 11.12 Correction Transaction

真正数据变更必须在同一个 UnitOfWork 中完成：

```text
A completed → voided
        ↓
INSERT replacement B
        ↓
INSERT copied Snapshot B
        ↓
rebuild Stats for source Character / Regime
        ↓
commit
```

其中任何 DB mutation 在 commit 前失败：

```text
全部 rollback
```

### 11.13 Safety Backup 与 Transaction Rollback 不同

Correction transaction rollback：

```text
保护本次尚未 commit 的数据库 mutation
```

而：

```text
pre_history_correction Safety Backup
```

是数据库级独立恢复点。

二者不是同一种安全机制。

### 11.14 Correction 对 Stats 的影响

Correction 后需要重新计算：

```text
Original Character
Original Regime
```

的 Stats。

例如：

```text
A = Win + Include
B = Loss + Include
```

eligible historical result 必须从：

```text
Win
```

变成：

```text
Loss
```

如果：

```text
B.include = false
```

则 replacement 不再进入 Historical sample。

### 11.15 Old Regime Correction

如果 A 属于：

```text
inactive old Regime
```

Stats rebuild 仍针对：

```text
A.history_regime_id
```

不会修改当前 active Regime 的 Stats。

### 11.16 Correction Chain

例如：

```text
A completed
↓ correction
A voided → B completed
```

如果以后又发现 B 仍然错误：

```text
B completed
↓ correction
B voided → C completed
```

形成：

```text
A → B → C
```

的审计链。

### 11.17 Branch 不允许

A 已经：

```text
voided
```

不能再次作为 completed Correction target。

同时数据库：

```text
ux_rounds_supersedes
```

保证一个 source Round 最多只有一个 direct replacement。

因此允许：

```text
chain
```

不允许：

```text
A → B
A → C
```

这种 branch。

### 11.18 Correction 与 Pending Void

Pending Void：

```text
pending
→ voided

不创建 replacement
post-run facts 仍为空
Snapshot 保留
```

Historical Correction：

```text
completed original
→ voided completed original
+
new completed replacement
```

两者不能混用。

### 11.19 Correction 与 Recalculate

Recalculate：

```text
尚未完成的当前 prediction
same Round ID
更新 prediction + Snapshot
```

Correction：

```text
已经完成的历史
new replacement Round ID
只修改局后事实
Snapshot 不重新计算
```

### 11.20 Correction 核心不变量

必须保持：

```text
completed history 不原地覆盖

Correction 前没有 pending Round

Correction target 必须 completed

Original Snapshot 必须存在

Correction reason 必填

Safety Backup 必须先成功

真正 mutation 前重新验证 source

Original 变 voided 但保留旧 post-run facts

Replacement 使用新 round_id

Replacement supersedes Original

Prediction facts 全部复制

calculated_at 保持原值

Replacement created/completed time 使用 correction time

Snapshot 除 round_id 外完整复制

Correction 不运行 Core

A void + B insert + B snapshot + Stats rebuild 同事务

Correction chain 可以延长但不能 branch
```

---

## 12. Recovery：未完成单局恢复

Recovery 解决：

> 应用退出或崩溃后，live database 中仍存在一个合法 pending Round。

Recovery 不是重新计算，也不是数据库 Restore。

### 12.1 Startup Recovery Classification

启动检查 pending count：

```text
0
→ READY_DRAFT

1
→ READY_RECOVERY

2+
→ RECOVERY_ERROR
```

一个 pending Round 是受支持的正常持久化状态。

多个 pending Round 属于数据不变量异常。

### 12.2 Recovery Inspect

Workflow 从：

```text
DRAFT
```

调用 Recovery inspect。

一个 pending 时：

```text
→ RECOVERY
```

此时可以显示有限的恢复预览。

但尚未正式把 analysis 恢复成当前 locked view。

### 12.3 Continue Recovery

用户明确点击：

```text
Continue
```

后，RecoveryService 读取：

```text
same pending Round
same Snapshot
```

然后构造 committed analysis view。

### 12.4 Recovery 不运行 Core

Continue Recovery 不调用：

```text
Subjective Model
Historical Model
Odds Analysis
```

因为数据库中已经存在当时正式 committed Snapshot。

重新计算会使用：

```text
现在的历史
```

而不是：

```text
当时 Calculate / Recalculate 的历史
```

从而破坏审计。

### 12.5 Recovery 不写数据库

正常 Recovery Continue：

```text
只读
```

不会：

```text
UPDATE Round
UPDATE Snapshot
revision_count += 1
```

也不会改变：

```text
calculated_at
history_data_through_at
```

### 12.6 Recovery 不生成新 ID

恢复的是：

```text
原 Round
```

所以：

```text
round_id
```

必须保持。

Recovery 不调用：

```text
IdGenerator
```

### 12.7 Recovery 不取得新 Clock Time

Recovery 不是一个新的业务事实写入。

因此：

```text
不调用 Clock
```

也不会把：

```text
created_at
calculated_at
last_updated_at
history_exposed_at
```

更新成应用重启时间。

### 12.8 Recovery 后 Prediction Revision Locked

Recovery 成功后：

```text
PENDING_LOCKED
```

但：

```text
prediction revision locked = true
```

因此：

```text
Modify
Recalculate
```

不可再使用。

### 12.9 为什么采用保守 Lock

数据库只能知道：

```text
result = NULL
include = NULL
```

但这些局后 choice 本来在 Confirm Save 之前只存在内存。

如果应用在：

```text
用户已经看到结果
但尚未 Confirm Save
```

时崩溃，数据库无法证明这一点。

所以 Recovery 采用：

```text
knowledge may already exist
→ lock revision
```

而不是重新开放 Modify。

### 12.10 Result / Include 不从内存恢复

Recovery 后：

```text
result = None
include = None
```

用户需要重新选择。

因为它们不是 durable facts。

### 12.11 PENDING_EDIT Crash

假设：

```text
committed Revision 0
        ↓
Modify
        ↓
PENDING_EDIT candidate
        ↓
crash
```

Candidate 没有持久化。

重启 Recovery 得到：

```text
Revision 0
```

不是内存 candidate。

这正是：

```text
committed facts
```

与：

```text
uncommitted edit memory
```

的边界。

### 12.12 Multiple Pending

如果存在：

```text
2+
```

pending：

```text
不能选最新
不能选最旧
不能让用户任选
```

系统进入：

```text
RECOVERY_ERROR
```

并将 Runtime 视为 unsafe。

### 12.13 Recovery 与 Restore

```text
Recovery
    不替换 database
    继续 live DB 中 pending Round

Restore
    使用 backup 替换 probability.db
```

Restore 后如果新的 live database 自己包含一个 pending Round：

```text
Restore 完成
→ READY_RECOVERY
→ 再走普通 Recovery
```

### 12.14 Recovery 核心不变量

```text
同一个 Round
同一个 Snapshot
不运行 Core
不写 DB
不生成 ID
不更新时间
不恢复未持久化 Candidate
不恢复内存 result/include
Recovery 后锁死 prediction revision
多个 pending 不自动猜测
Recovery 与 Restore 严格分离
```

---

## 13. Backup、Restore 与 Emergency Recovery

数据安全系统包括：

```text
Recent Backup
Daily Backup
Safety Backup
Normal Restore
Emergency Restore
Emergency Recovery state
```

它们处理不同风险。

### 13.1 Live Database

默认 live database：

```text
%LOCALAPPDATA%\ProbabilityCalibrationTool\data\probability.db
```

Backup pools：

```text
%LOCALAPPDATA%\ProbabilityCalibrationTool\backups\recent
%LOCALAPPDATA%\ProbabilityCalibrationTool\backups\daily
%LOCALAPPDATA%\ProbabilityCalibrationTool\backups\safety
```

删除应用解压目录：

```text
≠
删除用户数据库
```

### 13.2 Backup Categories

当前：

```text
RECENT
DAILY
SAFETY
```

三个独立 pool。

### 13.3 Recent Backup

关键业务操作成功 commit 后创建 Recent Backup。

当前包括：

```text
Complete Pending
Void Pending
Start New Regime
Historical Correction
```

普通：

```text
Calculate
Recalculate
```

不通过这一 post-commit机制自动创建 Recent Backup。

### 13.4 Recent 是 Post-Commit

顺序：

```text
business transaction commit
        ↓
Recent Backup
```

因此 Recent Backup 失败：

```text
不能撤销已经成功 commit 的主数据
```

只产生 warning。

### 13.5 Recent Retention

有效 Recent Backup 当前保留：

```text
最新 5 个
```

轮换只针对：

```text
VALID
```

Backup。

### 13.6 Daily Backup

Daily Backup 是 Startup reliability 的最后阶段之一。

按：

```text
用户本地日历日期
```

判断当天是否已经存在有效 Daily。

### 13.7 Daily Retention

有效 Daily Backup 保留：

```text
最近 7 个不同本地日期
```

不是简单最后七个文件。

### 13.8 Daily Failure

普通 Daily Backup 失败：

```text
产生 warning
```

但不会把健康 live database 标记为失败。

### 13.9 Safety Backup

用于高风险操作前。

当前 reason：

```text
pre_migration
pre_restore
pre_history_correction
```

Safety Backup 失败时，相应高风险操作必须停止。

### 13.10 Safety Retention

有效 Safety Backup 当前独立保留：

```text
最新 10 个
```

### 13.11 Backup Creation

正式 SQLite Backup 大致：

```text
创建 temporary candidate
        ↓
检查 live source
        ↓
SQLite Online Backup
        ↓
验证 candidate
        ↓
验证 Schema
        ↓
fsync
        ↓
os.replace → final backup
```

不会简单复制正在工作的：

```text
probability.db
```

文件。

### 13.12 Backup Inventory

候选文件分类：

```text
VALID
CORRUPT
TEMPORARY
QUARANTINE
UNRELATED
```

只有：

```text
VALID
```

进入正常 Restore catalog。

### 13.13 Corrupt Backup 不自动删除

发现损坏 Backup 时：

```text
保留
```

供诊断或人工恢复。

不会因为 retention 自动把其视作普通旧 backup 清除。

### 13.14 Over-Retention

如果删除过期 Backup 失败：

```text
停止继续删除
保留超额文件
产生 BACKUP_OVER_RETENTION warning
```

安全策略是：

> 宁可多保留，也不在异常状态下继续批量删除。

### 13.15 Backup Catalog

UI 不直接操作任意文件系统路径。

BackupCatalogService：

```text
扫描 VALID backup
        ↓
生成 session-local candidate_id
        ↓
UI 只持有 opaque candidate handle
```

### 13.16 Candidate Handle Lifetime

每次 catalog refresh：

```text
旧 candidate handles 失效
```

过期 handle 不能继续 Restore。

### 13.17 Restore 会再次验证 Candidate

即使某文件曾经出现在 VALID 列表：

```text
真正 Restore 前仍重新验证
```

因为 catalog 与用户确认之间，文件可能已经发生变化。

### 13.18 Restore 不修改原 Backup

Restore 先复制 candidate 到：

```text
.restore_*.tmp
```

后续：

```text
migration
Stats repair
validation
```

只发生在 temporary restore copy。

原 Backup 保持不变。

### 13.19 Candidate Sidecars

如果 Backup Candidate 存在：

```text
-journal
-wal
-shm
```

sidecars，则拒绝正常 Restore candidate。

### 13.20 Normal Restore

Normal Restore 用于：

```text
当前 live database 健康
用户明确想恢复旧 Backup
```

不是损坏数据库的强制恢复通道。

### 13.21 Normal Restore Preconditions

要求：

```text
live DB health valid
Application invariants valid
没有 pending Round
Runtime 可以进入 quiescent state
candidate valid
```

### 13.22 Pre-Restore Safety Backup

Normal Restore 在替换健康 live database 前必须成功创建：

```text
pre_restore
```

Safety Backup。

顺序：

```text
验证 candidate
        ↓
pre_restore Safety Backup
        ↓
replace live DB
```

### 13.23 Runtime Quiescence

Restore 文件替换前要求：

```text
没有 active managed UoW
Runtime 未 paused
Runtime Lock 仍 held
```

进入 quiescent 后：

```text
禁止新 Managed UoW
```

直到 Restore window 结束。

### 13.24 Unknown Live Sidecar

Normal Restore 如果发现 live DB 周围存在无法解释的：

```text
-journal
-wal
-shm
```

会停止。

不会直接删除这些文件继续替换。

### 13.25 Normal Restore Success

validated temporary copy：

```text
os.replace
        ↓
成为新 probability.db
        ↓
post-replacement verification
```

然后重新判断：

```text
0 pending → READY_DRAFT
1 pending → READY_RECOVERY
2+ pending → RECOVERY_ERROR
```

### 13.26 Restore 到 Pending Backup

如果 Backup 中有：

```text
1 pending Round
+
Snapshot
```

成功 Restore 后：

```text
READY_RECOVERY
```

不会自动重新 Calculate。

### 13.27 Emergency Restore

Emergency Restore 用于：

```text
当前 live database unsafe
```

例如 Startup 已进入：

```text
EMERGENCY_RECOVERY
```

### 13.28 Healthy Runtime 不能使用 Emergency Restore

Emergency Restore 不是：

```text
跳过 Normal Restore 安全检查
```

的高级按钮。

健康 Runtime 必须使用 Normal Restore。

### 13.29 Emergency Candidate 仍必须先验证

即使 live DB 已损坏：

```text
Candidate 仍先完整 prepare / validate
```

不能：

```text
先覆盖损坏 live
再验证 candidate
```

### 13.30 Emergency Quarantine

Emergency Restore 尝试保存旧损坏：

```text
main DB
sidecars
```

为：

```text
UNVERIFIED_CORRUPT_...
```

诊断副本。

它不是：

```text
verified Safety Backup
```

### 13.31 Quarantine Copy 是 Best-Effort

旧损坏数据 copy 失败：

```text
QUARANTINE_COPY_FAILED
```

可以成为 warning。

但旧 SQLite sidecars 的安全隔离是强制要求。

### 13.32 Replacement Boundary

Restore 最重要的安全边界：

```text
replacement 尚未成功
```

与：

```text
replacement 已经成功
```

必须严格区分。

### 13.33 Pre-Replacement Failure

例如：

```text
invalid candidate
Safety Backup failure
Runtime busy
copy failure
validation failure
os.replace 尚未成功
```

此时：

```text
旧 live database 必须保持原样
```

如果原 Runtime 健康，也不能因为一次 Restore 操作失败就把：

```text
runtime.result
```

污染成 unsafe。

### 13.34 Post-Replacement Failure

如果：

```text
os.replace 已成功
```

但新 live DB post-check 失败：

```text
不能假装 Restore 未发生
```

系统不会静默再次替换回旧 DB。

而是：

```text
runtime.unsafe_database = true
→ EMERGENCY_RECOVERY
```

### 13.35 为什么不自动回滚 Replacement

已经成功：

```text
os.replace
```

属于 filesystem durable boundary。

普通 SQLite transaction rollback 无法撤销。

自动进行第二次隐式文件替换本身又是新的高风险操作。

因此当前选择：

```text
显式进入 Emergency Recovery
```

### 13.36 Restore 后 Session 必须重建

成功 Restore 后：

```text
旧 DesktopSession
旧 Workflow
旧 Maintenance cache
旧 Correction cache
旧 Restore handles
旧 confirmation tickets
```

全部作废。

DesktopHost 根据新：

```text
RuntimeResult
```

重新构造 Session / Window。

### 13.37 Old Callback 也必须失效

即使 Restore 前已经捕获：

```text
old_workflow.calculate
old_session.maintenance_rows
old_catalog.refresh
```

Restore 后也不能继续调用。

旧 Session lifetime 被 revoke。

### 13.38 Recovery / Restore / Emergency Recovery

```text
Recovery
    继续当前 pending Round

Normal Restore
    健康 live DB → verified backup

Emergency Restore
    unsafe live DB → verified backup

Emergency Recovery
    Runtime safety disposition
```

四者不能混淆。

---

## 14. Startup Safety、Application Invariants 与 Stats Repair

Startup 不是简单：

```text
打开 SQLite
→ 显示窗口
```

而是一条数据安全验证链。

### 14.1 StartupDisposition

当前：

```text
READY_DRAFT
READY_RECOVERY
RECOVERY_ERROR
EMERGENCY_RECOVERY
UNSUPPORTED_NEWER_SCHEMA
ALREADY_RUNNING
DATA_SAFETY_ERROR
```

它们是 Runtime / Startup state，不是 WorkflowState。

### 14.2 READY_DRAFT

表示：

```text
数据库健康
pending_count = 0
```

可以建立正常 DesktopSession，Workflow 从 DRAFT 开始。

### 14.3 READY_RECOVERY

表示：

```text
数据库健康
pending_count = 1
```

属于受支持状态。

### 14.4 RECOVERY_ERROR

主要表示：

```text
pending_count > 1
```

这违反正常产品不变量。

Runtime 标记 unsafe。

### 14.5 EMERGENCY_RECOVERY

表示：

> 当前 live database 已不能被正常业务层安全访问，需要数据库级恢复。

### 14.6 UNSUPPORTED_NEWER_SCHEMA

如果：

```text
user_version > supported version
```

旧程序拒绝：

```text
写入
降级
猜测 Schema
```

### 14.7 ALREADY_RUNNING

Runtime Lock 已被另一实例持有时：

```text
ALREADY_RUNNING
```

第二实例不会继续进入正常数据库业务路径。

### 14.8 Fresh Database 判定

只有：

```text
live database path 真正不存在
```

才允许 Fresh Initialization。

以下都不是 Fresh：

```text
0-byte probability.db
空 SQLite
损坏文件
已有 user_version=0 SQLite
```

### 14.9 为什么不能把 0-byte 当 Fresh

程序无法证明 0-byte 文件是：

```text
新安装
```

还是：

```text
数据损坏
误覆盖
文件系统事故
```

自动初始化会把潜在数据事故伪装成新用户。

所以：

```text
路径存在
→ 视为 existing user data
```

### 14.10 Fresh Initialization 使用 Temporary DB

初始化先创建：

```text
.initialize_*.tmp
```

完整流程：

```text
initialize_v1
        ↓
SQLite health
        ↓
Application invariants
        ↓
Stats validation(repair=False)
        ↓
确认 live path 仍不存在
        ↓
fsync
        ↓
os.replace → probability.db
```

### 14.11 Initialization Failure

任何步骤失败：

```text
不安装正式 live DB
清理 temporary file
```

避免留下半初始化数据库。

### 14.12 SQLite Health

Existing DB 首先检查：

```text
PRAGMA integrity_check
PRAGMA user_version
核心 table inventory
```

SQLite Health 回答：

> SQLite 文件结构是否可正常读取？

### 14.13 Application Invariants

之后检查：

> 表中的业务事实彼此是否仍符合产品合同？

例如：

```text
Frozen Character identities
Active Regime structure
Round ↔ Snapshot
Round lifecycle facts
Exposure audit
Correction chain
Historical source links
```

SQLite integrity OK 不等于业务事实一定正确。

### 14.14 Frozen Character Identity

当前 34 Character 的：

```text
character_id
internal_code
display_name
tainted
pair_row
```

必须与冻结 seed 一致。

发现异常：

```text
报告 invariant failure
```

而不是自动覆盖回正确值。

### 14.15 Active Regime

每个 active Character：

```text
必须恰好一个 active Regime
```

Application invariant 会再次检查。

### 14.16 Round ↔ Snapshot

必须满足：

```text
每个 Round 恰好一个 Snapshot
每个 Snapshot 必须对应 Round
```

Missing Snapshot：

```text
不能自动重算
```

因为无法恢复当时 Historical world state。

### 14.17 Lifecycle Facts

Invariant Service 再次检查：

```text
pending shape
completed shape
voided shape
```

不能仅依赖 Schema CHECK。

### 14.18 Exposure Audit

要求：

```text
history_exposed
↔
history_exposed_at exists
```

并且：

```text
subjective_independence_compromised = true
→ history_exposed = true
```

### 14.19 Visible History Authority

如果：

```text
reference_history = true
Snapshot Historical status = VALID
```

但：

```text
history_exposed = false
```

属于不变量错误。

不能直接展示历史。

### 14.20 Historical Source Link

如果 Snapshot 保存：

```text
last_included_historical_round_id
```

则 source Round 必须：

```text
存在
不是当前 Round
same Character
same Regime
calculated_at 不晚于当前 prediction
```

### 14.21 Correction Graph Invariants

检查：

```text
parent exists
parent voided
replacement not pending
no branch
no cycle
```

并检查 replacement prediction facts 与 predecessor 一致。

### 14.22 Replacement Snapshot Invariant

Correction replacement Snapshot 除：

```text
round_id
```

之外必须与 predecessor Snapshot 一致。

否则说明 Historical Correction 偷偷重写了 prediction。

### 14.23 Multiple Pending Priority

Startup 一旦发现：

```text
pending_count > 1
```

优先进入：

```text
RECOVERY_ERROR
```

并阻止 Daily Backup。

### 14.24 Source Invariant Failure

普通 source invariant issue：

```text
DATA_SAFETY_ERROR
```

不会：

```text
自动修 Round
自动修 Snapshot
创建正常 Daily Backup
```

### 14.25 Stats 是 Repairable Exception

`character_stats` 明确被排除在 source-fact corruption 之外。

因为它可以从：

```text
rounds
```

确定性重建。

### 14.26 Stats Validation 覆盖所有 Regime

检查：

```text
active Regime
inactive historical Regime
```

所有 Stats。

### 14.27 Stats Expected Values

根据 eligible history 计算：

```text
included_games = number of eligible rounds
wins = result true count
losses = included_games - wins
last_included_round_id = chronology last
stats_version = current version
```

### 14.28 Stats Repair

如果：

```text
row missing
counts wrong
last ID wrong
stats_version wrong
```

则可以：

```text
rebuild from rounds
```

### 14.29 Stats Repair Batch Atomicity

一次 Startup Stats repair 中，如果多个 Regime 需要修复：

```text
同一个 UnitOfWork
```

任何中途失败：

```text
整个 repair batch rollback
```

不能只修一半。

### 14.30 Repair Direction

必须始终：

```text
Source Round Facts
        ↓
Character Stats
```

不能：

```text
为了让 Stats 对得上
→ 修改 Round
```

### 14.31 Repairability Boundary

可以自动修：

```text
character_stats
```

不能猜测修：

```text
characters
history_regimes
rounds
round_analysis_snapshots
Exposure audit
Correction audit
```

### 14.32 Final Health

Stats validation / repair 成功后：

```text
再次 SQLite health verify
```

然后才进入 Daily Backup。

### 14.33 Daily Backup 在最后

Startup 核心顺序：

```text
Runtime Lock
        ↓
SQLite Health
        ↓
Schema Version
        ↓
Migration if explicitly supported
        ↓
Application Invariants
        ↓
Pending classification
        ↓
Stats validation / repair
        ↓
Final SQLite Health
        ↓
Daily Backup
        ↓
Ready disposition
```

### 14.34 Unsafe Runtime UoW Admission

正常 Managed UoW 只允许：

```text
READY_DRAFT
READY_RECOVERY
```

其它 safety dispositions 不能继续正常业务数据库写入。

---

## 15. Runtime、DesktopSession 与权限边界

系统有三层不同状态：

```text
Runtime state
Session state
Workflow state
```

它们不能互相替代。

### 15.1 RuntimeContext

RuntimeContext 持有：

```text
Application Runtime Lock
Logger
ReliabilityResult
unsafe_database state
managed UoW activity count
restore pause state
closed state
```

它覆盖整个当前应用运行生命周期。

### 15.2 Managed UoW Admission

新的 Managed UoW 进入前要求：

```text
Runtime 未关闭
Runtime 未 paused
Runtime Lock held
unsafe_database = false
runtime.result exists
disposition = READY_DRAFT or READY_RECOVERY
```

否则拒绝。

### 15.3 Active UoW Count

Runtime 记录当前：

```text
_active
```

Managed UoW 数量。

这让 Restore 可以证明：

```text
当前没有 Runtime 管理中的数据库 connection
```

### 15.4 `quiescent()`

Restore 使用：

```text
runtime.quiescent()
```

要求：

```text
_active = 0
未 paused
未 closed
lock held
```

成功进入后：

```text
paused = true
```

新的 Managed UoW 被阻止。

### 15.5 Quiescent 不强制杀事务

如果已有 active UoW：

```text
Restore 被拒绝
```

而不是：

```text
强制 rollback / close existing transaction
```

### 15.6 Runtime Close

Runtime close 要求：

```text
无 active UoW
无 restore pause
```

之后：

```text
关闭 logger
释放 Runtime Lock
```

### 15.7 DesktopSession

正常 Runtime 创建一个 DesktopSession。

DesktopSession 组合：

```text
Workflow
RoundService
RecoveryService
MaintenanceService
RegimeService
CorrectionService
Backup integration
Backup catalog
```

它不是第二套业务逻辑。

### 15.8 Only One Real Workflow

DesktopSession 只有一个正式：

```text
Workflow
```

UI 不应维护另一套独立业务状态机。

### 15.9 GuardedWorkflow

DesktopSession 对外使用 GuardedWorkflow。

其职责：

```text
每次实际 callback 调用时
重新验证 Session 是否仍有效
```

但不重新实现 Workflow transition rules。

### 15.10 Session Dispose

Session dispose 后：

```text
confirmation tickets 清空
warnings 清空
session marked disposed
```

任何旧调用：

```text
DisposedSessionError
```

### 15.11 Captured Callback 也必须失效

即使此前已经保存：

```text
callback = old_session.workflow.calculate
```

Session Dispose 后执行 callback：

```text
仍必须被 guard 拒绝
```

这防止 Restore 后 stale Qt event 修改新数据库。

### 15.12 Normal DesktopSession 只存在于 Healthy Runtime

只有：

```text
READY_DRAFT
READY_RECOVERY
```

可以创建 Normal DesktopSession。

Unsafe state 使用：

```text
RestoreSession
```

### 15.13 RestoreSession

RestoreSession 故意：

```text
没有 Workflow
没有 normal business UoW
```

只提供 Safety / Restore 所需能力。

这是一种 capability isolation，而不是简单隐藏按钮。

### 15.14 Administrative Operations

当前高影响操作：

```text
Start New Regime
Historical Correction
Normal Restore
```

要求：

```text
Healthy Runtime
Active DesktopSession
WorkflowState = DRAFT
Session not busy
```

### 15.15 Session Busy

`busy` 是 DesktopSession 高层操作互斥状态。

它不是：

```text
SQLite transaction lock
WorkflowState
```

### 15.16 Confirmation Ticket

高影响操作采用：

```text
begin
→ issue one-shot ticket
→ user confirm
→ consume ticket
→ execute
```

Ticket 是：

```text
session-local
in-memory
opaque
```

授权。

### 15.17 Ticket Identity Binding

例如：

```text
Regime ticket
→ character_id

Correction ticket
→ round_id

Restore ticket
→ backup candidate_id
```

不能拿旧 ticket 对新的 target 执行操作。

### 15.18 New Ticket Invalidates Old

同一种 operation 重新 begin：

```text
新 ticket 替换旧 ticket
```

旧确认立即失效。

### 15.19 Consume Before Execute

真正业务操作前：

```text
consume ticket
```

然后才调用 Service。

所以：

> 一次确认最多驱动一次执行尝试。

即使业务执行失败，旧 ticket 也不会恢复。

### 15.20 Stale Cancel

过期 UI interaction 的 Cancel 只能撤销：

```text
与其 ticket identity 完全匹配
```

的 authority。

不能撤销后来生成的新确认。

### 15.21 Navigation Revokes Confirmation

例如：

```text
Back
Reload
page switch
重新选择对象
```

会使不再匹配当前交互上下文的 confirmation 失效。

### 15.22 Confirmation 不替代业务检查

Ticket 只证明：

> 用户在当前 Session 中确认过这个目标。

它不证明：

```text
数据库仍健康
source 没变化
target 仍 completed
没有 pending
Backup candidate 仍 valid
```

Service 必须再次验证。

### 15.23 DesktopHost

DesktopHost 根据：

```text
RuntimeResult
```

建立：

```text
Normal DesktopSession + Main Window
```

或：

```text
RestoreSession + Safety Window
```

### 15.24 Restore Routing

Normal DesktopSession 只能请求：

```text
Normal Restore
```

Emergency Restore 只在允许的 unsafe Safety state 开放。

### 15.25 Restore 后 Reroute

如果 Restore 真正改变：

```text
runtime.result
```

DesktopHost：

```text
dispose old session
close old window
重新 route
创建 new session/window
```

### 15.26 Pre-Replacement Failure

如果 Normal Restore 在 replacement 前失败：

```text
runtime.result 未改变
```

正常旧 Session 继续有效。

不能因为用户选了坏 Backup 就无故销毁健康 Workflow。

### 15.27 Session State 不持久化

以下均为 transient：

```text
busy
confirmation tickets
disposed
UI selections
page caches
candidate handles
session warnings
```

它们不写核心 SQLite。

### 15.28 Runtime / Session / Workflow 与 Durable Facts

```text
Runtime
Session
Workflow memory
    → transient

Round
Snapshot
Regime
Correction audit
Exposure audit
    → durable
```

Recovery 只从 durable facts 重建。

---

## 16. Error Handling、Safe Presentation 与 Logging

错误处理分成：

```text
业务是否失败
用户应该看到什么
开发者日志应该保留什么
```

不能简单：

```text
except Exception:
    show(str(exc))
```

### 16.1 ApplicationError

Application 层使用稳定错误类别，例如：

```text
BusinessRuleError
InputValidationError
InvalidWorkflowTransitionError
ApplicationInvariantError
```

并搭配：

```text
ErrorCode
```

### 16.2 ErrorCode

ErrorCode 用于：

```text
稳定业务语义
Localization mapping
Presentation routing
```

而不是直接把 exception string 当 UI 文案。

### 16.3 Public Expected Error Whitelist

只有显式批准的：

```text
ErrorCode
```

可以走 expected user presentation。

内部错误即使恰好有 ErrorCode，也不能自动把原 exception message 释放给用户。

### 16.4 Input Validation

InputValidationError 还携带：

```text
field
```

例如：

```text
p_h_raw
win_odds_raw
lose_odds_raw
character_id
reason
```

UI 可以在对应字段附近显示错误。

### 16.5 Business Rule Error

例如：

```text
CURRENT_STATE
REVISION_CLOSED
CONFIRMATION_EXPIRED
HEALTHY_DRAFT_REQUIRED
```

通常显示全局安全业务提示。

### 16.6 Unexpected Error

未预期异常：

```text
不直接显示 str(exc)
不直接显示 repr(exc)
```

而是：

```text
生成 Error ID
写完整日志
返回 Safe ErrorPresentation
```

### 16.7 ErrorPresentation

核心字段：

```text
message
error_id
safe error code
```

默认 generic 用户文案类似：

```text
The operation could not be completed.
Error ID: <uuid>
```

### 16.8 Error ID

Error ID 是：

```text
用户错误提示
↔
开发者 diagnostic log
```

之间的 correlation ID。

它不是业务 identity，也不是错误类别。

### 16.9 Diagnostic Log

日志可以保留：

```text
Error ID
exception class
exception text
Traceback
internal path
SQL diagnostic
```

因为它服务于开发者排查。

### 16.10 UI 禁止暴露内部信息

正常用户错误 presentation 不应直接包含：

```text
Traceback
Raw SQL
内部绝对路径
Python exception class
Repository implementation details
```

### 16.11 SafeErrorCode

内部 failure 包装后的安全高层结果，例如：

```text
OPERATION_FAILED
RESTORE_NOT_REPLACED
RESTORE_RECOVERY_REQUIRED
RECENT_BACKUP_FAILED
DAILY_BACKUP_FAILED
```

与普通 Application ErrorCode 属于不同层。

### 16.12 Restore Safe Errors

Pre-replacement failure 可以明确告诉用户：

```text
Restore did not replace the live database.
```

Post-replacement failure 则必须表达：

```text
Replacement requires emergency recovery.
```

因为二者的数据安全含义完全不同。

### 16.13 Warning

Warning 可以表达：

```text
Stats rebuilt
Recent backup failed
Daily backup failed
Backup over-retention
Quarantine copy failed
```

它不一定表示主业务失败。

### 16.14 Business Success + Warning

例如：

```text
Round Complete commit 成功
Recent Backup 失败
```

最终：

```text
Round 仍 completed
+
显示 Backup warning
```

不能把 Workflow 画回未保存状态。

### 16.15 Single Execution

DesktopBoundary 核心原则：

```text
One execution
One authoritative re-render
Then errors/warnings
Never retry
```

### 16.16 为什么不能 Retry

如果：

```text
业务 commit 已成功
UI render 失败
```

自动重试业务操作可能造成：

```text
double completion
duplicate replacement
duplicate Regime
duplicate backup
```

所以 presentation failure 不得驱动业务 retry。

### 16.17 Authoritative Re-Render

操作结束后，无论 success/failure：

```text
先从 Workflow / Session 获取当前权威状态
重新 render
然后显示 error/warning
```

错误文字不能成为状态来源。

### 16.18 Pre-Action Render Failure

如果操作前连当前权威 UI 都不能成功构造：

```text
不执行业务 operation
```

### 16.19 Presentation Failure

如果：

```text
业务成功
post-operation render 失败
```

数据库已提交事实继续保留。

错误边界只报告 presentation error。

### 16.20 Duplicate Invocation Guard

UI boundary 使用 operation-active guard，避免：

```text
double-click
queued duplicate
reentrant callback
```

在同一 presentation operation 中重复执行。

它与：

```text
Session busy
SQLite transaction
```

是不同层。

### 16.21 Localization Failure Fallback

如果连 safe error translation 都失败：

```text
使用固定 English fallback
仍保留 Error ID
```

不能退回原始 exception text。

### 16.22 Logging Lifetime

正式 rotating log：

```text
%LOCALAPPDATA%\ProbabilityCalibrationTool\logs\app.log
```

在取得 Runtime Lock 后才打开。

### 16.23 Current Log Rotation

当前：

```text
maxBytes = 2 MiB
backupCount = 5
encoding = UTF-8
```

日志不是永久业务审计。

### 16.24 Business Audit vs Log

SQLite：

```text
业务事实
历史审计
可恢复数据
```

Log：

```text
运行诊断
exception traceback
Error ID
```

二者不能互相替代。

---

## 17. 时间、ID 与确定性排序

时间与 ID 是审计合同的一部分。

### 17.1 Clock

Application 通过可注入：

```text
Clock
```

取得当前时间。

生产实现返回：

```text
aware UTC datetime
```

### 17.2 UTC Normalization

Clock 返回值必须：

```text
是 datetime
具有 timezone
具有有效 UTC offset
```

随后统一：

```text
astimezone(UTC)
```

### 17.3 Naive Datetime 拒绝

例如：

```text
datetime(2026, 9, 4, 12, 0)
```

不能被默认为：

```text
UTC
```

或：

```text
local time
```

必须明确 timezone。

### 17.4 SQLite Timestamp Format

标准持久化：

```text
YYYY-MM-DDTHH:MM:SS.ffffffZ
```

其中：

```text
Z = UTC
```

### 17.5 Local Time 只属于 Presentation

数据库：

```text
UTC
```

UI：

```text
按用户本地时区格式化
```

例如标签：

```text
Calculated locally
Started locally
```

并不意味着 SQLite 存储本地时间。

### 17.6 `created_at`

表示：

> 当前 Round identity 创建时间。

Calculate 首次创建。

普通 Recalculate 不改变。

### 17.7 `calculated_at`

表示：

> 当前 committed prediction revision 的计算时间。

Calculate：

```text
= T0
```

Recalculate：

```text
= new time
```

### 17.8 `last_updated_at`

表示：

> 当前 Round 最近一次正式持久化业务修改时间。

会在：

```text
Calculate
Recalculate
Complete
Void
Correction
```

等操作中更新。

### 17.9 `completed_at`

只表示：

```text
Round 正式完成时间
```

Pending 时为空。

### 17.10 `voided_at`

只表示：

```text
Round 正式 void 时间
```

包括：

```text
Pending Void
Historical Correction Original
```

### 17.11 `history_exposed_at`

表示：

> 第一次 durable Historical exposure 时间。

后续 Recalculate：

```text
sticky
```

不会不断刷新成最新 calculation time。

### 17.12 Snapshot Cutoff

```text
history_data_through_at
```

表示：

> 构造该 Snapshot 时 Historical query 的 cutoff。

### 17.13 Recovery 不更新时间

Recovery：

```text
不调用 Clock
```

因为没有创建新持久化业务事实。

### 17.14 Recalculate 时间

Recalculate：

```text
round_id unchanged
created_at unchanged
calculated_at = now
last_updated_at = now
revision_count += 1
```

### 17.15 Complete 时间

Complete：

```text
completed_at = now
last_updated_at = now
```

但：

```text
calculated_at unchanged
```

### 17.16 Void 时间

Void：

```text
voided_at = now
last_updated_at = now
```

但：

```text
calculated_at unchanged
```

### 17.17 Correction 时间

一次 Correction 使用统一：

```text
correction_time
```

Original：

```text
voided_at = correction_time
last_updated_at = correction_time
```

Replacement：

```text
created_at = correction_time
completed_at = correction_time
last_updated_at = correction_time
```

但：

```text
calculated_at = original.calculated_at
```

### 17.18 Regime Switch 时间

同一次 Regime switch：

```text
old.ended_at = now
new.started_at = now
new Stats.updated_at = now
```

使用同一个时间边界。

### 17.19 IdGenerator

Application 通过：

```text
IdGenerator
```

生成 durable identity。

生产实现当前：

```text
UUID4 string
```

### 17.20 Round ID

Calculate：

```text
new round_id
```

Recalculate：

```text
same round_id
```

Recovery：

```text
same round_id
```

Correction：

```text
new replacement round_id
```

### 17.21 Regime ID

每次：

```text
Start New Regime
```

生成新的：

```text
regime_id
```

旧 ID 永远保留。

### 17.22 UUID 不代表时间

UUID4 是随机 identity。

不能把：

```text
round_id
```

本身解释成 creation timestamp。

### 17.23 Historical Chronology

Eligible Historical rows：

```text
ORDER BY calculated_at ASC, round_id ASC
```

主要时间键：

```text
calculated_at
```

`round_id` 只作为相同 calculated_at 时的 deterministic tie-breaker。

### 17.24 为什么不用 `completed_at`

Historical chronology 表达：

```text
prediction calculation order
```

而不是：

```text
outcome completion order
```

### 17.25 为什么不用 `last_updated_at`

Correction / Complete 会改变：

```text
last_updated_at
```

如果用它排序，会把旧 prediction 错误移动到最新位置。

### 17.26 Correction Replacement Chronology

Replacement：

```text
created_at = correction time
calculated_at = original calculation time
```

因此 Historical sample 中仍保持原 prediction chronology。

### 17.27 Correction Candidate Browsing

Historical Correction UI 可以采用不同排序：

```text
completed_at DESC
round_id
```

因为它服务的是：

```text
最近完成记录优先浏览
```

而不是 Historical Model chronology。

### 17.28 Display Name 不参与 Identity

Character identity：

```text
character_id
```

不依赖：

```text
Isaac
以撒
```

等显示名。

Localization 不能改变持久 identity。

---

## 18. 架构边界与依赖方向

当前主要分层：

```text
core
domain
application
persistence
infrastructure
ui
```

以及：

```text
desktop_host.py
bootstrap.py
localization.py
```

### 18.1 Core

Core 负责：

```text
纯数学
数值验证
Probability
EV
S
Odds Combination
Model Relation
```

它不负责：

```text
SQLite
Workflow
Backup
Restore
Qt UI
```

### 18.2 Core 不知道 Round

Core 接收数学 inputs，例如：

```text
p_h_raw
wins
losses
odds
```

不需要知道：

```text
round_id
regime_id
database
```

### 18.3 Historical Eligibility 不属于 Core

Core 只接受：

```text
wins
losses
```

哪些 Round 能进入 Historical Model，由：

```text
Application + Persistence
```

决定。

### 18.4 Domain

Domain 提供共享业务数据结构：

```text
Records
Enums
DTOs
```

例如：

```text
RoundRecord
RoundAnalysisSnapshotRecord
RoundStatus
HistoryModelStatus
EvState
```

### 18.5 Application

Application 负责：

```text
业务规则
Use Cases
Workflow
Transaction orchestration
Recovery
Correction
Regime
Startup
Restore
```

它决定：

> 数学什么时候允许运行、数据库事实什么时候允许改变。

### 18.6 Analysis Builder

Application analysis builder 负责：

```text
验证 Application input
        ↓
调用 Core
        ↓
组合完整 Snapshot
```

Snapshot assembly 不属于单个 Core 数学函数。

### 18.7 Persistence

Persistence 负责：

```text
SQLite Schema
Connection
UnitOfWork
Repositories
Migration
Serialization
Seed
```

Repository 不拥有完整 Workflow transition 权限。

### 18.8 Repository 不运行概率模型

正确路径：

```text
Persistence
→ eligible rows

Application
→ wins/losses

Core
→ Historical estimate
```

不能让 SQLite Repository 自己调用 SciPy 完成模型。

### 18.9 Infrastructure

Infrastructure 负责技术能力：

```text
Backup
Restore engine
SQLite health
Runtime lock
Logging
Paths
Error reporting
```

它不决定概率业务语义。

### 18.10 Ports

Application 对部分基础设施使用明确能力接口，例如：

```text
Clock
IdGenerator
SafetyBackupPort
```

这样测试可以注入 deterministic fake，而业务层不依赖具体 OS 实现。

### 18.11 UI

UI 负责：

```text
Qt Widget
Navigation
Rendering
Formatting
Localization presentation
Error/banner display
```

UI 不负责：

```text
Probability formula
SQL
Transaction
Historical readiness
```

### 18.12 UI 不直接 Import Core / Persistence

当前架构测试禁止 production UI 直接依赖：

```text
probability_calibration_tool.core
probability_calibration_tool.persistence
sqlite3
scipy
```

UI 必须通过 Application View / Session 获取数据。

### 18.13 UI 不访问 Workflow 私有字段

Presentation 使用：

```text
公开 Workflow API / properties
```

而不是：

```text
workflow._private_field
```

### 18.14 UI Formatting 不改变 Domain Value

例如：

```text
0.7123
```

可以显示：

```text
71.2%
```

但不能修改原 probability。

UTC datetime 可以显示本地时间，但源值保持 UTC。

### 18.15 UI 不成为最终 Input Validator

Widget 可以提供输入便利。

真正业务合法性仍由：

```text
Application / Core
```

判断。

避免 UI 与 Core 维护两套不同规则。

### 18.16 Application View 是信息边界

例如 Maintenance View 只提供：

```text
Regime
Reason
Included sample count
```

UI 不能为了“显示更多”绕过 View 直接查询 wins/losses。

这是 Anti-Anchoring 的一部分。

### 18.17 Workflow 与 Service 分工

Workflow：

```text
当前交互状态
transition
memory choices
revision lock
```

Service：

```text
数据库业务操作
事务
persistent facts
```

不能互相完全替代。

### 18.18 Service 仍需自我防御

即使正常 UI 一定经过 Workflow，Service 仍必须检查：

```text
pending
completed target
snapshot exists
active regime
```

等核心业务条件。

### 18.19 Database Constraint 不替代 Protocol

Schema 可以保证：

```text
FK
unique
status shape
```

但不能决定：

```text
History 什么时候显示
Recovery 后能不能 Modify
Correction 前是否需要 Safety Backup
```

这些属于 Application protocol。

### 18.20 DesktopHost

DesktopHost 负责：

```text
RuntimeResult
→ Normal Session / Safety Session
→ Window routing
```

以及 Restore 后 Session replacement。

### 18.21 Bootstrap

`bootstrap.py` 是 production composition root。

它负责组装：

```text
QApplication
Paths
Localization
StartupService
Runtime
DesktopHost
Qt event loop
```

不应该承载概率业务规则或事务。

### 18.22 Localization Fail-Open

Localization failure：

```text
→ English fallback
```

属于可降级 presentation capability。

Database invariant failure：

```text
→ fail closed
```

不能采用相同策略。

### 18.23 Tests 也是架构合同

测试不仅检查结果，也冻结：

```text
UI import boundaries
Atomicity
Recovery no-Core
Correction Snapshot copy
Restore Session revocation
Anti-Anchoring
```

因此 architecture tests 属于产品维护合同的一部分。

---

## 19. Compatibility、Change Rules 与技术合同总结

本文描述当前正式实现。

未来允许演进，但必须区分：

```text
内部实现重构
```

与：

```text
产品合同变化
```

### 19.1 Product Version

例如：

```text
1.1.0
```

描述整个应用 Release。

它不能替代内部数学或 Schema version。

### 19.2 当前独立版本

当前：

```text
Schema Version = 1

SUBJECTIVE_MODEL_VERSION = 1
HISTORY_MODEL_VERSION = 1
HISTORY_GATE_VERSION = 1
ODDS_ANALYSIS_VERSION = 1
STATS_VERSION = 1
```

这些数值当前碰巧都是 `1`，但语义彼此独立。

### 19.3 Schema Version

描述：

```text
SQLite persistent structure
```

如果增加不可兼容持久化字段或结构，需要判断：

```text
Schema Version bump
Migration
Backup compatibility
```

### 19.4 Subjective Model Version

如果改变：

```text
Clamp
Breakpoints
Factors
Logit interval algorithm
```

需要重新评估：

```text
SUBJECTIVE_MODEL_VERSION
```

### 19.5 Historical Model Version

如果改变：

```text
Jeffreys prior
Posterior estimator
Credible interval algorithm
```

需要重新评估：

```text
HISTORY_MODEL_VERSION
```

### 19.6 History Gate Version

如果只改变：

```text
minimum sample size
maximum interval width
```

则可能只需要：

```text
HISTORY_GATE_VERSION
```

变化。

### 19.7 Odds Analysis Version

如果改变：

```text
EV
S
break-even
epsilon
odds combination
historical threshold analysis
```

需要重新评估：

```text
ODDS_ANALYSIS_VERSION
```

### 19.8 Stats Version

描述：

```text
character_stats derived-cache contract
```

不等于 Schema Version 或 Historical Model Version。

### 19.9 Product Release 不要求所有内部版本增加

例如一个只增加 Localization 的产品版本：

```text
Product Version 增加
```

但：

```text
Schema
Models
Gate
Stats
```

完全可以保持原版本。

### 19.10 Snapshot 自描述数学版本

旧 Snapshot 必须保存其：

```text
Subjective model version
Historical model version
Gate version
Odds analysis version
```

所以未来模型升级后：

```text
不自动批量重算旧 Snapshot
```

### 19.11 Snapshot 不是 Cache

Model upgrade：

```text
影响未来新 prediction
```

不代表：

```text
覆盖历史 prediction
```

旧 Snapshot 是当时分析事实。

### 19.12 Migration 不等于历史重算

Schema migration 可以：

```text
转换结构
补充可确定 metadata
```

默认不能借 Migration：

```text
重新解释旧 prediction
重新计算旧 Historical values
重写 Exposure audit
```

### 19.13 Model Upgrade 与 Schema Upgrade 独立

可能：

```text
Model v2
Schema v1
```

也可能：

```text
Schema v2
所有 Model 仍 v1
```

不能人为让这些数字保持一致。

### 19.14 Regime 不是 Version Migration

Regime 表示：

```text
业务历史分段
```

不是模型升级。

模型升级也不自动意味着必须 Start New Regime。

### 19.15 Correction 不是 Migration

Correction：

```text
更正业务历史事实
```

Migration：

```text
转换数据库结构
```

不能互相替代。

### 19.16 Backward Compatibility 必须具体说明

所谓“兼容旧版本”至少要分别回答：

```text
旧 DB 能否打开
旧 Backup 能否 Restore
旧 Snapshot 是否保留
旧 Language Pack 是否可用
旧应用能否打开新 DB
```

不能只写：

```text
backward compatible
```

而不说明具体对象。

### 19.17 Newer Database

旧应用遇到：

```text
user_version > supported
```

必须拒绝。

不能：

```text
忽略未知字段
删除新数据
改回旧 user_version
```

### 19.18 Backup Compatibility

合法 Backup Restore 依赖：

```text
SQLite health
Schema compatibility
Migration path
Application invariants
Stats repairability
```

不依赖单纯文件扩展名。

### 19.19 Language Pack Compatibility

当前 zh_CN language pack 没有严格的 package-version metadata handshake。

因此推荐：

> 使用与应用 Release 对应的语言包。

但不能声称：

```text
版本不一致时应用会自动拒绝
```

除非未来正式实现。

### 19.20 User Data Path 也是行为合同

默认：

```text
%LOCALAPPDATA%\ProbabilityCalibrationTool\
```

如果未来改变数据根，需要考虑：

```text
live DB
Backup
Logs
Settings
Language Pack
```

的发现和迁移。

### 19.21 Portable Package ≠ Portable Data

当前：

```text
Portable
```

只表示：

```text
无需安装程序
解压运行
```

用户数据仍保存在 LocalAppData。

### 19.22 Internal Refactor

通常可以视为普通重构：

```text
函数拆分
变量改名
helper 移动
等价 SQL 改写
性能优化
UI layout 重构
```

前提：

```text
业务行为和持久化合同完全不变
```

### 19.23 Contract Change

以下通常属于产品合同变化：

```text
修改数学公式
修改 Historical Gate
修改 eligible-history 条件
允许多个 pending
Recovery 后开放 Modify
Completed Round 原地覆盖
取消 Correction Safety Backup
改变 Restore replacement semantics
Maintenance 提前显示 wins/losses
```

### 19.24 Contract Change Review

重大变化至少检查：

```text
Mathematical behavior
Schema
Migration
Snapshot
Workflow
Recovery
Anti-Anchoring
Correction
Backup compatibility
Restore
Error exposure
Tests
Docs
```

### 19.25 Golden Tests

数学 Golden Tests 是 reference behavior。

如果数学有意变化：

```text
先定义新公式和 version
再更新 Golden
```

不能：

```text
代码算出新值
→ 直接修改 expected
```

### 19.26 `SPEC_1.0.md`

`SPEC_1.0.md` 是：

> 1.0 历史设计与验收基线。

未来不应不断重写成当前最新规格。

### 19.27 本 Technical Reference

`TECHNICAL_REFERENCE.zh-CN.md` 回答：

> 当前正式实现实际上如何工作？

它是 current behavior reference。

### 19.28 User Guide

`USER_GUIDE.zh-CN.md` 回答：

> 普通用户如何正确操作？

不承担完整公式和 Schema 细节。

### 19.29 Localization Guide

`LOCALIZATION.zh-CN.md` 负责：

```text
English baseline
zh_CN external QM
QSettings preference
restart-only
translation maintenance
```

### 19.30 Development Guide

`DEVELOPMENT.zh-CN.md` 负责：

```text
开发环境
Tests
Ruff
Localization build
PyInstaller
Package QA
Release
```

### 19.31 Documentation Strategy

原则：

```text
少而权威
```

而不是每份文档重复同样内容。

### 19.32 文档冲突

如果：

```text
Docs
Source
Tests
Historical Spec
```

发生冲突：

```text
停止
确认预期合同
调查 drift 来源
再统一修正
```

不能机械认定任意一方必然正确。

### 19.33 Release 前 Cross-Document Check

至少检查：

```text
README
USER_GUIDE
TECHNICAL_REFERENCE
LOCALIZATION
DEVELOPMENT
Release Notes
```

关键术语和行为必须一致。

### 19.34 Frozen Model Constants

当前重要常量：

```text
FLOAT_EPSILON = 1e-12

JEFFREYS_ALPHA = 0.5
JEFFREYS_BETA = 0.5

HISTORY_CREDIBLE_LEVEL = 0.95
HISTORY_MIN_SAMPLE_SIZE = 20
HISTORY_MAX_INTERVAL_WIDTH = 0.25

SUBJECTIVE_MIN_PROBABILITY = 0.01
SUBJECTIVE_LOW_BREAKPOINT = 0.45
SUBJECTIVE_MID_HIGH_BREAKPOINT = 0.55
SUBJECTIVE_HIGH_BREAKPOINT = 0.85
SUBJECTIVE_VERY_HIGH_BREAKPOINT = 0.95
SUBJECTIVE_MAX_PROBABILITY = 0.99
```

以及 Subjective factors：

```text
1.5
2.0
1.4
1.2
```

这些是产品合同参数，不是可以随意调整的 magic numbers。

### 19.35 Final Data Authority

当前权威层次：

```text
characters
    Frozen reference identity

history_regimes
    Historical segmentation facts

rounds
    Primary business / audit facts

round_analysis_snapshots
    Historical prediction analysis facts

character_stats
    Rebuildable derived cache

meta
    Infrastructure metadata
```

### 19.36 Final Information Independence

系统同时保护：

```text
Mathematical independence
```

与：

```text
Information independence
```

因此不仅关心公式是否分开，也关心：

> 用户什么时候看到了 Historical information。

### 19.37 Final Audit Principle

系统倾向：

```text
保留历史事实
通过状态和链表达修改
```

所以：

```text
Correction
→ replacement chain

Exclude
→ Round 保留

Void
→ Round + Snapshot 保留

Regime
→ 分段，不删除

Snapshot
→ 保留当时分析
```

### 19.38 Final Recovery Principle

```text
Recovery
    same pending Round

Restore
    replace live DB from verified backup

Emergency Recovery
    unsafe Runtime disposition

Emergency Restore
    database-level replacement path
```

术语必须严格区分。

### 19.39 Final Safety Principle

可以安全降级的外围能力：

```text
Localization
Recent Backup
Daily Backup
```

可以：

```text
fallback / warning
```

但：

```text
Source Invariants
Snapshot Integrity
Correction Audit
Required Safety Backup
Restore Validation
```

失败时必须：

```text
fail closed
```

### 19.40 Final Change Principle

未来修改前首先判断：

```text
这是实现变化？
还是产品合同变化？
```

实现变化：

```text
保持测试通过
保持文档准确
```

合同变化：

```text
定义新行为
评估 Version / Migration
更新 Tests
更新 Docs
验证旧 Data / Backup Compatibility
```

---

## 20. 最终维护检查表

虽然本文技术主题到第 19 节结束，但维护核心行为时可以使用下面的最终检查表：

1. 是否改变用户可观察行为？
2. 是否改变 Subjective / Historical 数学合同？
3. 是否需要 Model / Gate / Odds / Stats Version 更新？
4. 是否改变 SQLite Schema？
5. 是否需要 Migration？
6. 是否影响旧 Backup Restore？
7. 是否改变 Snapshot 历史意义？
8. 是否改变 eligible history？
9. 是否改变 Anti-Anchoring？
10. 是否改变 Workflow？
11. 是否改变 Recovery？
12. 是否改变 Historical Correction？
13. 是否改变 transaction atomicity？
14. 是否改变 Startup / Restore safety？
15. 是否改变 error exposure？
16. 是否改变用户数据路径？
17. 是否需要更新 Golden / Integration / UI Tests？
18. 是否需要更新 README？
19. 是否需要更新 User Guide？
20. 是否需要更新 Localization / Development 文档？

---

## 结论

Probability Calibration Tool 当前最重要的技术合同可以压缩为：

```text
数学可复现

历史来源可追溯

Prediction 不被事后静默改写

Snapshot 保存当时分析事实

Correction 保留完整审计链

Recovery 继续原 pending Round

Restore 不伪装成 Recovery

Stats 只是可重建 Cache

高风险操作先验证

无法证明数据库安全时 fail closed

UI 不越过信息暴露边界

未来合同变化必须显式设计、测试、版本化并记录
```

只要这些合同继续成立，内部实现可以持续演进。

如果其中任何合同发生变化，就应把它当作正式产品行为变化，而不是静默的实现调整。
