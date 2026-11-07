"""Simple wall-clock hourly runner with per-hour duplicate protection."""

import logging
import time

from automation.pipeline import AutomationPipeline


def run_hourly(pipeline: AutomationPipeline) -> None:
    logger = logging.getLogger(__name__)
    while True:
        try:
            pipeline.process_title_experiments()
            result = pipeline.run_once()
            logger.info("Hourly pipeline result: %s", result)
        except Exception:
            logger.exception("Hourly pipeline failed; it will retry next hour.")
        seconds_until_next_hour = 3600 - (time.time() % 3600)
        time.sleep(seconds_until_next_hour)
