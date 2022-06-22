import datetime as dt
import logging
import random
import sys
import time
from os.path import join

from playwright.sync_api import sync_playwright
from pydantic import ValidationError

from lakat.bot import Lakat
from lakat.config import load_config
from lakat.constants import MINUTE


def setup_logger() -> logging.Logger:
    formatter = logging.Formatter("%(asctime)s:%(levelname)s: %(message)s")
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)

    logger = logging.getLogger("lakat")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    return logger


def main():
    logger = setup_logger()

    try:
        config = load_config()
    except FileNotFoundError as err:
        sys.stderr.write(f"error: {err.filename} file not found\n")
        sys.exit(1)
    except ValidationError as err:
        params = [".".join(str(p) for p in error["loc"]) for error in err.errors()]
        sys.stderr.write(f"error: missing config params: {params}\n")
        sys.exit(1)

    logger.info("Starting Lakat..")

    while True:
        for account_cfg in config.accounts:
            with sync_playwright() as playwright:
                context = playwright.chromium.launch_persistent_context(
                    headless=config.headless,
                    user_data_dir=join(config.profiles_path, account_cfg.email),
                )
                context.set_default_timeout(2 * MINUTE)

                lakat = Lakat(config=account_cfg, context=context, logger=logger)
                try:
                    lakat.run()
                except Exception as error:
                    logger.exception(error, exc_info=True)

                    if config.debug:
                        now = dt.datetime.now().isoformat(timespec="seconds")
                        screenshot_path = join(
                            config.screenshots_path, account_cfg.email, f"{now}.png"
                        )
                        lakat.capture_screenshot(path=screenshot_path)

                context.close()

        sleep_duration = 60 * config.interval + random.randint(0, 60)
        logger.info(f"waiting {config.interval} minutes ...")
        time.sleep(sleep_duration)


if __name__ == "__main__":
    main()
