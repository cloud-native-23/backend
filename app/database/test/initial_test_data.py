import logging

from .init_test_db import test_init_db
from .test_database import TestingSessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init() -> None:
    db = TestingSessionLocal()
    test_init_db(db)


def main() -> None:
    logger.info("Creating initial test data")
    init()
    logger.info("Initial test data created")


if __name__ == "__main__":
    main()
