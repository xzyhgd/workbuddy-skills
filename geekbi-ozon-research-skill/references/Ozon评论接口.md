# Ozon 评论接口

## 入口

- 搜索：`GET /api/v1/ozon/review/ai-search`
- 脚本：`ozon_review_search.py`

必须传明确 `goodsId`，可传 `keyword`、`score=1..5`、`page`、`size`、`sort=commentTime|helpful|score` 和 `order=asc|desc`。未指定站点时默认俄罗斯站 `siteId=1`；其他市场先查询站点列表。最多访问前 200 条。

返回字段可包含评论正文、标题、优点、缺点、规格、评分、图片、视频、有用数、作者、变体、地区、卖家回复、购买标记、回复数、评论时间、观察时间和来源。响应 `summary` 是完整筛选结果的总数、平均分、正向评论占比和带媒体占比，不是仅当前页统计。
