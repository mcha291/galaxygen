"""Stage implementations. Importing this package registers every implementation.

Shared where identical: a stage lives here once and any model may map a slot to
it. Each stage declares what it reads and publishes (galaxy/core/stage.py).
"""

from . import halo  # noqa: F401  (checkpoint 1, first in the order)
from . import disc  # noqa: F401
from . import assembly  # noqa: F401  (checkpoint 2)
from . import sfh  # noqa: F401  (checkpoint 3)
from . import chemistry  # noqa: F401
from . import vertical  # noqa: F401
from . import chemistry_dtd  # noqa: F401  (the advanced model's chemistry slot)
from . import vertical_alpha  # noqa: F401  (and its vertical slot)
from . import pattern  # noqa: F401  (checkpoint 4, seeded)
from . import systems  # noqa: F401  (checkpoint 5)
from . import planets  # noqa: F401  (checkpoint 6, seeded)
