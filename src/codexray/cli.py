from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from .analyzer import analyze_file_snippet, analyze_path, analyze_snippet
from .config import AnalyzerConfig


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="codexray",
        description="Offline-first static analysis for Python files and notebooks.",
    )
    parser.add_argument(
        "target", nargs="?", help="Path to file or directory to analyze"
    )
    parser.add_argument("--snippet", help="Inline Python snippet to analyze")
    parser.add_argument(
        "--start-line", type=int, help="Start line for target file snippet analysis"
    )
    parser.add_argument(
        "--end-line", type=int, help="End line for target file snippet analysis"
    )
    parser.add_argument("--output", help="Write JSON result to this path")
    parser.add_argument(
        "--allow-network", action="store_true", help="Enable network-dependent features"
    )
    parser.add_argument("--max-file-bytes", type=int, default=2 * 1024 * 1024)
    parser.add_argument("--max-snippet-chars", type=int, default=50_000)

    args = parser.parse_args()

    if not args.target and not args.snippet:
        parser.error("Provide a target path or use --snippet")

    config = AnalyzerConfig(
        allow_network=args.allow_network,
        max_file_size_bytes=args.max_file_bytes,
        max_snippet_chars=args.max_snippet_chars,
    )

    if args.snippet:
        result = analyze_snippet(args.snippet, config=config)
    elif args.start_line is not None and args.end_line is not None:
        if not args.target:
            parser.error("Line-range analysis requires a file target")
        result = analyze_file_snippet(
            Path(args.target),
            start_line=args.start_line,
            end_line=args.end_line,
            config=config,
        )
    else:
        result = analyze_path(Path(args.target), config=config)

    payload = asdict(result)
    rendered = json.dumps(payload, indent=2)

    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    else:
        print(rendered)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
