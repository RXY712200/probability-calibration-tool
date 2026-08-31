# Phase 4 Completion Report

## Files created

新增 17 个源码文件、15 个测试/测试支持文件及 2 个交付报告：

```text
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\application\invariant_service.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\application\migration_service.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\application\reliability_views.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\application\restore_service.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\application\runtime_context.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\application\startup_service.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\application\stats_validation_service.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\infrastructure\__init__.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\infrastructure\backup.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\infrastructure\error_reporting.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\infrastructure\logging_setup.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\infrastructure\paths.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\infrastructure\restore_engine.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\infrastructure\runtime_lock.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\infrastructure\sqlite_health.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\persistence\migration_engine.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\persistence\reliability.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\application\reliability\__init__.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\application\reliability\conftest.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\application\reliability\test_application_invariants.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\application\reliability\test_restore.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\application\reliability\test_startup.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\application\reliability\test_stats_validation.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\infrastructure\__init__.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\infrastructure\conftest.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\infrastructure\helpers.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\infrastructure\test_backup.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\infrastructure\test_logging.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\infrastructure\test_paths.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\infrastructure\test_runtime_lock.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\infrastructure\test_sqlite_health.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\tests\integration\persistence\test_migrations_phase4.py
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\outputs\phase4_completion_report.md
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\outputs\phase4_validation_commands.md
```

## Files modified

```text
C:\Users\rxy71\Documents\Codex\2026-08-30\files-pasted-by-the-user-probability\src\probability_calibration_tool\persistence\repositories\regimes.py
```

仅新增只读 `HistoryRegimeRepository.list_all()`。未删除源文件或测试。对实施前的 73 个源码、测试和配置文件进行 SHA-256 对比，只有上述文件变化。

## Schema

Schema v1 unchanged

SPEC 与 Schema 文件 SHA-256 均与实施前一致：

```text
SPEC_1.0.md: AEE4EB200BEA8EC1A652A65A2076645613E6057C37D6280A9A0787CC5B040FC4
schema.py:   FB457C818780A94EF62AB53A3ED02FC0779FF1C4B0001734FBD67D56486F9315
```

## Persistence additions

- `regimes.py`：增加包含 inactive regime 的只读查询，供完整缓存校验使用。
- `reliability.py`：增加源记录清单和源数据外键检查，区分源事实损坏与可重建缓存。
- `migration_engine.py`：增加显式迁移注册表、顺序规划和单事务执行器；正式注册表为空，没有产品 v2。

未改变已有 Repository/UoW 的事务或写入语义。

## Infrastructure architecture

依赖方向保持 Application → Persistence / Infrastructure；Infrastructure 不导入 Application。

- `paths`：持久目录模型。
- `logging_setup`：bootstrap/full 两阶段日志及关闭。
- `error_reporting`：Error ID、异常日志与安全展示对象。
- `runtime_lock`：OS 级单实例锁。
- `sqlite_health`：既有库探测、完整检查、元数据和 sidecar 识别。
- `backup`：Online Backup、清单、三池保留、非致命协调器、Safety adapter。
- `restore_engine`：同目录 TEMP、原子替换、隔离和尽力清理。
- Application 新增启动、恢复、迁移、不变量、统计校验服务，以及 RuntimeContext 和非 UI 结果 DTO。

仅使用标准库及已有项目组件，未引入框架。

## Paths

生产路径来自 `AppPaths.from_local_appdata()`：

```text
%LOCALAPPDATA%\ProbabilityCalibrationTool\
  data\probability.db
  backups\recent\
  backups\daily\
  backups\safety\
  logs\app.log
  runtime\application.lock
```

测试使用 `AppPaths.from_root(tmp_path)`，生产路径构造测试也将 LOCALAPPDATA 替换为临时目录；没有访问真实用户应用数据。目录创建可重复执行。

## Logging and error reporting

