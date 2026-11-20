#!/usr/bin/env python3
"""只读检查 ozon-keyword-validation 的本地运行条件。

不联网、不启动守护进程、不登录、不读取凭据值，也不创建或修改文件。
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

MIN_PYTHON = (3, 10)
VALID_OVERALL = {"ready", "partial", "needs_setup", "unavailable"}
VALID_PROBE_STATUSES = {"ready", "missing", "unavailable", "unknown"}


def version_text() -> str:
    return ".".join(str(part) for part in sys.version_info[:3])


def load_probe(path: Path | None) -> dict:
    """读取脱敏探测状态；兼容 Windows 常见 UTF-8 BOM，不读取任何凭据。"""
    if path is None:
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return {"probe_error": str(exc)}
    if not isinstance(value, dict):
        return {"probe_error": "probe 文件必须是 JSON 对象"}
    return value


def normalized_probe_status(probe: dict, key: str) -> str:
    value = str(probe.get(key, "unknown"))
    return value if value in VALID_PROBE_STATUSES else "unknown"


def main() -> int:
    parser = argparse.ArgumentParser(description="只读检查 Ozon 关键词验证环境")
    parser.add_argument(
        "--probe-results",
        type=Path,
        help="可选的脱敏宿主探测 JSON；只接受状态，不接受或输出 API Key、Cookie、密码或 Token。",
    )
    parser.add_argument(
        "--evidence-dir",
        type=Path,
        help="可选的项目内证据目录；仅检查存在性和可写性。",
    )
    args = parser.parse_args()

    checks: list[dict[str, object]] = []
    python_ok = sys.version_info[:2] >= MIN_PYTHON
    checks.append({
        "id": "python-runtime",
        "status": "ready" if python_ok else "missing",
        "detail": f"Python {version_text()}，要求不低于 3.10。",
    })

    probe = load_probe(args.probe_results)
    if "probe_error" in probe:
        for check_id in ("seller-api-readonly", "human-browser-session"):
            checks.append({
                "id": check_id,
                "status": "unknown",
                "detail": "未读取有效的脱敏宿主探测结果。",
            })
    else:
        checks.append({
            "id": "seller-api-readonly",
            "status": normalized_probe_status(probe, "seller_api_readonly"),
            "detail": "仅记录受信任宿主返回的只读 API 状态；不读取或输出凭据。",
        })
        checks.append({
            "id": "human-browser-session",
            "status": normalized_probe_status(probe, "human_browser_session"),
            "detail": "仅记录人工浏览器会话状态；不读取 Cookie、密码或令牌。",
        })

    if args.evidence_dir is None:
        evidence_status = "unknown"
        evidence_detail = "未指定项目内证据目录；仍可做不落盘的结构化分析。"
    elif not args.evidence_dir.exists() or not args.evidence_dir.is_dir():
        evidence_status = "missing"
        evidence_detail = "证据目录不存在或不是目录。"
    else:
        evidence_status = "ready" if os.access(args.evidence_dir, os.W_OK) else "unavailable"
        evidence_detail = "仅检查目录写入权限，不创建、修改或删除文件。"
    checks.append({"id": "project-evidence-directory", "status": evidence_status, "detail": evidence_detail})

    if not python_ok:
        overall = "needs_setup"
    elif any(item["status"] == "unavailable" for item in checks):
        overall = "unavailable"
    elif any(item["status"] == "missing" for item in checks):
        overall = "partial"
    elif any(item["status"] == "unknown" for item in checks):
        overall = "partial"
    else:
        overall = "ready"

    payload = {
        "status": overall if overall in VALID_OVERALL else "unavailable",
        "checks": checks,
        "credential_values_exposed": False,
        "network_requests_performed": False,
        "mutations_performed": False,
        "next_step": {
            "ready": "可直接进入与当前请求匹配的只读关键词验证流程。",
            "partial": "继续已就绪功能，并在交付中标注降级范围和证据等级。",
            "needs_setup": "只配置缺失的必需项后重新检查。",
            "unavailable": "检查授权、登录、网络、权限或目录问题；无法恢复时按降级矩阵执行。",
        }[overall],
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
