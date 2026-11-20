#!/usr/bin/env python3
"""查询 Ozon 关键词详情与历史。"""

import argparse
import json
import sys
from urllib.error import HTTPError, URLError

from geekbi_auth import ActionRequired, authenticated_json_request
from ozon_search_common import DEFAULT_BASE_URL, build_url, validate_object_response


ENDPOINT = "/api/v1/ozon/keyword/ai-info"


def build_params(keyword_id, keyword, site_id):
    if site_id < 1:
        raise ValueError("siteId 必须大于 0")
    if not (keyword_id and keyword_id.strip()) and not (keyword and keyword.strip()):
        raise ValueError("keywordId 或 keyword 至少提供一个")
    params = [("siteId", str(site_id))]
    if keyword_id and keyword_id.strip():
        params.append(("keywordId", keyword_id.strip()))
    else:
        params.append(("keyword", keyword.strip()))
    return params


def validate_response(payload):
    result = validate_object_response(payload, "keyword", "Ozon 关键词详情查询失败")
    if not isinstance(result["data"].get("history"), list):
        raise ValueError("成功响应缺少 history")
    return result


def main():
    parser = argparse.ArgumentParser(description="查询 Ozon 关键词详情与历史")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--keyword-id")
    group.add_argument("--keyword")
    parser.add_argument("--site-id", type=int, default=1)
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--timeout", type=float, default=45)
    args = parser.parse_args()
    try:
        params = build_params(args.keyword_id, args.keyword, args.site_id)
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
