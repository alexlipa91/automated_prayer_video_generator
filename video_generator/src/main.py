import datetime
import logging
import time
import argparse

from vangelo.config import VangeloConfig
from vangelo.runner import VangeloRunner
from santo_del_giorno.runner import SantoRunner
from santo_del_giorno.config import SantoConfig

logger = logging.getLogger("root")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Video generator')
    parser.add_argument('--date', type=datetime.date,
                        default=datetime.datetime.now().date(), help='date to generate the video for')
    parser.add_argument('--test-mode', action='store_true',
                        help='run pipeline test mode (faster). It skips a bunch of steps')
    parser.add_argument('--pipeline', default='vangelo', choices=["vangelo", "santo"],
                        help="Which pipeline to run")

    cli_args = parser.parse_args()

    if cli_args.pipeline == "vangelo":
        runner = VangeloRunner(VangeloConfig(
            date=cli_args.date), test_mode=cli_args.test_mode)
    elif cli_args.pipeline == "santo":
        runner = SantoRunner(SantoConfig(date=cli_args.date),
                             test_mode=cli_args.test_mode)
    else:
        raise ("Unknown pipeline")

    runner.run()
