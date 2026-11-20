# 换词复跑 SOP

本 SOP 只覆盖关键词验证，不做商品编辑、广告投放、调价、上架或后台配置保存。

## 0. 启动、核对与目录

1. 任务 0 核对：确认 Ozon 报表入口为 `/app/analytics/what-to-sell/all-queries`，错误路径 `/app/analytics/search-queries` 不使用；确认 Wordstat 已登录。
2. 页面只显示相对窗口且绝对起止日期不可见时，停下让用户选择窗口口径并写入 `run_manifest.json` 的 `ozon_window_decision`；未获决定不进入判定。
3. 为本轮选择用户确认的项目目录，并建立新的 `ozon-keyword-pipeline/` 运行目录；已存在的历史运行目录不覆盖。
4. 创建 `PROGRESS.md`，用不超过 10 行记录目标、顺序、最大风险、运行日期、当前阶段与止损时间。
5. 创建 `BLOCKED.md`，无阻断时写“无”；同时创建 `data/run_manifest.json`，记录地区、设备、计划词数、页面预期窗口、运行 ID 和操作者，不得记录凭据。

## 1. SKU → 种子词

1. 从本店只读 SKU 标题与参数，或用户提供的原始导出中提取 5 个可核验 SKU。
2. 每 SKU 提炼一个俄语名词词典形核心词，写入 `data/seeds.csv`。
3. 标题或参数不足时写 `seed_pending`，进入 `BLOCKED.md`，不凭常识补词。

## 2. 种子词 → 冻结关键词批次

1. 每有效核心词保留核心词，并扩展 1–2 个长尾，目标总量为 10–12。
2. 属性词只能来自标题、参数、PDP 或 Ozon 站内返回的高频变体。
3. 记录构造方式、属性来源和 SKU 到 `data/keywords.csv`。
4. 检查数量、去重和证据来源后，将本批 `batch_status` 改为 `frozen`。之后不在本批替词。

## 3. 站内 Ozon 读取

1. 在正确入口的只读搜索查询报表逐词查询，记录页面实际列名、列顺序、筛选、窗口标签、抓取日、时间戳和截图编号；只有精确命中查询词的行可抄录，相似长尾词写 `no_exact_match`。
2. 原始行写入 `data/ozon_raw.csv`；字段对应写入 `data/ozon_column_mapping.csv`。
3. 单词在该来源连续失败三次，写入 `BLOCKED.md` 并继续下一个词。
4. 只允许搜索、切换只读指标、导出和截图。看到写入操作或人机验证时停止受影响步骤。

## 4. Wordstat 读取

1. 对每词先读取频次，再打开 Dynamics。分别记录频次查询式与趋势查询式，不假定两者同口径。
2. 频次取 Phrasing/Top queries 首行 `Number of queries`，不得取 `along with ... : N`；`No impression data` 写 `UNVERIFIED` 并截图，不写 0。
3. 记录频次、趋势方向、地区、设备、两个窗口、截图和时间戳到 `data/yandex_raw.csv`；批量提交后强制切回频次视图再解析，冲突时以截图为准。
4. 空结果、稳定性提示或瞬时错误最多重试三次；之后写入 `BLOCKED.md`。不要用 Wordstat 数字表示 Ozon 销量、订单或买家数。

## 5. 冻结阈值 → 交叉判定 → 反向验证

1. 趋势方向算法在读取前冻结（默认最近 12 个月前后各 6 个月均值比较，±10% 分界）；全部原始数据完成后，按 `decision-rules.md` 筛出有效行，分别计算中位数。
2. 将规则原文、SHA-256、趋势算法、有效行 ID、阈值和时间写入 manifest，再开始判定。
3. 写入 `data/keywords_result.csv`；每个黄灯必须带原因码；缺证据词为 `UNVERIFIED`。
4. 抽取一个完成词，重新读取 Ozon 和 Wordstat 两源并保存 `reverse-check-*` 截图。发现差异先查窗口、地区、设备、缓存和更新时间；不能解释则改为 `UNVERIFIED`。
5. 生成 `sop.md`，包含五步、冻结规则、本批真实示例一行、失败模式与对策、Wordstat API 升级路径、下轮复跑指引和未覆盖范围；机械规则反直觉结果写 `rule_limitation_note`，不改阈值。

## 结束与止损

- 到 3 小时或完整处理 12 个词时停止本轮。
- 保存已完成的原始数据和证据，不删除失败材料；清理 `_page.html` 与 `_` 开头临时文件。
- 在 `PROGRESS.md` 记录完成数、未核验数、阻断项和下一步，并核对其中证据数量与实际文件一致。
- 对外汇报完成情况时，明确区分 `verified`、`partial` 与 `UNVERIFIED`。
