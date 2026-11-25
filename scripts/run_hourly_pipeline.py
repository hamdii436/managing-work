"""Start one run or the hourly AI music and YouTube scheduler."""

import argparse
import logging
import sys
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from automation.config import Settings
from automation.pipeline import AutomationPipeline
from automation.scheduler import run_hourly


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--once", action="store_true", help="Run the pipeline once.")
    args = parser.parse_args()
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )
    settings = Settings.from_env()
    pipeline = AutomationPipeline(settings)
    if args.once or not settings.scheduler_enabled:
        pipeline.process_title_experiments()
        print(pipeline.run_once())
    else:
        run_hourly(pipeline)


if __name__ == "__main__":
    main()
