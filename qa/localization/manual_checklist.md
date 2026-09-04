# Localization Step 7 Localization-Delta Manual Checklist

Status: `MANUAL ACCEPTANCE PAUSED — PENDING EXTERNAL REVIEW`

This supersedes the former broad 212-row Step 7 manual contract. It certifies the localization delta only; frozen 1.0 business transactions and their persistence/atomicity semantics remain covered by frozen acceptance and Step 6 automation. Every formal result begins as `NOT_RUN`; preparation never records PASS, FAIL, or N/A.

Formal display baseline: **2560×1600 at 150% only**. `default`, `minimum practical`, and `maximized` mean normal launch, the smallest meaningful resizable window, and Windows Maximize. A future N/A is permitted only for `N/A_ALLOWED` with an exact reason, safe-reproduction rationale, and Step 6 evidence.

## Gate A — Environment & Localization Identity

| ID | Area | Language | Scaling | State / human-observable localization risk | Requirement | Result | Evidence | Notes |
|---|---|---|---|---|---|---|---|---|
| A-ENV-01 | Windows environment | N/A | Actual | Record Windows 11 x64 edition/build | MANDATORY | NOT_RUN | — | Environment identity. |
| A-ENV-02 | Native display | N/A | Actual | Record native 2560×1600 | MANDATORY | NOT_RUN | — | Display identity. |
| A-ENV-03 | Formal baseline | en + zh_CN | 150% | 2560×1600 @ 150%; representative default/minimum practical/maximized only | MANDATORY | NOT_RUN | — | No alternate formal scaling route. |
| A-ENV-04 | Runtime identity | en | 150% | Built-in English; translator absent | MANDATORY | NOT_RUN | — | Human records effective language. |
| A-ENV-05 | Runtime identity | zh_CN | 150% | Preferred/Effective zh_CN; official external pack loaded; no fallback | MANDATORY | NOT_RUN | — | Human records identity. |
| A-ENV-06 | Pack identity | zh_CN | N/A | Official TS/QM provenance, hashes, PySide6 and Qt versions | MANDATORY | NOT_RUN | — | Preparation facts may be copied into evidence. |
| A-ENV-07 | Isolation | All | N/A | Scenario root is isolated from live DB/settings | MANDATORY | NOT_RUN | — | Verify before launch. |

## Gate B — English Built-in Regression

| ID | Area | Language | Scaling | State / human-observable localization risk | Requirement | Result | Evidence | Notes |
|---|---|---|---|---|---|---|---|---|
| B-EN-01 | AppShell | en | 150% | Healthy READY_DRAFT startup; no localization notice/debug marker | MANDATORY | NOT_RUN | — | Presentation regression only. |
| B-EN-02 | Round | en | 150% | DRAFT controls, representative long name and Jacob & Esau; default + minimum practical | MANDATORY | NOT_RUN | — | No full character-matrix recertification. |
| B-EN-03 | Analysis | en | 150% | Locked Subjective and valid Historical Analysis presentation | MANDATORY | NOT_RUN | — | Isaac 50W/50L fixture. |
| B-EN-04 | Analysis | en | 150% | History not requested, Cain no eligible history, Magdalene insufficient history | MANDATORY | NOT_RUN | — | Presentation state distinctions. |
| B-EN-05 | Analysis | en | 150% | Dynamic text/timestamp/warning; default + minimum practical + maximized | MANDATORY | NOT_RUN | — | No raw placeholders. |
| B-EN-06 | Modify / Recalculate | en | 150% | PENDING_EDIT and recalculated locked presentation distinguishable | MANDATORY | NOT_RUN | — | No recalculation semantics recertification. |
| B-EN-07 | Post-run | en | 150% | One confirmation presentation and clean New Round presentation | MANDATORY | NOT_RUN | — | No persistence proof required. |
| B-EN-08 | Maintenance | en | 150% | Maintenance and pre-calculate anti-anchoring; default + minimum practical | MANDATORY | NOT_RUN | — | Presentation only. |
| B-EN-09 | Regime | en | 150% | Start New Regime editor presentation | MANDATORY | NOT_RUN | — | No regime mutation required. |
| B-EN-10 | Correction | en | 150% | Candidate/editor presentation at minimum practical; Cancel/Back only | MANDATORY | NOT_RUN | — | Do not execute correction. |
| B-EN-11 | Restore | en | 150% | Normal Restore candidate/confirmation presentation at minimum practical; Cancel/Back only | MANDATORY | NOT_RUN | — | Do not execute restore. |
| B-EN-12 | Recovery / Errors | en | 150% | Representative Recovery presentation and ordinary expected validation error | MANDATORY | NOT_RUN | — | No recovery business-state proof required. |
| B-EN-13 | Keyboard | en | 150% | Tab, Enter-or-Space, and Esc spot-check on ordinary UI | MANDATORY | NOT_RUN | — | No destructive activation. |
| B-EN-14 | Geometry | en | 150% | One representative administrative page at minimum practical | MANDATORY | NOT_RUN | — | Correction or Restore. |
| B-EN-15 | English identity | en | 150% | Canonical built-in English remains readable and untranslated by external pack | MANDATORY | NOT_RUN | — | Presentation regression only. |

