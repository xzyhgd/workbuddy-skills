#!/usr/bin/env python3
"""查询 Ozon 店铺详情与历史。"""

import argparse
import json
import sys
from urllib.error import HTTPError, URLError

from geekbi_auth import ActionRequired, authenticated_json_request
from ozon_search_common import DEFAULT_BASE_URL, build_url, validate_object_response


ENDPOINT = "/api/v1/ozon/mall/ai-info"


def build_params(mall_id, site_id):
    if not mall_id.strip():
        raise ValueError("店铺 ID 不能为空")
    if site_id < 1:
        raise ValueError("siteId 必须大于 0")
    return [("mallId", mall_id.strip()), ("siteId", str(site_id))]


def validate_response(payload):
    result = validate_object_response(payload, "mall", "Ozon 店铺详情查询失败")
    if "history" in result["data"] and not isinstance(result["data"]["history"], list):
        raise ValueError("history 必须是数组")
    return result


def main():
    parser = argparse.ArgumentParser(description="查询 Ozon 店铺详情与历史")
    parser.add_argument("--mall-id", required=True)
    parser.add_argument("--site-id", type=int, default=1)
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--timeout", type=float, default=45)
    args = parser.parse_args()
    try:
        params = build_params(args.mall_id, args.site_id)
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
