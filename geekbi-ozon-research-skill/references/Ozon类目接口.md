# Ozon 类目接口

## 入口

- 搜索：`GET /api/v1/ozon/category/ai-search`
- 子类目：`GET /api/v1/ozon/category/ai-list`
- 详情与父链：`GET /api/v1/ozon/category/ai-info`
- 脚本：`ozon_category_search.py`、`ozon_category_list.py`、`ozon_category_info.py`

未指定站点时默认俄罗斯站 `siteId=1`；其他市场先查询站点列表。类目来自 Ozon 服务已同步的 MySQL 类目树，不从名称猜测 ID。

搜索支持 `keyword`、`parentCatId`、`catLevel`，以及 `dsr`、`itemCount`、`mallCount` 区间；可按更新时间、累计/日周月销量销售额、商品数、店铺数、DSR、层级和均价排序。返回 `catId`、原文/中文名、父级、层级、叶子标记、指标与时间。

`ai-list` 的 `parentCatId=0` 从根层开始；`ai-info` 必须传 `catId`，返回 `category`、`path` 和 `history`。