## Gate C — Official zh_CN Presentation

| ID | Area | Language | Scaling | State / human-observable localization risk | Requirement | Result | Evidence | Notes |
|---|---|---|---|---|---|---|---|---|
| C-ZH-01 | Identity / glyph | zh_CN | 150% | Effective zh_CN, official external QM, no fallback, no mojibake/tofu/replacement; mixed Chinese/Latin/numeric rendering | MANDATORY | NOT_RUN | — | One real production observation. |
| C-ZH-02 | Characters | zh_CN | 150% | All 34 mappings: 以撒、抹大拉、该隐、犹大、???、夏娃、参孙、阿撒泻勒、拉撒路、伊甸、游魂、莉莉丝、店主、亚玻伦、遗骸、伯大尼、雅各和以扫、堕化以撒、堕化抹大拉、堕化该隐、堕化犹大、堕化???、堕化夏娃、堕化参孙、堕化阿撒泻勒、堕化拉撒路、堕化伊甸、堕化游魂、堕化莉莉丝、堕化店主、堕化亚玻伦、堕化遗骸、堕化伯大尼、堕化雅各 | MANDATORY | NOT_RUN | — | Includes long Tainted names and ampersand-sensitive Jacob & Esau source identity. |
| C-ZH-03 | Round | zh_CN | 150% | DRAFT controls and Chinese wrapping; default + minimum practical | MANDATORY | NOT_RUN | — | Representative geometry. |
| C-ZH-04 | Analysis | zh_CN | 150% | Valid history, dynamic placeholders, timestamps, warning, N/A, and no raw %1/%2/%3 leakage | MANDATORY | NOT_RUN | — | Isaac 50W/50L fixture. |
| C-ZH-05 | Analysis | zh_CN | 150% | History not requested, Cain no eligible history, Magdalene insufficient history | MANDATORY | NOT_RUN | — | State-specific Chinese presentation. |
| C-ZH-06 | Analysis | zh_CN | 150% | Default + minimum practical + maximized wrapping/layout | MANDATORY | NOT_RUN | — | Representative geometry. |
| C-ZH-07 | Maintenance | zh_CN | 150% | Maintenance/table and historical-stage wording; default + minimum practical | MANDATORY | NOT_RUN | — | Representative geometry. |
| C-ZH-08 | Correction | zh_CN | 150% | Candidate/editor presentation and 更正原因（必填）; default + minimum practical | MANDATORY | NOT_RUN | — | Unicode entry only; do not commit correction. |
| C-ZH-09 | Restore | zh_CN | 150% | Normal Restore candidate/confirmation presentation; default + minimum practical | MANDATORY | NOT_RUN | — | Do not execute restore. |
| C-ZH-10 | Recovery / StartupSafety | zh_CN | 150% | Representative Recovery or StartupSafety page at minimum practical | MANDATORY | NOT_RUN | — | Presentation only. |
| C-ZH-11 | Terminology | zh_CN | 150% | 单局、新一局、维护、历史阶段、当前历史阶段、开始新的历史阶段、历史记录更正、备份恢复、常规备份恢复、紧急备份恢复、未完成单局恢复、紧急数据恢复、主观概率、历史概率、参考历史数据、不参考历史数据、计入历史、不计入历史、胜、负、更正原因（必填） | MANDATORY | NOT_RUN | — | Regime must never be 模式; Restore/Recovery/Emergency Recovery remain distinct. |
| C-ZH-12 | English leakage | zh_CN | 150% | Classify every observed English fragment as INTENTIONAL_PRODUCT_NAME, INTENTIONAL_TECHNICAL_TOKEN, QT_OWNED, or DEFECT_APP_OWNED | MANDATORY | NOT_RUN | — | ASCII is not automatically a defect. |
| C-ZH-13 | Unicode / keyboard | zh_CN | 150% | Enter `人工验收：中文原因 01`; ordinary Tab, Enter-or-Space, and Esc behavior | MANDATORY | NOT_RUN | — | No destructive activation. |
| C-ZH-14 | Context coverage | zh_CN | 150% | Real production observations collectively cover all 12 frozen contexts | MANDATORY | NOT_RUN | — | Traceability appendix names each context. |
| C-ZH-15 | Presentation quality | zh_CN | 150% | Long labels, wrapping, placeholders and localized safety/priority presentation remain legible | MANDATORY | NOT_RUN | — | Human visual judgment. |