加锁前只用 bootstrap 日志；取得锁后才打开共享 RotatingFileHandler。配置为 2 MiB、5 个历史文件，包含时间、级别、logger 和消息。异常生成唯一 Error ID，日志记录同一 ID 和完整 traceback；展示对象仅包含通用消息和 ID。真实日志轮转及 ID 对应测试通过。

## Runtime lock

Windows 使用 `msvcrt` 字节范围锁，不依赖锁文件是否存在。第二实例返回 ALREADY_RUNNING，不打开共享轮转日志。真实子进程测试证明 A 持锁、B 失败、强制终止 A 后 C 成功。RuntimeContext 在整个运行期持有锁和 logger，显式关闭时释放；恢复期间阻止新 managed UoW，有活动 UoW 时拒绝恢复。

## Fresh database safety

只有启动前不存在主库时才创建同一 data 目录的临时库，调用既有原子初始化，完成完整 integrity、不变量和缓存验证，关闭连接并 flush 后 `os.replace` 安装。四类注入故障均保持 live 不存在，并尽力清理临时文件。

既有零字节、空 SQLite、无预期 Schema 的 version 0 和损坏文件均进入安全路径，不重新初始化覆盖。

## Existing database probe

默认以 `mode=rw` 打开已存在文件，不隐式创建，不在探测时改变 journal_mode；允许 SQLite 自己恢复 hot rollback journal。真实崩溃子进程测试验证未提交变更回滚、原数据保留。先完整检查，再读版本；较新 Schema 在 seed、迁移、缓存修复和业务写入前被拒绝，数据字节保持不变。

## SQLite health

所有关键检查使用完整 `PRAGMA integrity_check`，仅接受逻辑结果恰好为单行 `ok`，没有替换为 quick_check。备份/恢复验证还检查版本与六张核心表，拒绝只是结构完整的无关空数据库。

## Backup

使用 `sqlite3.Connection.backup()`，在源读取事务中取得一致版本和内容。临时候选完成 Online Backup、关闭、完整检查、源版本匹配、核心表验证和 flush 后，原子晋升为正式备份，随后才清理旧备份。

文件名包含类别、UTC 时间和唯一 ID；Daily 额外记录注入的本地日历日期，Safety 记录明确原因。清单严格区分有效、损坏、临时、隔离和无关文件；后三类不参与轮转，损坏识别文件告警并保留。

- Recent：最新 5 个有效备份。
- Daily：最新 7 个不同本地日期；当天已有有效备份则复用；损坏的当天备份不占名额，保留并尝试新建。
- Safety：独立保留最新 10 个有效备份。

候选失败不删除旧备份；删除最旧备份失败立即停止后续删除，保留新备份并告警，允许超额保留。Recent/Daily 失败返回非致命警告，不撤销已提交主库事务。代表性数据独立重开核对通过。

## SafetyBackup adapter

`SQLiteSafetyBackupAdapter.create_verified_safety_backup(reason)` 结构兼容既有 SafetyBackupPort；成功必须创建已验证 Safety，失败向调用者传播。通过测试注入未修改的 Phase 3 历史纠错服务验证契约；没有在 Phase 3 中添加生产触发器或更改纠错逻辑。

## Migration

显式注册表规划有序迁移；live 迁移先检查旧库，成功创建 pre_migration Safety 后才 BEGIN IMMEDIATE。每步迁移体成功后才更新 user_version，提交前完整检查，提交后重开完整检查。

提交前失败回滚 Schema、数据和版本并保留 Safety；提交后检查失败明确报告已提交状态，启动进入 Emergency Recovery，保留 Safety，不宣称回滚、不自动恢复。测试注入 synthetic 1→2→3；正式产品仍只有 v1，较新版本拒绝迁移/降级。恢复候选迁移仅在保留原件的 TEMP 上执行。

## Normal Restore

