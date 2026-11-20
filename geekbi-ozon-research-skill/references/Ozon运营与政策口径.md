# Ozon 运营与政策口径

以下用于解释数据，不替代 Ozon 最新规则、卖家协议或专业税务/合规意见。涉及费用、物流、禁限售和促销时，应在执行当天复核官方页面。

- 未指定站点时默认俄罗斯站 `siteId=1`、`siteUID=ru`、币种 RUB；指定其他市场时先实时查询站点列表并使用其返回的 `siteId`、`siteUID` 和币种。站点存在不等于当前已有数据，空结果应按覆盖不足解释。
- `SKU` 是具体商品/规格记录；`SPU` 是服务端按已上报 `spuId`、`productId` 等可信身份聚合的规格组。没有可信关联时不能自行合并。
- `fulfillmentType`、`sellerType`、`metricSource`、`dataSource` 只按原值解释。Ozon 官方说明 realFBS/FBP 等可用方式会受仓库、路线和时间影响，不能把某个履约标签永久等同于跨境、时效或成本优势。[Ozon Partner Delivery](https://docs.ozon.com/global/en/fulfillment/rfbs/logistic-settings/partner-delivery-ozon/?country=TR)
- Ozon 官方分析工具包含卖家分析、站点趋势、热门商品和搜索查询等模块；极鲸云字段只有在响应明确给出来源和时间窗时，才可按相应指标解释，不能把采集快照冒充当前账号的完整 Seller Analytics。[Ozon Analytics Tools](https://docs.ozon.com/global/tr/analytics/analytics-and-metrics/analytics-tools/?country=TR)
- Ozon 商品卡中的价格、库存、媒体、佣金和状态会变化；当前结果是更新时间对应的快照。[Ozon 商品与价格管理](https://docs.ozon.com/global/ozon-seller-app/product-management/)
- 促销可能改变买家最终价格和搜索曝光，比较常规价与促销价时必须说明字段和时间。[Ozon 促销说明](https://docs.ozon.com/global/promotion/promotions/promo/?country=OTHER)
- 佣金、物流、仓储、广告、退货、税费和汇率都会影响利润。没有完整且同日的成本字段时，只能做收入或价差分析，不能声称净利润。
