#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


APP_NAME = "commandclaw-session-capture"
STATE_VERSION = 1
DEDUP_WINDOW_SECONDS = 60
MAX_CONTEXT_CHARS = 12000
RECENT_SESSION_CHARS = 4000


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def state_path() -> Path:
    return repo_root() / ".claude" / "state.json"


def sessions_dir() -> Path:
    return repo_root() / "raw" / "sessions"


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def read_stdin() -> str:
    if sys.stdin.isatty():
        return ""
    return sys.stdin.read()


def load_state() -> dict[str, Any]:
    path = state_path()
    if not path.exists():
        return {
            "version": STATE_VERSION,
            "captures": {},
            "cost": {"events": 0},
        }

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {
            "version": STATE_VERSION,
            "captures": {},
            "cost": {"events": 0},
        }

    data.setdefault("version", STATE_VERSION)
    data.setdefault("captures", {})
    data.setdefault("cost", {"events": 0})
    return data


def save_state(state: dict[str, Any]) -> None:
    path = state_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def parse_payload(raw_text: str) -> tuple[str, str | None]:
    text = raw_text.strip()
    if not text:
        return "", None

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return text, None

    pretty = json.dumps(parsed, indent=2, sort_keys=True)
    session_id = None
    if isinstance(parsed, dict):
        value = parsed.get("session_id") or parsed.get("sessionId")
        if isinstance(value, str):
            session_id = value
    return pretty, session_id


def session_file_for(date: datetime) -> Path:
    return sessions_dir() / f"{date.date().isoformat()}.md"


def ensure_session_file(path: Path, date: datetime) -> None:
    if path.exists():
        return
    header = "\n".join(
        [
            f"# Claude Session Captures for {date.date().isoformat()}",
            "",
            "Machine-generated hook captures written to `raw/sessions/`.",
            "Treat this file as an immutable raw source for later compilation.",
            "",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(header, encoding="utf-8")


def render_capture_entry(
    *,
    timestamp: datetime,
    event_name: str,
    session_id: str,
    payload_text: str,
    payload_sha: str,
) -> str:
    lines = [
        "",
        f"## {timestamp.isoformat()} | {event_name} | session `{session_id}`",
        f"- Hook: `{event_name}`",
        f"- Session ID: `{session_id}`",
        f"- Payload SHA-256: `{payload_sha}`",
        f"- Payload bytes: `{len(payload_text.encode('utf-8'))}`",
        "",
    ]

    if payload_text:
        fence = "json" if payload_text.startswith("{") or payload_text.startswith("[") else "text"
        lines.extend(
            [
                f"```{fence}",
                payload_text,
                "```",
                "",
            ]
        )
    else:
        lines.extend(["_No stdin payload was provided by the hook._", ""])

    return "\n".join(lines)


def should_skip_capture(
    *,
    state: dict[str, Any],
    event_name: str,
    session_id: str,
    payload_sha: str,
    timestamp: datetime,
) -> bool:
    key = f"{event_name}:{session_id}"
    previous = state["captures"].get(key)
    if not isinstance(previous, dict):
        return False

    if previous.get("sha256") != payload_sha:
        return False

    seen_at = previous.get("captured_at")
    if not isinstance(seen_at, str):
        return False

    try:
        previous_ts = datetime.fromisoformat(seen_at)
    except ValueError:
        return False

    return timestamp - previous_ts <= timedelta(seconds=DEDUP_WINDOW_SECONDS)


def record_capture_state(
    *,
    state: dict[str, Any],
    event_name: str,
    session_id: str,
    payload_sha: str,
    timestamp: datetime,
) -> None:
    key = f"{event_name}:{session_id}"
    state["captures"][key] = {
        "captured_at": timestamp.isoformat(),
        "sha256": payload_sha,
    }
    state["cost"]["events"] = int(state["cost"].get("events", 0)) + 1


def command_capture(args: argparse.Namespace) -> int:
    if os.environ.get("CLAUDE_INVOKED_BY") == APP_NAME:
        print("SESSION_CAPTURE_SKIPPED recursion-guard")
        return 0

    timestamp = now_utc()
    raw_payload = read_stdin()
    payload_text, payload_session_id = parse_payload(raw_payload)
    payload_sha = sha256_text(payload_text or raw_payload or "")
    event_name = args.event or os.environ.get("CLAUDE_HOOK_EVENT_NAME") or "UnknownEvent"
    session_id = (
        os.environ.get("CLAUDE_SESSION_ID")
        or payload_session_id
        or os.environ.get("CLAUDE_SESSION")
        or "unknown"
    )

    state = load_state()
    if should_skip_capture(
        state=state,
        event_name=event_name,
        session_id=session_id,
        payload_sha=payload_sha,
        timestamp=timestamp,
    ):
        print("SESSION_CAPTURE_SKIPPED duplicate")
        return 0

    path = session_file_for(timestamp)
    ensure_session_file(path, timestamp)
    entry = render_capture_entry(
        timestamp=timestamp,
        event_name=event_name,
        session_id=session_id,
        payload_text=payload_text,
        payload_sha=payload_sha,
    )
    with path.open("a", encoding="utf-8") as handle:
        handle.write(entry)

    record_capture_state(
        state=state,
        event_name=event_name,
        session_id=session_id,
        payload_sha=payload_sha,
        timestamp=timestamp,
    )
    save_state(state)
    print(f"SESSION_CAPTURED {path.relative_to(repo_root())}")
    return 0


def trim_block(text: str, limit: int) -> str:
    stripped = text.strip()
    if len(stripped) <= limit:
        return stripped
    return stripped[-limit:]


def load_optional_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def latest_session_file() -> Path | None:
    files = sorted(sessions_dir().glob("*.md"))
    if not files:
        return None
    return files[-1]


def command_context(_: argparse.Namespace) -> int:
    parts: list[str] = []

    index_text = trim_block(load_optional_text(repo_root() / "wiki" / "index.md"), 5000)
    overview_text = trim_block(load_optional_text(repo_root() / "wiki" / "overview.md"), 3000)
    session_path = latest_session_file()
    recent_session = trim_block(load_optional_text(session_path), RECENT_SESSION_CHARS) if session_path else ""

    if index_text:
        parts.extend(["# Wiki Index", "", index_text, ""])

    if overview_text:
        parts.extend(["# Wiki Overview", "", overview_text, ""])

    if recent_session and session_path is not None:
        parts.extend(
            [
                f"# Recent Session Log ({session_path.relative_to(repo_root())})",
                "",
                recent_session,
                "",
            ]
        )

    output = "\n".join(parts).strip()
    print(trim_block(output, MAX_CONTEXT_CHARS))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="CommandClaw session capture utilities.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    capture = subparsers.add_parser("capture", help="Append a session hook payload to raw/sessions/.")
    capture.add_argument("--event", help="Explicit hook event name.")
    capture.set_defaults(func=command_capture)

    context = subparsers.add_parser("context", help="Emit startup context for Claude Code.")
    context.set_defaults(func=command_context)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
