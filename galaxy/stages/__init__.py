"""Stage implementations. Importing this package registers every implementation.

Shared where identical: a stage lives here once and any model may map a slot to
it. Each stage declares what it reads and publishes (galaxy/core/stage.py).
"""

from . import halo  # noqa: F401  (checkpoint 1, first in the order)
from . import disc  # noqa: F401
