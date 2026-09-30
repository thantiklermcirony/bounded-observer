"""Source plugins. Importing this package registers every built-in source."""

from .base import SOURCES, Source, register  # noqa: F401
from . import simulator, athena, replay, lsl_in  # noqa: F401
