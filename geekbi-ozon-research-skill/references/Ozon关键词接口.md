# Ozon 关键词接口

## 入口

- 搜索：`GET /api/v1/ozon/keyword/ai-search`
- 详情：`GET /api/v1/ozon/keyword/ai-info`
- 脚本：`ozon_keyword_search.py`、`ozon_keyword_info.py`

未指定站点时默认俄罗斯站 `siteId=1`；其他市场先查询站点列表。搜索支持 `keyword`、`catId`、`dsr`、`itemCount`、`monthSold`、`monthSales` 区间。可按更新时间、搜索量、累计/日周月销量销售额、商品数、店铺数、DSR 和均价排序。

返回可包含原始词、中文词、搜索量、销量销售额、商品/店铺供给、均价、首个上架时间、类目、历史、观察时间和数据来源。详情必须提供 `keywordId` 或原始 `keyword`，优先使用 ID。
