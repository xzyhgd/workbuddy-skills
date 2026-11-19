# 候选证据包规范

每个候选建立一个独立证据包。目录名使用稳定候选 ID，不用临时页面标题替代。

```text
candidates/<candidate-id>/
├── 00_manifest.json
├── 01_demand/
├── 02_competition/
├── 03_product-delivery/
├── 04_economics/
└── 05_validation/
```

## `00_manifest.json` 最小字段

```json
{
  "schema_version": "1.0",
  "candidate_id": "example-compatible-nozzle",
  "decision_status": "P1",
  "supporting_labels": ["recheck_required"],
  "confidence": "low",
  "created_at": "2026-11-19T00:00:00Z",
  "time_window": "2026-11-01 to 2026-11-19",
  "coverage_status": "query_partial",
  "zero_status": "partial_zero",
  "data_quality": "incomplete",
  "sources": [],
  "artifacts": [],
  "unknowns": [],
  "falsifiers": [],
  "replay_steps": []
}
```

## 字段约束

- `decision_status` 只能为 `P0`、`P1`、`P2`。
- `supporting_labels` 只能使用 `watchlist`、`variant_only`、`recheck_required`；它们不改变最终决策状态。
- `coverage_status` 只能为 `full_table_verified`、`top50_truncated`、`query_partial`、`filter_unreliable`、`unavailable_not_zero`、`service_error`。
- `zero_status` 只能为 `true_zero`、`filter_false_zero`、`partial_zero`、`unavailable_zero`。
- 每个事实字段另记 `observed`、`estimated` 或 `unknown`，未知字段不得作为门禁通过依据。

## 来源记录

每个 `sources` 条目至少包含：来源类型、URL 或页面路径、采集时间、查询词、统计窗口、筛选条件、核验城市、样本量、覆盖状态和原始快照相对路径。

后台货号要进入决策证据时，必须在 `artifacts` 中关联前台 PDP：真实 URL、标题、规格、包装数、发货地、ETA 与快照。不能用后台货号名称推断物理规格。

## 文件要求

- 原始截图、导出或文本快照不得被后处理覆盖。
- 经济模型保存输入、参数版本、三种情景和结果。
- D0、D7、D28 分开保存，且使用相同的口径字段。
- 保存 SHA-256 或等效哈希时，记录哈希对象和计算时间。

## 无法落盘时

如果环境无写入权限，交付中必须列出应保存的目录和文件名，并将证据状态标为“部分验证”；不得写成“证据包已完成”。
