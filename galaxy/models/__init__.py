"""Model declarations. Importing this package registers every model.

A model is a declaration, not a pipeline: a name, the inputs it accepts, its
constants, and a map from stage slot to implementation (GALAXY_PLAN.md §2).
A third model slots in by adding a module here, not by forking anything.
"""

from . import simple  # noqa: F401  (the default model registers first)
from . import advanced  # noqa: F401
