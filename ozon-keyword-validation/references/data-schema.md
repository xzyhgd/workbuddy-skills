# 数据表、字段映射与证据关联

所有 CSV 以 UTF-8 保存，并用标准库 `csv` 写入以正确转义俄语、百分号与逗号。不要把注释行写入 CSV 表头；冻结规则、运行信息和字段映射分别写入独立文件。

## 运行目录

```text
ozon-keyword-pipeline/
├── PROGRESS.md
├── BLOCKED.md
├── sop.md
├── data/
│   ├── run_manifest.json
│   ├── seeds.csv
│   ├── keywords.csv
│   ├── ozon_raw.csv
│   ├── ozon_column_mapping.csv
│   ├── yandex_raw.csv
│   └── keywords_result.csv
└── evidence/
    ├── ozon-<序号><分片>.png
    ├── yandex-<序号><分片>.png
    └── reverse-check-<来源>-<序号>.png
```

## `seeds.csv`

| 列 | 含义 |
|---|---|
| `offer_id` | 本店 SKU 标识；来自只读 API、导出或截图 |
| `russian_title` | 原始俄语标题 |
| `core_lemma` | 名词词典形核心品类词 |
| `chinese_gloss` | 中文释义 |
| `seed_basis` | 标题、参数或 PDP 的证据来源 |
| `status` | `valid`、`seed_pending` 或 `UNVERIFIED` |
| `evidence_ids` | 关联的截图或原始导出编号 |

## `keywords.csv`

| 列 | 含义 |
|---|---|
| `keyword_id` | 稳定编号，如 `K01` |
| `core_lemma` | 对应核心词 |
| `keyword` | 待验证俄语词 |
| `construction_method` | `core`、`title_attribute`、`parameter_attribute` 或 `ozon_high_frequency_variant` |
| `attribute_source` | 使用的属性词及其来源说明 |
| `source_offer_id` | 关联 SKU |
| `batch_status` | `candidate` 或 `frozen` |

## `ozon_raw.csv`

本表必须保留页面实际列名、列顺序和原始文本，不预先假定列数。

固定元数据列：

```text
keyword_id,keyword,page_column_position,page_column_name,page_value_raw,
window_start,window_end,filter_context,capture_timestamp,coverage_status,
evidence_ids,read_status
```

- 每个页面数据列占一行；同一关键词因此可有多行。
- `page_column_position` 从 1 起记录页面的实际列位置。
- `read_status` 使用 `verified`、`UNVERIFIED`、`schema_changed`、`page_error`、`window_dates_unverified` 或 `no_exact_match`。
- 仅保存页面原始字符串，不在此表中做数值转换或中位数计算。

## `ozon_column_mapping.csv`

| 列 | 含义 |
|---|---|
| `mapping_version` | 本批字段映射版本 |
| `page_column_position` | Ozon 页面实际列位置 |
| `page_column_name` | 页面原始列名 |
| `standard_field` | 标准字段名；不确定时为 `UNMAPPED` |
| `field_role` | `keyword`、`metric`、`metadata` 或 `unknown` |
| `value_type` | `text`、`integer`、`decimal`、`percent` 或 `unknown` |
| `mapping_status` | `confirmed`、`UNMAPPED` 或 `schema_changed` |
| `evidence_ids` | 证明列名及含义的截图编号 |

只有 `mapping_status=confirmed` 的字段才能进入结果表。预期站内数值字段为 7 项，但必须以本批页面真实列为准：

```text
ozon_popularity_index,
ozon_add_to_cart,
ozon_add_to_cart_conversion_rate,
ozon_unique_buyers,
ozon_order_conversion_rate,
ozon_no_action_queries,
ozon_no_action_query_share
```

若页面无法证实这 7 项，保留原始列但不伪装为完整结果。

## `yandex_raw.csv`

| 列 | 含义 |
|---|---|
| `keyword_id` | 关联关键词 |
| `keyword` | 显示关键词 |
| `wordstat_frequency_query` | 频次页面实际输入的查询表达式 |
| `wordstat_dynamics_query` | Dynamics 页面实际输入的查询表达式 |
| `query_comparability_note` | 两个表达式是否同口径；不同则说明原因 |
| `frequency_value` | 频次页面原始数值 |
| `frequency_window_start` / `frequency_window_end` | 页面可见或导出可证实的频次窗口 |
| `trend_window_start` / `trend_window_end` | 趋势窗口 |
| `trend_direction` | `up`、`flat`、`down` 或 `UNVERIFIED` |
| `region` / `device` | 页面实际所选地区和设备 |
| `capture_timestamp` | 抓取时间 |
| `evidence_ids` | 频次和趋势截图编号 |
| `read_status` | `verified`、`UNVERIFIED`、`window_dates_unverified`、`page_error` 或 `no_impression_data` |

查询式说明：

- 双引号限制词数，不固定词序或词形。
- `[]` 固定词序。
- `!` 固定词形。
- `+` 强制计入停用词。
- Dynamics 不得假设支持频次页的所有运算符；记录页面实际接受的表达式。

## `keywords_result.csv`

每个关键词一行。只有双源完整、日期可核验、Ozon 字段映射确认并可定位证据的行，才可有绿黄红判定。

```text
keyword_id,keyword,
ozon_popularity_index,ozon_add_to_cart,ozon_add_to_cart_conversion_rate,
ozon_unique_buyers,ozon_order_conversion_rate,ozon_no_action_queries,
ozon_no_action_query_share,
wordstat_frequency_query,wordstat_dynamics_query,query_comparability_note,
wordstat_frequency,frequency_window_start,frequency_window_end,
trend_window_start,trend_window_end,trend_direction,region,device,
classification,yellow_reason_code,classification_note,
ozon_evidence_ids,yandex_evidence_ids,capture_timestamp,verification_status
```

- `classification` 只能为 `green`、`yellow`、`red` 或 `UNVERIFIED`。
- `yellow_reason_code` 仅在黄色时使用；其他状态写空。
- `verification_status` 只能为 `verified`、`partial` 或 `UNVERIFIED`。
- 所有 `*_evidence_ids` 使用分号分隔；一项读数若需要多图，必须列出全部文件。

## `run_manifest.json`

至少记录：运行 ID、运行时间、批次关键词 ID、地区、设备、`ozon_report_path`、`ozon_window_decision`、`trend_direction_method`、Ozon 与 Wordstat 窗口、字段映射版本、冻结规则原文与 SHA-256、参与中位数的有效行 ID、阈值、反向验证对象、阻断项、`evidence_file_count` 和最终汇总。不得保存 API Key、密码、Cookie、Token 或请求头。