## Gate D — Language Lifecycle / Fallback

| ID | Area | Language | Scaling | State / human-observable localization risk | Requirement | Result | Evidence | Notes |
|---|---|---|---|---|---|---|---|---|
| D-LC-01 | Healthy dialog | en | 150% | Preferred=en, Current=en, English and 简体中文 availability, Built-in/External provenance | MANDATORY | NOT_RUN | — | Truthfulness. |
| D-LC-02 | Restart lifecycle | en→zh_CN | 150% | Save zh_CN; no live mass retranslation; genuine exit/relaunch makes zh_CN effective | MANDATORY | NOT_RUN | — | Record Launch 1 → action → process exit → Launch 2. |
| D-LC-03 | Restart lifecycle | zh_CN→en | 150% | Save English; no live mass retranslation; genuine exit/relaunch makes English effective | MANDATORY | NOT_RUN | — | Record Launch 1 → action → process exit → Launch 2. |
| D-LC-04 | No-op / cancel | Both | 150% | Same-language no-op; Cancel, Esc, and X cause no save | MANDATORY | NOT_RUN | — | One route may evidence all four. |
| D-LC-05 | Default persistence | en | 150% | Explicit default-English save persists correctly | MANDATORY | NOT_RUN | — | Lifecycle presentation. |
| D-LC-06 | Missing pack | en fallback | 150% | Preferred zh_CN remains; Effective English; notice/dialog truthfulness; no partial localization | MANDATORY | NOT_RUN | — | Fallback presentation. |
| D-LC-07 | Pack restoration | zh_CN | 150% | Restore valid pack without changing Preferred; restart resumes zh_CN | MANDATORY | NOT_RUN | — | Lifecycle presentation. |
| D-LC-08 | Corrupt pack | en fallback | 150% | Full English fallback; Preferred unchanged; no partial localization | MANDATORY | NOT_RUN | — | Fallback presentation. |
| D-LC-09 | Discovery | en fallback | 150% | Wrong filename and wrong location are unavailable | MANDATORY | NOT_RUN | — | Pack discovery truthfulness. |
| D-LC-10 | Invalid preference | en | 150% | Invalid saved preference falls back to English without auto rewrite | MANDATORY | NOT_RUN | — | Read-state presentation. |
| D-LC-11 | Settings read failure | en | 150% | Deterministic human route if safely available; otherwise exact Step 6 evidence | N/A_ALLOWED | NOT_RUN | — | Never automatically select N/A. |
| D-LC-12 | Confirm-time disappearance | en | 150% | zh pack disappears before Confirm: no save, prior Preferred/Effective retained, no false success | MANDATORY | NOT_RUN | — | Isolated in-session mutation. |
| D-LC-13 | Save failure | en | 150% | Generic QSettings save failure preserves existing preference | MANDATORY | NOT_RUN | — | Isolated fault route. |
| D-LC-14 | Qt translator degraded | zh_CN | 150% | Reproduce if safely deterministic; otherwise exact Step 6 evidence; app stays zh_CN while Qt-owned text may remain English | N/A_ALLOWED | NOT_RUN | — | Never automatically select N/A. |
| D-LC-15 | Qt translator healthy | zh_CN | 150% | Healthy Qt translator state recorded | MANDATORY | NOT_RUN | — | Official QM identity. |
| D-LC-16 | Startup notice | Both | 150% | Localization startup notice appears once per process; dismissal leaves normal app usable | MANDATORY | NOT_RUN | — | Language dialog stays truthful after fallback/error states. |

