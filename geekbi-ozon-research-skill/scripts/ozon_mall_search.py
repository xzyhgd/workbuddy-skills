#!/usr/bin/env python3
"""调用极鲸云 Ozon 店铺搜索接口。"""

import argparse
import json
import sys
from urllib.error import HTTPError, URLError

from geekbi_auth import ActionRequired, authenticated_json_request
from ozon_search_common import (
    DEFAULT_BASE_URL, build_url, parse_int, parse_number, parse_pairs,
    validate_page, validate_range_pairs, validate_search_response, validate_site, validate_sort,
)


ENDPOINT = "/api/v1/ozon/mall/ai-search"
BASE_PARAMS = {
    "keyword", "preset", "catId", "brandId", "brand", "bodyName", "country",
    "chinaFlag", "mallLevel", "siteId", "page", "size", "sort", "order",
}
NUMERIC_RANGE_FIELDS = {
    "rank", "positiveRate", "onSaleGoodsNum", "mallStar", "reviewNum", "followerNum",
    "goodsNum", "spuNum", "daySold", "weekSold", "monthSold", "totalSold",
    "daySales", "weekSales", "monthSales", "totalSales",
}
INTEGER_RANGE_FIELDS = {
    "rank", "onSaleGoodsNum", "reviewNum", "followerNum", "goodsNum", "spuNum",
    "daySold", "weekSold", "monthSold", "totalSold",
}
DATE_RANGE_FIELDS = {"mallOpenTime"}
ALLOWED_PARAMS = BASE_PARAMS | {
    f"{field}{suffix}"
    for field in NUMERIC_RANGE_FIELDS | DATE_RANGE_FIELDS
    for suffix in ("Min", "Max")
}
SORT_FIELDS = {
    "updateTime", "observedAt", "mallSold", "mallSales", "goodsNum", "spuNum",
    "followerNum", "mallStar", "reviewNum", "avgPrice", "daySold", "weekSold",
    "monthSold", "daySales", "weekSales", "monthSales", "totalSold", "totalSales",
    "mallOpenTime", "mallLevel", "rank", "categoryRank", "positiveRate",
    "onSaleGoodsNum", "sellingGoodsNum",
}
PRESETS = {"hot", "hot-new", "new", "old-three-year", "quality", "plus", "china"}


def parse_params(raw_params):
    params, values = parse_pairs(raw_params, ALLOWED_PARAMS)
    validate_site(values)
    validate_page(values)
    validate_sort(values, SORT_FIELDS)
    validate_range_pairs(values, NUMERIC_RANGE_FIELDS, DATE_RANGE_FIELDS, INTEGER_RANGE_FIELDS)
    if "catId" in values:
        parse_int("catId", values["catId"], minimum=1)
    if "mallLevel" in values:
        parse_int("mallLevel", values["mallLevel"], minimum=0)
    if "chinaFlag" in values and values["chinaFlag"].lower() not in {"true", "false"}:
        raise ValueError("chinaFlag 只支持 true 或 false")
    if "preset" in values and values["preset"] not in PRESETS:
        raise ValueError("preset 不在当前支持的店铺榜单中")
    for field in ("mallStarMin", "mallStarMax"):
        if field in values and not 0 <= parse_number(field, values[field]) <= 5:
            raise ValueError(f"{field} 必须在 0 到 5 之间")
    return params


def main():
    parser = argparse.ArgumentParser(description="查询 Ozon 店铺并输出 JSON")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--param", action="append", default=[], help="查询条件，格式为 名称=值")
    parser.add_argument("--timeout", type=float, default=45)
    args = parser.parse_args()
    try:
        params = parse_params(args.param)
        payload = authenticated_json_request(
            build_url(args.base_url, ENDPOINT, params), args.base_url, args.timeout
        )
        payload = validate_search_response(payload, "Ozon 店铺查询失败")
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
