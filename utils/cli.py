import argparse
import json
from pathlib import Path

from .resume_agent import parse_resume


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--resume", required=True, help="path to pdf or plain text resume")
    args = p.parse_args()

    facts = parse_resume(Path(args.resume))
    print(json.dumps(facts.model_dump(), indent=2))


if __name__ == "__main__":
    main()

