#!/usr/bin/env python3
"""调用极鲸云 Ozon 关键词搜索接口。"""

import argparse
import json
import sys
from urllib.error import HTTPError, URLError

from geekbi_auth import ActionRequired, authenticated_json_request
from ozon_search_common import (
    DEFAULT_BASE_URL, build_url, parse_int, parse_pairs, validate_page,
    validate_range_pairs, validate_search_response, validate_site, validate_sort,
)


ENDPOINT = "/api/v1/ozon/keyword/ai-search"
BASE_PARAMS = {"keyword", "catId", "siteId", "page", "size", "sort", "order"}
RANGE_FIELDS = {"dsr", "itemCount", "monthSold", "monthSales"}
INTEGER_RANGE_FIELDS = {"dsr", "itemCount", "monthSold"}
ALLOWED_PARAMS = BASE_PARAMS | {
    f"{field}{suffix}" for field in RANGE_FIELDS for suffix in ("Min", "Max")
}
SORT_FIELDS = {
    "updateTime", "searchVolume", "totalSold", "totalSales", "itemCount", "mallCount",
    "dsr", "daySold", "weekSold", "monthSold", "daySales", "weekSales", "monthSales", "avgPrice",
}


def parse_params(raw_params):
    params, values = parse_pairs(raw_params, ALLOWED_PARAMS)
    validate_site(values)
    validate_page(values)
    validate_sort(values, SORT_FIELDS)
    validate_range_pairs(values, RANGE_FIELDS, integer_fields=INTEGER_RANGE_FIELDS)
    if "catId" in values:
        parse_int("catId", values["catId"], minimum=1)
    return params


def main():
    parser = argparse.ArgumentParser(description="查询 Ozon 关键词并输出 JSON")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--param", action="append", default=[], help="查询条件，格式为 名称=值")
    parser.add_argument("--timeout", type=float, default=45)
    args = parser.parse_args()
    try:
        params = parse_params(args.param)
        payload = authenticated_json_request(
            build_url(args.base_url, ENDPOINT, params), args.base_url, args.timeout
        )
        payload = validate_search_response(payload, "Ozon 关键词查询失败")
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
