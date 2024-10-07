import click
from loguru import logger
import sys


logger.remove(0)
logger.add(sys.stderr, level="INFO", format="{level} | {message}")
