# governed/cli.py
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from governed.config import Config
from governed.engine import check_source
from governed.diagnostics import Severity


def _read_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as e:
        print(f"error: failed to read {path}: {e}", file=sys.stderr)
        sys.exit(1)


def _report_human(diagnostics):
    errors = [d for d in diagnostics if d.severity == Severity.ERROR]
    warnings = [d for d in diagnostics if d.severity == Severity.WARNING]

    for d in diagnostics:
        print(d.format_human())

    if errors:
        print(f"\n❌ {len(errors)} error(s), {len(warnings)} warning(s)")
        sys.exit(1)
    else:
        print(f"\n✅ check passed ({len(warnings)} warning(s))")
        sys.exit(0)


def _report_json(diagnostics):
    payload = {
        "valid": not any(d.severity == Severity.ERROR for d in diagnostics),
        "diagnostics": [d.to_json() for d in diagnostics],
    }
    print(json.dumps(payload, indent=2))
    sys.exit(0 if payload["valid"] else 1)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="governed",
        description="Governed Python static checker",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    check = sub.add_parser("check", help="Check a Python file")
    check.add_argument("file", type=Path)
    check.add_argument("--json", action="store_true", help="Emit JSON diagnostics")

    report = sub.add_parser("report", help="Alias for check with --json")
    report.add_argument("file", type=Path)

    args = parser.parse_args(argv)

    if args.command in {"check", "report"}:
        path: Path = args.file
        source = _read_file(path)

        config = Config()
        diagnostics = check_source(source, config)

        if args.command == "report" or getattr(args, "json", False):
            _report_json(diagnostics)
        else:
            _report_human(diagnostics)


if __name__ == "__main__":
    main()
