"""python -m prd_agent <artifact-path> [--autonomous] [--out stories/<name>.md]

Run from the repository root. Without --autonomous the run stops at the flag loop.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from prd_agent.errors import StageError
from prd_agent.llm import default_llm
from prd_agent.pipeline import run

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="prd-agent",
        description="Turn a builder's own artifact into a product story that sells.",
    )
    parser.add_argument("artifact_path", help="path to the artifact repository to read")
    parser.add_argument(
        "--autonomous",
        action="store_true",
        help="complete the run and ship the flag footer instead of stopping to ask",
    )
    parser.add_argument(
        "--out",
        default=None,
        help="where to write the story (default: stories/<artifact-name>.md)",
    )
    parser.add_argument(
        "--trends-file",
        default=None,
        help="read trends.json from this path instead of running the live web pass",
    )
    parser.add_argument(
        "--answers-file",
        default=None,
        help="a JSON object of flag id to answer, used instead of reading stdin",
    )
    return parser

def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        llm = default_llm()
        result = run(
            Path(args.artifact_path),
            llm=llm,
            trends_file=Path(args.trends_file) if args.trends_file else None,
            out=Path(args.out) if args.out else None,
            autonomous=args.autonomous,
        )
    except StageError as error:
        print(f"prd-agent: {error}", file=sys.stderr)
        return 2
    if result.awaiting_answers:
        print(f"prd-agent: {len(result.flags)} open flags. Answer them and re-run with --answers-file, "
              f"or re-run with --autonomous to ship them as the footer.")
        for flag in result.flags:
            print(f"  [{flag['id']}] {flag['need']}: {flag['claim']} (unlock: {flag['unlock']})")
        return 0
    print(f"prd-agent: wrote {result.story_path}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
