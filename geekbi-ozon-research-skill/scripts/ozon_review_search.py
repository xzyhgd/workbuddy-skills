#!/usr/bin/env python3
"""按商品 ID 查询极鲸云 Ozon 评论。"""

import argparse
import json
import sys
from urllib.error import HTTPError, URLError

from geekbi_auth import ActionRequired, authenticated_json_request
from ozon_search_common import (
    DEFAULT_BASE_URL, build_url, parse_int, parse_pairs, validate_page,
    validate_search_response, validate_site, validate_sort,
)


ENDPOINT = "/api/v1/ozon/review/ai-search"
ALLOWED_PARAMS = {"goodsId", "keyword", "score", "siteId", "page", "size", "sort", "order"}
SORT_FIELDS = {"commentTime", "helpful", "score"}


def parse_params(raw_params):
    params, values = parse_pairs(raw_params, ALLOWED_PARAMS)
    if not values.get("goodsId", "").strip():
        raise ValueError("必须提供明确的 goodsId")
    validate_site(values)
    validate_page(values)
    validate_sort(values, SORT_FIELDS)
    if "score" in values:
        parse_int("score", values["score"], minimum=1, maximum=5)
    return params


def main():
    parser = argparse.ArgumentParser(description="查询 Ozon 商品评论并输出 JSON")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--param", action="append", default=[], help="查询条件，格式为 名称=值")
    parser.add_argument("--timeout", type=float, default=45)
    args = parser.parse_args()
    try:
        params = parse_params(args.param)
        payload = authenticated_json_request(
            build_url(args.base_url, ENDPOINT, params), args.base_url, args.timeout
        )
        payload = validate_search_response(payload, "Ozon 评论查询失败")
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
