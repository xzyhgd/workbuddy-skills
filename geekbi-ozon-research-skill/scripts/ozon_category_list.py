#!/usr/bin/env python3
"""查询 Ozon 类目树的直接子类目。"""

import argparse
import json
import sys
from urllib.error import HTTPError, URLError

from geekbi_auth import ActionRequired, authenticated_json_request
from ozon_search_common import DEFAULT_BASE_URL, build_url, validate_envelope


ENDPOINT = "/api/v1/ozon/category/ai-list"


def build_params(parent_cat_id, site_id):
    if parent_cat_id < 0:
        raise ValueError("parentCatId 不能小于 0")
    if site_id < 1:
        raise ValueError("siteId 必须大于 0")
    return [("parentCatId", str(parent_cat_id)), ("siteId", str(site_id))]


def validate_response(payload):
    data = validate_envelope(payload, "Ozon 类目列表查询失败")
    if not isinstance(data, dict) or not isinstance(data.get("list"), list):
        raise ValueError("成功响应缺少类目 list")
    if not isinstance(data.get("site"), dict):
        raise ValueError("成功响应缺少站点信息")
    return {"code": 0, "data": data}


def main():
    parser = argparse.ArgumentParser(description="查询 Ozon 子类目")
    parser.add_argument("--parent-cat-id", type=int, default=0)
    parser.add_argument("--site-id", type=int, default=1)
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--timeout", type=float, default=45)
    args = parser.parse_args()
    try:
        params = build_params(args.parent_cat_id, args.site_id)
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
