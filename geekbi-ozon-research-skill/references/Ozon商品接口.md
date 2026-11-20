# Ozon 商品接口

## 入口

- 搜索：`GET /api/v1/ozon/goods/ai-search`
- 详情：`GET /api/v1/ozon/goods/ai-info`
- 脚本：`ozon_goods_search.py`、`ozon_goods_info.py`

未指定站点时默认 `siteId=1`（俄罗斯站，RUB）；其他市场先运行站点脚本取得真实 `siteId`。搜索每页 1–100 条，Skill 最多访问排序后的前 200 条。

## 搜索参数

基础条件包括 `keyword`、`catId`、`goodsId`、`mallId`、`skuId`、`spuId`、`offerId`、`brandId`、`brand`、`salesLabel`、`sellerType`、`fulfillmentType`、`dataSource`、`entityMode=SKU|SPU` 和 `analyticsWindowDays=7|28`。

区间条件统一使用 `字段Min` / `字段Max`，覆盖销量和销售额、价格、评分和评论、跟卖数、库存、浏览和转化、广告、促销、退货、缺货、包装、配送及日期。完整白名单以脚本常量和 `--help` 为准。

榜单预设：

- `new`：新品，默认按上架时间。
- `hot`：有月销量的热销商品，默认按月销量。
- `five-star`：五星且有近期销量的商品。
- `rising`：周销量增长率达到服务端阈值的商品。

排序方向脚本只接受 `asc` / `desc`。服务端排序字段使用源码白名单；不要传不存在或文档未收录的字段。

## 详情参数与返回

详情必须传 `goodsId`，可传 `mallId` 与 `analyticsWindowDays=7|28`。返回可包含：

- `goods`：当前商品；`skus`、`spu`：规格与可信聚合；
- `history`：观察历史；`sellerOffers`：当前已收录报价；
- `mall`、`site`、类目链与佣金带；
- `goodsUrl`、`mallUrl` 等来源明确的链接。

`sold7d/sold28d` 等显式窗口字段优先于无后缀字段。比例字段单位为百分比点；`20` 表示 20%。`salesEstimated`、`metricsPartial`、`dataSource`、`metricSource` 必须随结论说明。
