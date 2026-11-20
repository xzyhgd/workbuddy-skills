# 冻结判定规则

在收集完成本批数据、写入任何 `green`、`yellow` 或 `red` 前，完整复制本文件的“本批规则原文”到 `data/run_manifest.json`，计算 SHA-256，写入参与样本和阈值。判定开始后不得修改规则或替换关键词；新增词必须进入下一批。

## 本批规则原文

1. 有效样本是同时满足以下条件的关键词行：
   - Ozon 的 `ozon_popularity_index` 与 `ozon_add_to_cart_conversion_rate` 均有确认字段映射、可解析数值、可见窗口日期与可定位证据；该行为查询词精确匹配，不是 `no_exact_match`；
   - Wordstat 的频次有可解析数值、可见窗口日期和可定位证据；
   - 趋势方向为 `up`、`flat` 或 `down`，并有趋势窗口和证据；
   - 该行不是 `schema_changed`、`window_dates_unverified`、`page_error` 或 `UNVERIFIED`。
2. 缺失值、未核验值、文本无法解析的值和窗口未核验值，不参与中位数、阈值或绿黄红判断。
3. 每个指标在有效样本中独立计算中位数：
   - 奇数个样本：排序后的中间值；
   - 偶数个样本：排序后中间两个值的算术平均；
   - 不同指标可因缺失产生不同有效样本集合，必须在 manifest 中分别记录行 ID。
4. 站内侧强：`ozon_popularity_index` 和 `ozon_add_to_cart_conversion_rate` 均大于或等于各自中位数。
5. Wordstat 侧强：`wordstat_frequency` 大于或等于本批有效样本中位数，且 `trend_direction` 不为 `down`。
6. 绿：站内侧强且 Wordstat 侧强。
7. 黄：只有一侧强，或两侧证据完整但存在以下可解释冲突之一：
   - `SEASONALITY`：趋势、窗口或同季历史表明季节性影响；
   - `PLATFORM_GAP`：站内与全网受众、履约或平台渗透差异有页面证据；
   - `DATA_PARTIAL`：非关键辅助字段缺失，但绿红关键字段完整；
   - `CONFLICTING_SIGNAL`：两源完整、指标方向冲突且暂无法归入其他代码。
8. 红：站内侧弱且 Wordstat 侧弱，两侧关键证据均完整。
9. `UNVERIFIED`：任一关键来源、窗口、字段映射或证据定位不满足规则 1；不得强行降级为黄或红。
10. Ozon 热门度指数与 Wordstat 绝对频次不得直接相加、相减、取比例或跨源比较绝对大小；它们只分别与自身批次中位数比较。
11. Wordstat 频次查询和趋势查询可使用不同表达式，但必须记录实际表达式与 `query_comparability_note`。查询口径不同不影响“趋势非降”的最低判断，但必须在结果中明示，不得称为严格同词精确趋势。
12. 反向验证：从本批完成行中抽取 1 个词，在相同地区、设备、筛选和窗口设置下重新读取 Ozon 与 Wordstat。若任一数字或趋势结论不一致，先比较日期窗口、地区、设备、页面更新时间、缓存和排序。无法解释时，该词判 `UNVERIFIED`，保留两次证据并不得选取更优数字。
13. 绝对起止日期不可见时，只有 manifest 已记录用户选择 `accept_relative_window_with_capture_date` 且窗口字段标为 `7d_relative/<capture_date>`，该行才可视为满足“可见窗口日期”；未记录用户决定时按规则 9 判 `UNVERIFIED`，不得编造具体起止日。
14. 趋势方向算法在读取前冻结：默认取 Dynamics 最近 12 个月，前 6 个月均值与后 6 个月均值比较，`≥+10%` 为 `up`、`≤-10%` 为 `down`、其余 `flat`。采用其他算法必须先写入 manifest 并经用户确认，判定期间不得更换。

## 判定输出要求

- `classification=yellow` 必须填写一个 `yellow_reason_code` 和一句原因说明。
- `classification=green`、`red` 或 `UNVERIFIED` 的 `yellow_reason_code` 必须为空。
- 所有判定行必须保存 Ozon 与 Wordstat 的全部截图编号。
- `UNVERIFIED` 不计入绿黄红数量汇总；单独汇报数量与缺口。
- 机械规则产生反直觉结果时，在 `sop.md` 写明 `rule_limitation_note` 供人工判断；不得因此改阈值或分类。
- 交付前核对 `PROGRESS.md`、`run_manifest.json` 与实际证据文件数量一致。
- 判定只说明本批词的相对验证强弱，不构成采购、投放、合规或销量承诺。
