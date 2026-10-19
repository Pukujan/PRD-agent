"""python -m prd_agent <artifact-path> [--autonomous] [--out stories/<name>.md]

Run from the repository root. Without --autonomous the run stops at the flag loop.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from prd_agent import flags as flags_module
from prd_agent.errors import StageError
from prd_agent.llm import default_llm
from prd_agent.pipeline import answers_from_file, close_flag_loop, run

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="prd-agent",
        description="Turn a builder's own artifact into a product story that sells.",
    )
    parser.add_argument("artifact_path", help="path to the artifact repository to read")
    parser.add_argument(
        "--autonomous",
        action="store_true",
        default=True,
        help="complete the run without stopping to ask (default: True)",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        default=False,
        help="stop at open flags and prompt on stdin instead of running autonomously",
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
        "--no-web",
        action="store_true",
        help="never run the live web pass; requires --trends-file",
    )
    parser.add_argument(
        "--answers-file",
        default=None,
        help="a JSON object of flag id to answer, used instead of reading stdin",
    )
    parser.add_argument(
        "--evals",
        default=None,
        help="where to append the worked example; default evals/story_evals.json",
    )
    parser.add_argument(
        "--hype",
        default=None,
        help="Hype-to-Honesty Dial level: 1000 (electric), 750 (venture), 500 (balanced), 250 (truth)",
    )
    parser.add_argument(
        "--persona",
        default=None,
        help="Audience persona: solopreneur (unicorn/builder), enterprise (cto/vp), normie (consumer/magic)",
    )
    parser.add_argument(
        "--pack",
        action="store_true",
        default=False,
        help="generate the full multi-asset launch pack (copy.json, launch_thread.md, show_hn.md, pitch_deck.md)",
    )
    parser.add_argument(
        "--readme",
        action="store_true",
        default=False,
        help="write the story directly to <artifact-path>/README.md",
    )
    return parser

def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        llm = default_llm()
        is_autonomous = not args.interactive if args.interactive else args.autonomous
        hype_level = args.hype
        persona_choice = args.persona
        if not is_autonomous and hype_level is None:
            from prd_agent.hype import ask_hype_level
            hype_level = ask_hype_level()
        elif hype_level is None:
            hype_level = "1000"

        if not is_autonomous and persona_choice is None:
            from prd_agent.persona import ask_persona
            persona_choice = ask_persona()
        elif persona_choice is None:
            persona_choice = "solopreneur"

        result = run(
            Path(args.artifact_path),
            llm=llm,
            trends_file=Path(args.trends_file) if args.trends_file else None,
            out=Path(args.out) if args.out else None,
            readme=args.readme,
            autonomous=is_autonomous,
            answers=answers_from_file(Path(args.answers_file)) if args.answers_file else None,
            live=not args.no_web,
            evals_path=Path(args.evals) if args.evals else None,
            hype=hype_level,
            persona=persona_choice,
            pack=args.pack,
        )

    except StageError as error:
        print(f"prd-agent: {error}", file=sys.stderr)
        return 2
    if result.awaiting_answers:
        answers = flags_module.ask_questions(result.flags)
        result = close_flag_loop(
            result,
            llm=llm,
            answers=answers,
            hype=hype_level,
            persona=persona_choice,
            pack=args.pack,
        )
        if result.story_path.is_file():
            print(f"prd-agent: wrote {result.story_path}")
            if result.pack is not None:
                print(f"prd-agent: generated launch pack under {result.pack.pack_dir}")
            return 0
        return 0
    print(f"prd-agent: wrote {result.story_path}")
    if result.pack is not None:
        print(f"prd-agent: generated launch pack under {result.pack.pack_dir}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
