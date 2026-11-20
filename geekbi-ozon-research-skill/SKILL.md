---
name: geekbi-ozon-research-skill
description: 通过极鲸云查询和组合分析 Ozon 当前支持站点的真实商品、店铺、类目、关键词和评论数据，完成跨境选品、市场调研、竞品分析、SKU/SPU、价格带、需求供给、履约和用户反馈研究。用户提出 Ozon 综合选品、俄罗斯及其他可用市场机会、竞品店铺、类目赛道、搜索词或口碑研究，且需要多类数据形成经营判断时使用。只依据极鲸云真实返回数据，不提供 Ozon 平台内图搜、利润承诺或卖家后台操作。

version: "1.0.0"
display_name: "极鲸云Ozon数据分析与市场调研"
display_name_en: "GeekBI Ozon Data Analysis and Market Research"
description_zh: "使用极鲸云真实Ozon数据开展数据分析与市场调研，仅依据接口实际返回结果形成分析结论。"
description_en: "Combine supported data capabilities for product and market research. Powered by real Ozon data from GeekBI. Base findings only on returned data."
---

# 极鲸云 Ozon 综合研究

## 能力路由

- 商品：读取 [商品接口](references/Ozon商品接口.md)，运行 `ozon_goods_search.py` / `ozon_goods_info.py`。
- 店铺：读取 [店铺接口](references/Ozon店铺接口.md)，运行 `ozon_mall_search.py` / `ozon_mall_info.py`。
- 类目：读取 [类目接口](references/Ozon类目接口.md)，运行 `ozon_category_search.py` / `ozon_category_list.py` / `ozon_category_info.py`。
- 关键词：读取 [关键词接口](references/Ozon关键词接口.md)，运行 `ozon_keyword_search.py` / `ozon_keyword_info.py`。
- 评论：读取 [评论接口](references/Ozon评论接口.md)，运行 `ozon_review_search.py`。
- 未指定站点时默认俄罗斯站 `siteId=1`；指定其他市场时先运行 `ozon_site_list.py` 并只采用唯一匹配。

## 工作流

1. 明确研究对象、SKU/SPU 口径、指标窗口、筛选和输出目标。
2. 只调用回答问题所需的最少接口；类目、商品、店铺 ID 不猜测。
3. 先宽筛，再对少量候选查详情、历史、评论和关联实体。
4. 区分公开采集、Seller Analytics 窗口、估算字段和缺失值。
5. 输出站点、对应币种、条件、排序、页码、总命中、实际样本、更新时间和来源。
6. 经营判断读取 [运营与政策口径](references/Ozon运营与政策口径.md)；暂停按 [查询暂停与恢复流程](references/查询暂停与恢复流程.md)。

## 边界

- 最多访问排序后的前 200 条；未完成分页明确为样本。
- 热销、增长、高搜索量和高评分都不等于低竞争或可盈利。
- Ozon 图片上传后去 1688 等平台找货，不是 Ozon 平台内图搜，本 Skill 不路由该能力。
- 缺失值显示 `-`；数值 0 结合字段来源判断，不自动当作真实为零。
- 只使用响应提供的 `goodsUrl` / `mallUrl`，不拼接链接。

默认输出：结论、数据口径、关键证据、机会、风险、置信度和验证动作。
