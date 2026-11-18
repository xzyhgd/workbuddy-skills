# 候选 SKU 可复现证据包规范

> 用途：让每个候选 SKU 的“可做 / 不可做 / 待补证”结论可以由另一位操作者复抓、复算和推翻。它是 G0–G5 的证据载体，不是附录。

## 1. 基本原则

1. **一候选一证据包**：候选必须是可采购的 SKU 族，不能用“某类配件”混装多规格事实。
2. **四要素缺一不可**：取数路径与时间戳、样本/覆盖边界、PDP 实体绑定、原始快照。缺失则标 `incomplete`，不能进入采购依据。
3. **三态字段**：所有事实字段都写 `observed`（实测）、`estimated`（推算）或 `unknown`（未知）；未知不补默认值、不加机会分。
4. **不把不可用当零**：遇到 Qrator、验证码、服务错误、筛选失效、`q` 不匹配、页面未渲染时，记录受限状态并停止；不得重试绕过。
5. **原始文件优先**：报告中的数值必须能回指原始 JSON、TSV、HTML、截图或供应商材料；截图仅作辅助，结构化源优先。

## 2. 推荐目录

```text
/candidates/<candidate-id>/
  00_manifest.json
  01_g0_compliance.md
  02_wordstat.json
  03_ozon_queries_7d.json
  04_ozon_bestsellers_28d.tsv
  05_pdp_samples.jsonl
  06_reviews_samples.jsonl
  07_supplier_spec.pdf|xlsx|png|json
  08_fulfillment.json
  09_unit_economics.json
  10_d0_baseline.json
  11_d7_followup.json
  12_d28_review.json
  13_decision.md
  hashes.sha256
```

- 文件名可按实际来源扩展，但不得覆盖原始快照。
- 无法取得的文件保留空位并在 `manifest.json` 中说明原因；不能靠复制其它 SKU 的文件补齐。
- `hashes.sha256` 对每个原始文件记录 SHA-256；人工截图也须纳入。

## 3. `00_manifest.json` 最低结构

```json
{
  "schema_version": "1.0",
  "candidate_id": "pfa-176x273-2pack",
  "candidate_name": "PFA/nFEP 176×273 mm，2 张装",
  "created_at": "2026-11-18T10:30:00+03:00",
  "timezone": "UTC+3",
  "decision_status": "P1",
  "gate_status": {
    "G0": "pass",
    "G1": "pass",
    "G2": "conditional",
    "G3": "conditional",
    "G4": "conditional",
    "G5": "not_started"
  },
  "coverage_status": "top50_truncated",
  "data_quality": "incomplete",
  "sources": [],
  "artifacts": [],
  "unknowns": [],
  "falsifiers": [],
  "replay_steps": []
}
```

### 必填字段说明

| 字段 | 要求 |
|---|---|
| `candidate_id` | 稳定、可读、唯一；规格或包装变化应新建 ID |
| `created_at` / `timezone` | 精确时间与时区；Ozon 默认记录 UTC+3 |
| `decision_status` | `P0` / `P1` / `P2` / `pending_evidence` |
| `gate_status` | G0–G5 取 `pass` / `conditional` / `blocked` / `unavailable` / `not_started` |
| `coverage_status` | 见第 4 节；不得默认为 `full_table_verified` |
| `data_quality` | `complete` / `incomplete` / `restricted` / `invalid` |
| `unknowns` | 未验证规格、成本、履约、授权等；逐项说明影响 |
| `falsifiers` | 能推翻当前结论的明确证据与复测触发条件 |
| `replay_steps` | 另一操作者重取相同数据所需 URL、筛选、词、周期与人工操作 |

## 4. 覆盖状态与零值状态

### 4.1 覆盖状态（`coverage_status`）

| 值 | 含义 | 可否作为采购依据 |
|---|---|---|
| `full_table_verified` | 表格已完整导出/逐页复核，边界明确 | 可，仍需 PDP 锚定 |
| `top50_truncated` | 仅 Top 50 或有限列表 | 仅样本结论，不可外推市场总量 |
| `query_partial` | 单个/少量词的局部召回 | 仅用于词面信号 |
| `filter_unreliable` | 已知 SKU 反测失败或筛选被污染 | 不可用 |
| `unavailable_not_zero` | 服务、人机、权限、加载等受限 | 不可用，绝非零 |
| `service_error` | 页面或 API 明确故障 | 不可用 |

### 4.2 零值状态（`zero_status`）

| 值 | 触发条件 | 可得结论 |
|---|---|---|
| `true_zero` | 对照词、输入值、周期、筛选、页面加载与已知 SKU 反测均正常，明确无记录 | 暂时反证，仍需记录复测条件 |
| `filter_false_zero` | 已知存在 SKU/货号也无法召回，或类目筛选遗留 | 筛选失效，不得判零 |
| `partial_zero` | 局部词、Top 50 或单页未出现 | 仅说明该局部未见，不能推为全市场无需求 |
| `unavailable_zero` | 验证码、服务错误、动态加载失败、`q` 不匹配、空壳 | 不可用，不得判零 |

