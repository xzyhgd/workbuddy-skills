# Ozon 店铺接口

## 入口

- 搜索：`GET /api/v1/ozon/mall/ai-search`
- 详情：`GET /api/v1/ozon/mall/ai-info`
- 脚本：`ozon_mall_search.py`、`ozon_mall_info.py`

未指定站点时默认俄罗斯站 `siteId=1`；其他市场先查询站点列表。搜索最多访问前 200 条。

基础条件：`keyword`、`catId`、`brandId`、`brand`、`bodyName`、`country`、`chinaFlag`、`mallLevel`。区间支持排名、好评率、在售商品数、评分、评论数、粉丝、SKU/SPU、日周月/累计销量与销售额、开店时间。

榜单预设：`hot`、`hot-new`、`new`、`old-three-year`、`quality`、`plus`、`china`。排序白名单包括销量销售额、商品数、粉丝、评分、评论、客单价、开店时间、等级、排名和好评率等。

详情必须传 `mallId`，返回 `mall`、`history`、7 日可观察销量趋势及站点信息。缺失的商品/SPU 数可能由当前已索引商品事实补充，并带 `goodsAggregationSource` 和 `goodsAggregationScope`。