主库必须可打开、完整且无 pending；候选先只读验证，并拒绝候选携带 sidecar。原件保持逐字节不变，复制到 live 同目录 TEMP 后迁移、检查源不变量、修复派生缓存、再次验证。

成功创建当前主库 pre_restore Safety 后，确保 managed UoW 全部退出、所有内部连接关闭，再原子替换。未能取得静止状态则中止；Windows 未关闭外部连接阻止替换的实测通过。任何未解释的 live journal/WAL/SHM 均阻止普通恢复，不盲删。

替换后重开检查 integrity、源不变量和缓存，按 0/1/>1 pending 路由 Draft/Recovery/Recovery Error。替换前失败保留原主库；替换后失败进入紧急状态、保留 Safety、不自动二次替换。

## Emergency Restore

仅适用于主库不可打开、完整性失败，或启动已明确将主库判为不安全的情况。普通恢复失败本身不会授予绕过 Safety 的资格。

替换候选同样先经 TEMP 验证；无效候选保持当前损坏文件不动。不要求损坏主库的已验证 pre_restore。尽力复制主库及 sidecar 为 `UNVERIFIED_CORRUPT` 诊断文件；复制失败可告警后继续，但旧 sidecar 必须成功移离关联名称，否则中止替换。隔离文件不计 Safety 配额。替换后验证成功才返回就绪。

## Application invariants

已实现的源事实检查：

- 恰好 34 个角色，冻结 identity 五元组完全匹配。
- 每个 active 角色恰好一个 active regime；regime 身份唯一、所属角色存在，active 与 ended_at 一致。
- round/snapshot 标识唯一且严格一对一，无孤立 snapshot。
- round 的角色与 regime 所属一致。
- pending/completed/voided 与 result、include、completed_at、voided_at 生命周期事实一致。
- history_exposed 与 exposure 时间一致；独立性受损须有 exposure；已引用且 VALID 的历史须有持久 exposure 权限记录。
- snapshot 最后历史来源存在、非自身、同角色/同 regime，calculated_at 不晚于当前记录。
- supersede 图无分支、无环；被替代记录已 voided，新记录不能 pending；复制字段和 snapshot 保留原预测。
- 源数据外键关系有效。

不自动修复上述源事实，不重算持久预测。multiple pending 单独返回 RECOVERY_ERROR，不猜选一条记录。

## Stats validation

对 active/inactive 所有 regime 检查缺失缓存、STATS_VERSION、included_games、wins、losses、last_included_round_id。根据 eligible source rounds，复用已有 stats rebuild。

整批修复在单个 UoW 事务中完成：缺失项插入与所有重建一起提交；任一重建失败全部回滚。成功后写当前 STATS_VERSION 并告警。可修复缓存漂移不归类为源事实损坏。

## Startup

实际顺序：创建目录 → bootstrap 日志 → 获取运行锁 → full 日志 → 判断 live 是否已存在 → 缺失则 TEMP 初始化/验证/安装，既有则受控探测 → 完整检查/读取版本 → 拒绝较新版本或执行支持迁移 → 源不变量检查 → multiple pending 优先返回 RECOVERY_ERROR；其余源错误返回安全错误 → 统计校验/单事务修复 → 再次完整检查 → 合格时 Daily → 返回就绪结果。

返回值覆盖 READY_DRAFT、READY_RECOVERY、RECOVERY_ERROR、EMERGENCY_RECOVERY、UNSUPPORTED_NEWER_SCHEMA、ALREADY_RUNNING、DATA_SAFETY_ERROR。RuntimeContext 保持锁。健康启动的 Daily 失败只增加警告，不阻止就绪。严格顺序和各主要状态均有测试。

## Backup eligibility

启动 Daily 仅在 integrity 通过、Schema 受支持、源不变量正常、缓存有效或修复成功且 pending≤1 后运行。损坏、不支持版本、源错误、缓存修复失败及 multiple pending 均跳过 Daily，避免拿异常状态轮转健康历史。底层备份组件提供能力；没有加入 Phase 6 业务触发器。

