#!/usr/bin/env python3
"""查询 Ozon 当前支持的站点并按名称解析。"""

import argparse
import json
import sys
from urllib.error import HTTPError, URLError

from geekbi_auth import ActionRequired, authenticated_json_request, response_message
from ozon_search_common import DEFAULT_BASE_URL


ENDPOINT = "/api/v1/ozon/site/ai-list"


def normalize(value):
    return value.strip().casefold().removesuffix("站点").removesuffix("站").strip()


def validate_response(payload):
    if not isinstance(payload, dict):
        raise ValueError("站点列表响应必须是 JSON 对象")
    if payload.get("code") != 0:
        raise ValueError(response_message(payload, "Ozon 站点查询失败"))
    if not isinstance(payload.get("data"), list):
        raise ValueError("站点列表响应缺少 data 数组")
    return payload["data"]


def resolve_site(sites, country):
    target = normalize(country)
    matches = []
    for item in sites:
        if not isinstance(item, dict):
            continue
        candidates = {
            item.get("name"), item.get("country"), item.get("siteUID"), item.get("siteHost"),
        }
        if item.get("siteUID") == "ru":
            candidates.update({"俄罗斯", "俄国", "russia"})
        if target in {normalize(value) for value in candidates if isinstance(value, str)}:
            matches.append(item)
    if not matches:
        raise ValueError("未找到该 Ozon 站点，请确认中文名、站点 UID 或域名")
    return matches


def main():
    parser = argparse.ArgumentParser(description="查询并解析 Ozon 站点")
    parser.add_argument("--country", help="国家、站点 UID 或域名；不传则返回全部")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--timeout", type=float, default=30)
    args = parser.parse_args()
    try:
        payload = authenticated_json_request(
            f"{args.base_url.rstrip('/')}{ENDPOINT}", args.base_url, args.timeout
        )
        sites = validate_response(payload)
        data = resolve_site(sites, args.country) if args.country else sites
    except ActionRequired as error:
        print(json.dumps(error.public_payload(), ensure_ascii=False, indent=2))
        return 2
    except (ValueError, HTTPError, URLError, TimeoutError) as error:
        print(json.dumps({"error": True, "msg": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 1
    print(json.dumps({"code": 0, "data": {"matches": data}}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