## Gate E — Localization-Sensitive Safety / Priority Presentation

| ID | Area | Language | Scaling | State / human-observable localization risk | Requirement | Result | Evidence | Notes |
|---|---|---|---|---|---|---|---|---|
| E-SP-01 | Recovery priority | en fallback | 150% | Recovery is primary over localization notice; terminology remains distinct from Restore | MANDATORY | NOT_RUN | — | Presentation only. |
| E-SP-02 | Data Safety priority | Both | 150% | Data Safety is primary over localization notice and ordinary warning | MANDATORY | NOT_RUN | — | Presentation only. |
| E-SP-03 | Already running | en fallback | 150% | ALREADY_RUNNING suppresses localization fallback notice | MANDATORY | NOT_RUN | — | Two real isolated processes. |
| E-SP-04 | Emergency fallback | en fallback | 150% | Preferred zh_CN + missing pack: English effective fallback and Emergency remains primary | MANDATORY | NOT_RUN | — | Presentation only. |
| E-SP-05 | Expected error | Both | 150% | One bilingual expected business-rule error is readable | MANDATORY | NOT_RUN | — | No business-rule recertification. |
| E-SP-06 | Unexpected error | Both | 150% | Generic safe public text, readable Error ID; no traceback, SQL, private path, internal repr, or private diagnostics | MANDATORY | NOT_RUN | — | Presentation safety. |
| E-SP-07 | Error priority | Both | 150% | Error presentation outranks ordinary warning | MANDATORY | NOT_RUN | — | Presentation priority. |
| E-SP-08 | Backup warning | zh_CN | 150% | Representative deterministic backup/warning translation presentation | MANDATORY | NOT_RUN | — | No destructive replacement required. |

## Gate F — Evidence / Defect Closure

| ID | Area | Language | Scaling | State / human-observable localization risk | Requirement | Result | Evidence | Notes |
|---|---|---|---|---|---|---|---|---|
| F-EV-01 | Evidence integrity | All | 150% | Raw Windows screenshots; no AI edits or defect-concealing crops; one screenshot may support multiple rows | MANDATORY | NOT_RUN | — | Human result authority. |
| F-EV-02 | Defect closure | All | 150% | PASS/FAIL/N/A+reason, severity, owner, affected Step 6 rerun after production/localization fix; no unresolved BLOCKER/HIGH | MANDATORY | NOT_RUN | — | No fake screenshots. |

## Preparation totals

| Gate | Rows | Mandatory | N/A_ALLOWED | NOT_RUN |
|---|---:|---:|---:|---:|
| A — Environment & Localization Identity | 7 | 7 | 0 | 7 |
| B — English Built-in Regression | 15 | 15 | 0 | 15 |
| C — Official zh_CN Presentation | 15 | 15 | 0 | 15 |
| D — Language Lifecycle / Fallback | 16 | 14 | 2 | 16 |
| E — Localization-Sensitive Safety / Priority Presentation | 8 | 8 | 0 | 8 |
| F — Evidence / Defect Closure | 2 | 2 | 0 | 2 |
| Total | 63 | 61 | 2 | 63 |
