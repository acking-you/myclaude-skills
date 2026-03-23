#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sqlite3
import sys
from dataclasses import asdict
from dataclasses import dataclass
from datetime import datetime
from datetime import timedelta
from pathlib import Path
from typing import Iterable
from typing import Sequence
from urllib.parse import quote

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None


DEFAULT_CODEX_HOME = Path.home() / ".codex"
SESSION_INDEX_FILENAME = "session_index.jsonl"
STATE_DB_PATTERN = re.compile(r"state_(\d+)\.sqlite$")
RELATIVE_TIME_PATTERN = re.compile(r"(?i)(\d+)\s*([smhdw])")
ANSI_PATTERN = re.compile(r"\x1b\[[0-9;]*m")

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"


@dataclass
class SessionRecord:
    session_id: str
    rollout_path: str
    created_at: int
    updated_at: int
    source: str
    model_provider: str
    cwd: str
    title: str
    first_user_message: str
    archived: bool
    archived_at: int | None
    cli_version: str
    model: str | None
    reasoning_effort: str | None
    tokens_used: int
    thread_name: str | None

    def best_label(self) -> str:
        if self.thread_name:
            return self.thread_name
        if self.title:
            return self.title
        if self.first_user_message:
            return self.first_user_message
        return "(empty preview)"

    def to_json_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["created_at_iso"] = format_timestamp(self.created_at)
        data["updated_at_iso"] = format_timestamp(self.updated_at)
        data["archived"] = bool(self.archived)
        return data


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Browse local Codex session history from SQLite and session_index.jsonl.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  codex_session_history.py --limit 20\n"
            "  codex_session_history.py --query provider --since 7d\n"
            "  codex_session_history.py --provider openai --view table\n"
            "  codex_session_history.py --sort-by created --since 2026-03-01 --until 2026-03-10\n"
            "  codex_session_history.py --view json --limit 200\n"
        ),
    )
    parser.add_argument("--db", help="Path to a specific state_*.sqlite file or directory.")
    parser.add_argument(
        "--codex-home",
        default=str(DEFAULT_CODEX_HOME),
        help="Codex home directory used to locate config.toml and session_index.jsonl.",
    )
    parser.add_argument(
        "--query",
        "-q",
        help="Case-insensitive substring search across id, provider, source, cwd, name, title, and preview.",
    )
    parser.add_argument(
        "--provider",
        action="append",
        default=[],
        help="Exact provider filter. Repeat to allow multiple providers.",
    )
    parser.add_argument(
        "--source",
        action="append",
        default=[],
        help="Exact source filter. Repeat to allow multiple sources.",
    )
    parser.add_argument(
        "--sort-by",
        choices=["updated", "created"],
        default="updated",
        help="Field used for ordering and time filtering.",
    )
    parser.add_argument(
        "--sort-order",
        choices=["desc", "asc"],
        default="desc",
        help="Sort direction.",
    )
    parser.add_argument(
        "--since",
        help="Lower bound for the selected time field. Accepts ISO time, YYYY-MM-DD, epoch seconds, or relative values like 7d or 12h.",
    )
    parser.add_argument(
        "--until",
        help="Upper bound for the selected time field. Accepts ISO time, YYYY-MM-DD, epoch seconds, or relative values like 7d or 12h.",
    )
    parser.add_argument(
        "--archived",
        choices=["any", "exclude", "only"],
        default="any",
        help="Archived session filter.",
    )
    parser.add_argument(
        "--limit",
        "-n",
        type=int,
        default=30,
        help="Maximum number of sessions to display after filtering.",
    )
    parser.add_argument(
        "--view",
        choices=["cards", "table", "json"],
        default="cards",
        help="Output layout.",
    )
    parser.add_argument(
        "--show-path",
        action="store_true",
        help="Include rollout path in card and table views.",
    )
    parser.add_argument(
        "--show-cwd",
        action="store_true",
        help="Include cwd in table view. Card view always includes cwd.",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable ANSI color output.",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Print provider/source counts for the filtered result set before the main output.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    color_enabled = sys.stdout.isatty() and not args.no_color

    try:
        codex_home = Path(args.codex_home).expanduser().resolve()
        db_path = detect_state_db_path(args.db, codex_home)
        index_path = codex_home / SESSION_INDEX_FILENAME
        session_names = load_session_names(index_path)

        with connect_read_only(db_path) as conn:
            total_count = fetch_total_count(conn)
            sessions = fetch_sessions(conn, args.sort_by, args.sort_order, session_names)

        filtered = filter_sessions(sessions, args)
        limited = filtered[: max(args.limit, 0)]

        if args.view == "json":
            json.dump([record.to_json_dict() for record in limited], sys.stdout, ensure_ascii=False, indent=2)
            sys.stdout.write("\n")
            return 0

        print_header(
            db_path=db_path,
            index_path=index_path,
            total_count=total_count,
            matched_count=len(filtered),
            shown_count=len(limited),
            args=args,
            color_enabled=color_enabled,
        )

        if args.stats:
            render_stats(filtered, color_enabled)

        if not limited:
            print(colorize("No matching sessions.", YELLOW, color_enabled))
            return 0

        if args.view == "table":
            render_table(limited, args, color_enabled)
        else:
            render_cards(limited, args, color_enabled)

        return 0
    except KeyboardInterrupt:
        return 130
    except Exception as err:  # pragma: no cover
        print(colorize(f"Error: {err}", RED, color_enabled=False), file=sys.stderr)
        return 1


def detect_state_db_path(explicit_db: str | None, codex_home: Path) -> Path:
    candidates: list[Path] = []

    if explicit_db:
        explicit_path = Path(explicit_db).expanduser()
        candidates.extend(find_state_db_candidates(explicit_path))
    else:
        env_home = os.environ.get("CODEX_SQLITE_HOME", "").strip()
        if env_home:
            candidates.extend(find_state_db_candidates(Path(env_home).expanduser()))

        configured_home = read_configured_sqlite_home(codex_home)
        if configured_home is not None:
            candidates.extend(find_state_db_candidates(configured_home))

        candidates.extend(find_state_db_candidates(codex_home))
        candidates.extend(find_state_db_candidates(codex_home / "sqlite"))

    deduped: list[Path] = []
    seen: set[Path] = set()
    for candidate in candidates:
        resolved = candidate.resolve()
        if resolved not in seen and resolved.exists():
            deduped.append(resolved)
            seen.add(resolved)

    if not deduped:
        raise FileNotFoundError(
            "Could not locate a state_*.sqlite file. Use --db or set CODEX_SQLITE_HOME."
        )

    deduped.sort(key=state_db_sort_key, reverse=True)
    return deduped[0]


def state_db_sort_key(path: Path) -> tuple[int, float]:
    match = STATE_DB_PATTERN.search(path.name)
    version = int(match.group(1)) if match else -1
    try:
        mtime = path.stat().st_mtime
    except OSError:
        mtime = 0.0
    return (version, mtime)


def find_state_db_candidates(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if not path.exists():
        return []
    return sorted(path.glob("state_*.sqlite"))


def read_configured_sqlite_home(codex_home: Path) -> Path | None:
    if tomllib is None:
        return None

    config_path = codex_home / "config.toml"
    if not config_path.exists():
        return None

    try:
        config = tomllib.loads(config_path.read_text(encoding="utf-8"))
    except Exception:
        return None

    sqlite_home = config.get("sqlite_home")
    if not isinstance(sqlite_home, str) or not sqlite_home.strip():
        return None

    raw_path = Path(sqlite_home.strip()).expanduser()
    if raw_path.is_absolute():
        return raw_path
    return Path.cwd() / raw_path


def connect_read_only(db_path: Path) -> sqlite3.Connection:
    uri = f"file:{quote(str(db_path), safe='/')}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def fetch_total_count(conn: sqlite3.Connection) -> int:
    row = conn.execute("SELECT COUNT(*) AS count FROM threads").fetchone()
    return int(row["count"]) if row is not None else 0


def fetch_sessions(
    conn: sqlite3.Connection,
    sort_by: str,
    sort_order: str,
    session_names: dict[str, str],
) -> list[SessionRecord]:
    order_column = "updated_at" if sort_by == "updated" else "created_at"
    order_direction = "DESC" if sort_order == "desc" else "ASC"
    query = f"""
SELECT
    id,
    rollout_path,
    created_at,
    updated_at,
    source,
    model_provider,
    cwd,
    title,
    first_user_message,
    archived,
    archived_at,
    cli_version,
    model,
    reasoning_effort,
    tokens_used
FROM threads
ORDER BY {order_column} {order_direction}, id {order_direction}
"""
    rows = conn.execute(query).fetchall()
    sessions: list[SessionRecord] = []
    for row in rows:
        session_id = row["id"]
        sessions.append(
            SessionRecord(
                session_id=session_id,
                rollout_path=row["rollout_path"],
                created_at=int(row["created_at"]),
                updated_at=int(row["updated_at"]),
                source=row["source"],
                model_provider=row["model_provider"],
                cwd=row["cwd"],
                title=row["title"],
                first_user_message=row["first_user_message"],
                archived=bool(row["archived"]),
                archived_at=int(row["archived_at"]) if row["archived_at"] is not None else None,
                cli_version=row["cli_version"],
                model=row["model"],
                reasoning_effort=row["reasoning_effort"],
                tokens_used=int(row["tokens_used"]),
                thread_name=session_names.get(session_id),
            )
        )
    return sessions


def load_session_names(index_path: Path) -> dict[str, str]:
    if not index_path.exists():
        return {}

    latest: dict[str, tuple[str, str]] = {}
    with index_path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
            session_id = payload.get("id")
            thread_name = payload.get("thread_name")
            updated_at = payload.get("updated_at", "")
            if not session_id or not thread_name:
                continue
            previous = latest.get(session_id)
            if previous is None or updated_at >= previous[0]:
                latest[session_id] = (updated_at, thread_name)
    return {session_id: value[1] for session_id, value in latest.items()}


def filter_sessions(records: Sequence[SessionRecord], args: argparse.Namespace) -> list[SessionRecord]:
    providers = {item.lower() for item in args.provider}
    sources = {item.lower() for item in args.source}
    query_tokens = [token.lower() for token in (args.query or "").split() if token.strip()]
    now = datetime.now().astimezone()
    since_ts = parse_time_expression(args.since, now, end_of_day=False) if args.since else None
    until_ts = parse_time_expression(args.until, now, end_of_day=True) if args.until else None
    time_field = "updated_at" if args.sort_by == "updated" else "created_at"

    filtered: list[SessionRecord] = []
    for record in records:
        if args.archived == "exclude" and record.archived:
            continue
        if args.archived == "only" and not record.archived:
            continue
        if providers and record.model_provider.lower() not in providers:
            continue
        if sources and record.source.lower() not in sources:
            continue

        field_ts = getattr(record, time_field)
        if since_ts is not None and field_ts < since_ts:
            continue
        if until_ts is not None and field_ts > until_ts:
            continue

        if query_tokens:
            haystack = " ".join(
                [
                    record.session_id,
                    record.model_provider,
                    record.source,
                    record.cwd,
                    record.rollout_path,
                    record.thread_name or "",
                    record.title,
                    record.first_user_message,
                ]
            ).lower()
            if any(token not in haystack for token in query_tokens):
                continue

        filtered.append(record)

    return filtered


def parse_time_expression(value: str, now: datetime, end_of_day: bool) -> int:
    stripped = value.strip()
    if not stripped:
        raise ValueError("time filter cannot be empty")

    if stripped.lower() == "now":
        return int(now.timestamp())
    if stripped.lower() == "today":
        dt = now.replace(hour=23 if end_of_day else 0, minute=59 if end_of_day else 0, second=59 if end_of_day else 0, microsecond=999999 if end_of_day else 0)
        return int(dt.timestamp())
    if stripped.lower() == "yesterday":
        yesterday = now - timedelta(days=1)
        dt = yesterday.replace(hour=23 if end_of_day else 0, minute=59 if end_of_day else 0, second=59 if end_of_day else 0, microsecond=999999 if end_of_day else 0)
        return int(dt.timestamp())

    if stripped.isdigit():
        return int(stripped)

    relative_matches = list(RELATIVE_TIME_PATTERN.finditer(stripped))
    if relative_matches and "".join(match.group(0) for match in relative_matches).replace(" ", "").lower() == stripped.replace(" ", "").lower():
        delta = timedelta()
        for match in relative_matches:
            amount = int(match.group(1))
            unit = match.group(2).lower()
            if unit == "s":
                delta += timedelta(seconds=amount)
            elif unit == "m":
                delta += timedelta(minutes=amount)
            elif unit == "h":
                delta += timedelta(hours=amount)
            elif unit == "d":
                delta += timedelta(days=amount)
            elif unit == "w":
                delta += timedelta(weeks=amount)
        return int((now - delta).timestamp())

    try:
        dt = datetime.fromisoformat(stripped.replace("Z", "+00:00"))
    except ValueError as err:
        raise ValueError(f"unsupported time expression: {value}") from err

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=now.tzinfo)

    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", stripped):
        if end_of_day:
            dt = dt.replace(hour=23, minute=59, second=59, microsecond=999999)
        else:
            dt = dt.replace(hour=0, minute=0, second=0, microsecond=0)

    return int(dt.timestamp())


def print_header(
    db_path: Path,
    index_path: Path,
    total_count: int,
    matched_count: int,
    shown_count: int,
    args: argparse.Namespace,
    color_enabled: bool,
) -> None:
    print(colorize("Codex Session History", BOLD + CYAN, color_enabled))
    print(f"  DB     : {db_path}")
    print(f"  Index  : {index_path}")
    print(f"  Rows   : {shown_count} shown / {matched_count} matched / {total_count} total")
    print(f"  Sort   : {args.sort_by} {args.sort_order}")
    filters = []
    if args.query:
        filters.append(f"query={args.query!r}")
    if args.provider:
        filters.append(f"provider={','.join(args.provider)}")
    if args.source:
        filters.append(f"source={','.join(args.source)}")
    if args.archived != "any":
        filters.append(f"archived={args.archived}")
    if args.since:
        filters.append(f"since={args.since}")
    if args.until:
        filters.append(f"until={args.until}")
    if filters:
        print(f"  Filter : {' | '.join(filters)}")
    print()


def render_stats(records: Sequence[SessionRecord], color_enabled: bool) -> None:
    provider_counts: dict[str, int] = {}
    source_counts: dict[str, int] = {}
    archived_count = 0

    for record in records:
        provider_counts[record.model_provider] = provider_counts.get(record.model_provider, 0) + 1
        source_counts[record.source] = source_counts.get(record.source, 0) + 1
        if record.archived:
            archived_count += 1

    print(colorize("Stats", BOLD + BLUE, color_enabled))
    print(f"  Archived : {archived_count}")
    print(f"  Providers: {format_counter_map(provider_counts)}")
    print(f"  Sources  : {format_counter_map(source_counts)}")
    print()


def format_counter_map(counter_map: dict[str, int]) -> str:
    if not counter_map:
        return "-"
    parts = [f"{name}={count}" for name, count in sorted(counter_map.items(), key=lambda item: (-item[1], item[0]))]
    return ", ".join(parts)


def render_cards(records: Sequence[SessionRecord], args: argparse.Namespace, color_enabled: bool) -> None:
    terminal_width = max(80, shutil.get_terminal_size((120, 40)).columns)
    query_tokens = [token for token in (args.query or "").split() if token.strip()]
    separator = "-" * min(terminal_width, 120)

    for index, record in enumerate(records, start=1):
        heading = (
            f"[{index:02d}] {record.session_id}  "
            f"{record.model_provider}  "
            f"{record.source}"
        )
        if record.archived:
            heading += "  archived"
        print(colorize(heading, BOLD + GREEN, color_enabled))
        print(
            f"  updated: {format_timestamp(record.updated_at)} ({format_relative(record.updated_at)})"
            f" | created: {format_timestamp(record.created_at)}"
        )

        if record.thread_name:
            print_wrapped_field("name", record.thread_name, terminal_width, query_tokens, color_enabled)
        if record.title and record.title != record.thread_name:
            print_wrapped_field("title", record.title, terminal_width, query_tokens, color_enabled)

        preview = record.first_user_message or "(empty preview)"
        print_wrapped_field("preview", preview, terminal_width, query_tokens, color_enabled)
        print_wrapped_field("cwd", record.cwd, terminal_width, query_tokens, color_enabled)
        print_wrapped_field("resume", f"codex resume {record.session_id}", terminal_width, query_tokens, color_enabled)

        extra = []
        if record.model:
            extra.append(f"model={record.model}")
        if record.reasoning_effort:
            extra.append(f"reasoning={record.reasoning_effort}")
        if record.cli_version:
            extra.append(f"cli={record.cli_version}")
        extra.append(f"tokens={record.tokens_used}")
        print(f"  meta   : {' | '.join(extra)}")

        if args.show_path:
            print_wrapped_field("path", record.rollout_path, terminal_width, query_tokens, color_enabled)

        print(colorize(separator, DIM, color_enabled))


def print_wrapped_field(
    label: str,
    value: str,
    terminal_width: int,
    query_tokens: Sequence[str],
    color_enabled: bool,
) -> None:
    prefix = f"  {label:<7}: "
    available = max(20, min(terminal_width, 120) - display_width(prefix))
    wrapped = wrap_display(value, available)
    for idx, line in enumerate(wrapped):
        rendered = highlight_terms(line, query_tokens, color_enabled)
        if idx == 0:
            print(prefix + rendered)
        else:
            print(" " * display_width(prefix) + rendered)


def render_table(records: Sequence[SessionRecord], args: argparse.Namespace, color_enabled: bool) -> None:
    width = max(100, shutil.get_terminal_size((120, 40)).columns)
    query_tokens = [token for token in (args.query or "").split() if token.strip()]

    columns: list[tuple[str, int]] = [
        ("#", 4),
        ("Session ID", 36),
        ("Provider", 14),
        ("Updated", 17),
        ("Label", max(20, width - 4 - 36 - 14 - 17 - 12)),
    ]
    if args.show_cwd:
        columns.append(("CWD", 24))
    if args.show_path:
        columns.append(("Path", 28))

    header = " ".join(header_text.ljust(col_width) for header_text, col_width in columns)
    print(colorize(header, BOLD + MAGENTA, color_enabled))
    print(colorize("-" * min(width, display_width(header)), DIM, color_enabled))

    for index, record in enumerate(records, start=1):
        label = record.best_label()
        values = [
            str(index).rjust(2),
            record.session_id,
            record.model_provider + ("*" if record.archived else ""),
            format_timestamp(record.updated_at, with_seconds=False),
            label,
        ]
        if args.show_cwd:
            values.append(record.cwd)
        if args.show_path:
            values.append(record.rollout_path)

        padded = []
        for (header_text, col_width), value in zip(columns, values):
            cell = truncate_display(value, col_width)
            cell = highlight_terms(cell, query_tokens, color_enabled)
            if header_text == "#":
                padded.append(cell.rjust(col_width))
            else:
                padded.append(cell.ljust(col_width + len(cell) - display_width(cell)))
        print(" ".join(padded))
    print()
    print(colorize("* archived session", DIM, color_enabled))


def highlight_terms(text: str, tokens: Sequence[str], color_enabled: bool) -> str:
    if not tokens or not color_enabled:
        return text

    def replace_match(match: re.Match[str]) -> str:
        return f"{YELLOW}{BOLD}{match.group(0)}{RESET}"

    result = text
    for token in sorted(tokens, key=len, reverse=True):
        result = re.sub(re.escape(token), replace_match, result, flags=re.IGNORECASE)
    return result


def colorize(text: str, style: str, enabled: bool) -> str:
    if not enabled:
        return text
    return f"{style}{text}{RESET}"


def format_timestamp(epoch_seconds: int, with_seconds: bool = True) -> str:
    dt = datetime.fromtimestamp(epoch_seconds).astimezone()
    return dt.strftime("%Y-%m-%d %H:%M:%S" if with_seconds else "%Y-%m-%d %H:%M")


def format_relative(epoch_seconds: int) -> str:
    now = datetime.now().astimezone().timestamp()
    delta = int(now - epoch_seconds)
    suffix = "ago" if delta >= 0 else "from now"
    delta = abs(delta)

    if delta < 60:
        return f"{delta}s {suffix}"
    if delta < 3600:
        return f"{delta // 60}m {suffix}"
    if delta < 86400:
        return f"{delta // 3600}h {suffix}"
    if delta < 86400 * 30:
        return f"{delta // 86400}d {suffix}"
    return f"{delta // (86400 * 30)}mo {suffix}"


def wrap_display(text: str, width: int) -> list[str]:
    if width <= 1:
        return [text]

    lines: list[str] = []
    for paragraph in text.splitlines() or [""]:
        if not paragraph:
            lines.append("")
            continue
        if " " not in paragraph:
            lines.extend(break_word(paragraph, width))
            continue

        current = ""
        for word in paragraph.split(" "):
            candidate = word if not current else f"{current} {word}"
            if display_width(candidate) <= width:
                current = candidate
                continue
            if current:
                lines.append(current)
            if display_width(word) <= width:
                current = word
            else:
                chunks = break_word(word, width)
                lines.extend(chunks[:-1])
                current = chunks[-1]
        if current:
            lines.append(current)
    return lines or [""]


def break_word(text: str, width: int) -> list[str]:
    chunks: list[str] = []
    current = ""
    for char in text:
        if display_width(current + char) > width and current:
            chunks.append(current)
            current = char
        else:
            current += char
    if current:
        chunks.append(current)
    return chunks or [text]


def truncate_display(text: str, width: int) -> str:
    if display_width(text) <= width:
        return text
    if width <= 3:
        return "." * max(width, 0)

    trimmed = ""
    for char in text:
        if display_width(trimmed + char + "...") > width:
            break
        trimmed += char
    return trimmed + "..."


def display_width(text: str) -> int:
    clean = ANSI_PATTERN.sub("", text)
    width = 0
    for char in clean:
        codepoint = ord(char)
        if codepoint < 32 or 0x7F <= codepoint < 0xA0:
            continue
        width += 2 if is_wide_char(char) else 1
    return width


def is_wide_char(char: str) -> bool:
    import unicodedata

    return unicodedata.east_asian_width(char) in {"W", "F"}


if __name__ == "__main__":
    raise SystemExit(main())
