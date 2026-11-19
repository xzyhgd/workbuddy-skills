#!/usr/bin/env python3
"""Read-only environment check for ozon-product-research."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


MIN_PYTHON = (3, 10)
VALID_STATUSES = {"ready", "partial", "needs_setup", "unavailable"}


def version_text() -> str:
    return ".".join(str(part) for part in sys.version_info[:3])


def load_probe(path: Path | None) -> dict:
    if path is None:
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return {"probe_error": str(exc)}
    return value if isinstance(value, dict) else {"probe_error": "probe 文件必须是 JSON 对象"}


def main() -> int:
    parser = argparse.ArgumentParser(description="只读检查 Ozon 产品研究所需环境")
    parser.add_argument(
        "--probe-results",
        type=Path,
        help="可选的脱敏宿主探测 JSON；仅接受状态，不接受或输出凭据。",
    )
    parser.add_argument(
        "--evidence-dir",
        type=Path,
        help="可选的项目内证据目录，仅检查其是否存在和可写。",
    )
    args = parser.parse_args()

    checks: list[dict[str, object]] = []
    python_ok = sys.version_info[:2] >= MIN_PYTHON
    checks.append(
        {
            "id": "python-runtime",
            "status": "pass" if python_ok else "fail",
            "detail": f"Python {version_text()}，要求不低于 3.10",
        }
    )

    probe = load_probe(args.probe_results)
    if "probe_error" in probe:
        checks.append(
            {
                "id": "browser-session",
                "status": "unknown",
                "detail": "未读取有效的脱敏宿主探测结果。",
            }
        )
    else:
        session = str(probe.get("browser_session", "unknown"))
        if session not in {"ready", "missing", "unavailable", "unknown"}:
            session = "unknown"
        checks.append(
            {
                "id": "browser-session",
                "status": session,
                "detail": "仅记录人工浏览器会话状态；不读取 Cookie、密码或令牌。",
            }
        )

    if args.evidence_dir is None:
        evidence_status = "unknown"
        evidence_detail = "未指定证据目录；仍可进行不落盘的结构化分析。"
    elif not args.evidence_dir.exists() or not args.evidence_dir.is_dir():
        evidence_status = "missing"
        evidence_detail = "证据目录不存在或不是目录。"
    else:
        evidence_status = "ready" if os.access(args.evidence_dir, os.W_OK) else "unavailable"
        evidence_detail = "仅检查目录写入权限，不创建、修改或删除文件。"
    checks.append({"id": "evidence-directory", "status": evidence_status, "detail": evidence_detail})

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
        "status": overall if overall in VALID_STATUSES else "unavailable",
        "checks": checks,
        "credential_values_exposed": False,
        "mutations_performed": False,
        "next_step": {
            "ready": "可直接进入与当前请求匹配的研究流程。",
            "partial": "继续可用功能，并在交付中标注受影响范围与证据等级。",
            "needs_setup": "只配置缺失的必需项后重新检查。",
            "unavailable": "检查登录、权限、网络或目录问题；无法恢复时按降级矩阵执行。",
        }[overall],
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
