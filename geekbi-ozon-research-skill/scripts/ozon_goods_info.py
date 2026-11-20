#!/usr/bin/env python3
"""查询 Ozon 商品详情、SKU/SPU、报价与历史。"""

import argparse
import json
import sys
from urllib.error import HTTPError, URLError

from geekbi_auth import ActionRequired, authenticated_json_request
from ozon_search_common import DEFAULT_BASE_URL, build_url, validate_object_response


ENDPOINT = "/api/v1/ozon/goods/ai-info"


def build_params(goods_id, mall_id, site_id, analytics_window_days):
    if not goods_id.strip():
        raise ValueError("商品 ID 不能为空")
    if site_id < 1:
        raise ValueError("siteId 必须大于 0")
    if analytics_window_days not in {7, 28}:
        raise ValueError("analyticsWindowDays 只支持 7 或 28")
    params = [
        ("goodsId", goods_id.strip()), ("siteId", str(site_id)),
        ("analyticsWindowDays", str(analytics_window_days)),
    ]
    if mall_id and mall_id.strip():
        params.append(("mallId", mall_id.strip()))
    return params


def validate_response(payload):
    result = validate_object_response(payload, "goods", "Ozon 商品详情查询失败")
    data = result["data"]
    for key in ("history", "skus", "sellerOffers"):
        if key in data and not isinstance(data[key], list):
            raise ValueError(f"{key} 必须是数组")
    return result


def main():
    parser = argparse.ArgumentParser(description="查询 Ozon 商品详情、SKU/SPU 与历史")
    parser.add_argument("--goods-id", required=True)
    parser.add_argument("--mall-id")
    parser.add_argument("--site-id", type=int, default=1)
    parser.add_argument("--analytics-window-days", type=int, choices=(7, 28), default=7)
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--timeout", type=float, default=45)
    args = parser.parse_args()
    try:
        params = build_params(args.goods_id, args.mall_id, args.site_id, args.analytics_window_days)
        payload = authenticated_json_request(
            build_url(args.base_url, ENDPOINT, params), args.base_url, args.timeout
        )
        payload = validate_response(payload)
    except ActionRequired as error:
        print(json.dumps(error.public_payload(), ensure_ascii=False, indent=2))
        return 2
    except (ValueError, HTTPError, URLError, TimeoutError) as error:
        print(json.dumps({"error": True, "msg": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 1
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
