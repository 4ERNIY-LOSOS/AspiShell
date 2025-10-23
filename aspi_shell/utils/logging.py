import logging
import sys

def setup_logging():
    """
    Настраивает базовую конфигурацию логирования для приложения.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)-8s] %(name)s: %(message)s',
        stream=sys.stderr,
        datefmt='%Y-%m-%d %H:%M:%S'
    )