## 5. 数据源记录（`sources[]`）

每一条来源至少写：

```json
{
  "source_id": "ozon-bestsellers-28d-pfa",
  "source_type": "ozon_bestsellers",
  "evidence_level": "A",
  "url_or_path": "https://seller.ozonru.cn/app/analytics/what-to-sell/ozon-bestsellers",
  "captured_at": "2026-11-18T10:30:00+03:00",
  "query": "pfa пленка",
  "filters": {"category": "cleared", "period": "28d"},
  "coverage_status": "top50_truncated",
  "city": "Moscow",
  "raw_artifact": "04_ozon_bestsellers_28d.tsv",
  "sha256": "<hash>",
  "notes": "类目筛选已清空；结果仅表示该查询召回样本"
}
```

### 证据等级

- **A**：本店 Seller API、登录态 Ozon 报表、前台 PDP、供应商原件、实际订单/结算单。
- **B**：官方公开资料、品牌公告、可复核的行业数据库。
- **C**：社区、评论讨论、论坛、媒体和第三方转述；只生成假设或解释痛点。
- **D**：分析推算；必须写公式、输入和敏感性，不能独立决定采购。

## 6. PDP 实体绑定（`05_pdp_samples.jsonl`）

每个后台商品或竞品样本必须至少含：

| 字段 | 说明 |
|---|---|
| `backend_sku` / `offer_id` | 后台识别符（若有） |
| `pdp_url` / `pdp_sku` | 前台可访问 URL 与 SKU |
| `title_raw` | 页面原始标题或 URL slug 还原标题 |
| `specs_observed` | 尺寸、厚度、张数、材料、型号、孔位等逐项标状态 |
| `price_paid` | 买家实付价；变体需标选中变体 |
| `fulfillment_observed` | 发货地、ETA、跨境/境内、可配送状态 |
| `reviews_at_capture` | 页面评论数，另标是否完成正文归属检查 |
| `binding_status` | `verified` / `partial` / `unverified` |

`binding_status != verified` 时，不得由货号或标题推导物理规格、兼容性、包装数或采购方案。

## 7. G0–G4 所需证据最小集

| 门禁 | 必须文件/字段 | 允许缺口 |
|---|---|---|
| G0 | 授权/许可、认证/管制/运输判断、品牌使用边界 | 无书面授权只能 P1/P2，不得 P0 |
| G1 | Wordstat、Ozon 查询、28 天复测或明确未取回、零值状态 | 低频品可暂缺一项，但必须标 `conditional` |
| G2 | 多词货架、PDP 样本、评价归属、单位价格归一化 | 仅 Top 50 时不可宣称市场总量 |
| G3 | 供应商规格、包装尺寸重量、ETA/发货地、兼容与防错 | 任一关键物理规格未知即不得采购 |
| G4 | 采购实价/区间、OGL 输入、三情景模型、全损预算 | 仅挂牌价可粗筛，不可最终批准 |

## 8. D0 / D7 / D28 与预测—实际校准

### D0：上架前基线

记录：商品页版本、类目/属性、价格、库存、ETA、关键词可见性、竞品、单位经济预测、首测数量与预算。

### D7：早期复测

记录：曝光、点击/转化、订单、广告花费、实际 ETA、异常、退款先兆、评价和竞品变化。D7 用于找原因，不可凭 7 天单次数据扩大采购。

### D28：周期裁决

记录：自然/付费订单、实际 CPA、签收与 ETA 偏差、退款/错配、评价归属、实际净利和库存周转。必须将预测与实际差异归类为：

```text
需求偏差 | 竞争偏差 | 履约偏差 | 成本偏差 | 合规偏差 | 数据质量偏差
```

## 9. `13_decision.md` 最低模板

```markdown
# <candidate-id> 决策

- 当前状态：P0 / P1 / P2
- G0–G5：逐门状态与一条关键证据
- 当前结论：
- 关键反证：
- 待补证项：
- 首测预算 / 数量 / 时间盒：
- D7 验收线：
- D28 扩大或停止条件：
- 翻案条件：
- 数据局限：覆盖状态、零值状态、受限记录
```

## 10. 完成检查清单

- ☐ 每一关键后台数值有路径、筛选、时间、覆盖范围与原始快照；
- ☐ 任何规格结论都有 PDP 或供应商实体材料，未凭货号脑补；
- ☐ 已记录筛选、词形、对照词与零值状态；
- ☐ 每份原始文件都写入哈希；
- ☐ 已区分事实、推算和未知；
- ☐ 已给出可推翻当前结论的证据；
- ☐ 已建立 D0；首测后补齐 D7 与 D28；
- ☐ 出现人机验证或服务错误时记录挂起，未绕过。
