from .partial import Partial
from .fields import Fields
from .omit import Omit
from . import paths
try:
    from .fastapi import depmap
except ImportError:
    ...