## Tests

`uv run pytest` → **747 passed in 38.59s**。

- passed: 747
- failed: 0
- skipped: 0
- xfailed: 0
- xpassed: 0

Phase 4 共 **88** 项：Infrastructure 22、Application reliability 59、Persistence migration 7。三组 collection 均成功：

```text
uv run pytest tests/integration/infrastructure --collect-only -q
uv run pytest tests/integration/application/reliability --collect-only -q
uv run pytest tests/integration/persistence/test_migrations_phase4.py --collect-only -q
```

Application reliability 分布为不变量 7、恢复 26、启动 19、统计 7。所有测试使用临时文件根。原有 659 项测试未删、未改、未跳过或 xfail。完整命令和输出见同目录 `phase4_validation_commands.md`。

## Fault injection

以下必需故障族全部通过，并断言数据库/文件幸存状态：

| 故障族 | 已验证结果 |
|---|---|
| Fresh 初始化/完整性/不变量/安装 | live 不存在，未接受半成品，TEMP 清理 |
| 备份候选创建 | 旧 5 份逐字节不变，无新正式备份 |
| 备份完整性/版本验证 | 候选不晋升，旧备份不轮转 |
| 备份轮转删除 | 首次删除失败即停止，保留新备份并超额保留 |
| Migration 提交前 | Schema/数据/版本回滚，Safety 保留 |
| Migration 提交后验证 | 已提交版本保留，安全路由，Safety 保留 |
| Normal Restore TEMP 复制/验证 | live 和原候选不变 |
| pre_restore Safety | 替换被阻止，live 不变 |
| live 原子替换 | 原主库保留且可用，Safety 保留 |
| 替换后验证 | 新主库保留，Safety 保留，紧急路由，无自动二次替换 |
| 统计批量重建 | 整批回滚，包括先前修复和缺失缓存插入 |
| 启动 Daily | 主库可用，仍 READY_DRAFT/READY_RECOVERY，返回警告 |

另外验证强杀锁持有者、真实 hot-journal 崩溃恢复、quarantine 复制失败及 sidecar 隔离失败。

## Phase 1 regression

`uv run pytest tests/unit/core -q` → **213 passed**。数学、Golden values 和既有测试未修改。

## Phase 2 regression

`uv run pytest tests/integration/persistence -q` → **300 passed**（原有 293 + Phase 4 migration 7）。

独立原有基线验证：

```text
uv run pytest tests/integration/persistence --ignore=tests/integration/persistence/test_migrations_phase4.py -q
```

结果：**293 passed**。这里的 --ignore 只隔离本阶段新增文件，不跳过任何已接受测试；完整测试命令已执行全部 747 项。

## Phase 3 regression

`uv run pytest tests/integration/application -q` → **212 passed**（原有 153 + Phase 4 reliability 59）。

独立原有基线验证：

```text
uv run pytest tests/integration/application --ignore=tests/integration/application/reliability -q
```

结果：**153 passed**。既有业务规则、状态机、audit-lock、Snapshot 行为及测试未修改。

## Ruff

`uv run ruff check .` → **All checks passed!**

`uv run ruff format --check .` → **109 files already formatted**。

两条命令退出码均为 0。

## SPEC deviations

none

## SPEC concerns

none

## Incomplete work

none

## Known risks

未来 Phase 6 必须保留 RuntimeContext 生命周期，并通过受管理 UoW 工厂接入业务资源；本阶段没有实施最终接线。当前证据覆盖 Windows 实际锁、SQLite 崩溃恢复和故障注入，不等同于物理断电、磁盘硬件失效或打包应用测试。外部工具若绕过应用锁修改文件，不受运行期资源管理约束。

## Phase 5 work

none

## Phase 6 work

none

Phase 4 complete. No Phase 5 or Phase 6 implementation was started.

