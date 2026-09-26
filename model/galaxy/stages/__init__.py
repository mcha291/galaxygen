"""Stage implementations. Importing this package registers every implementation.

Shared where identical: a stage lives here once and any model may map a slot to
it. Each stage declares what it reads and publishes (galaxy/core/stage.py).
"""

from . import halo  # noqa: F401  (checkpoint 1, first in the order)
from . import disc  # noqa: F401
from . import nucleus  # noqa: F401  (checkpoint 1, seeded: the M_. residual)
from . import assembly  # noqa: F401  (checkpoint 2)
from . import sfh  # noqa: F401  (checkpoint 3)
from . import chemistry  # noqa: F401
from . import vertical  # noqa: F401
from . import chemistry_dtd  # noqa: F401  (the chemistry slot)
from . import vertical_alpha  # noqa: F401  (and its vertical slot)
from . import ism  # noqa: F401  (checkpoint 3, after both chemistries and both verticals)
from . import light  # noqa: F401  (checkpoint 3: the disc's unresolved light)
from . import pattern  # noqa: F401  (checkpoint 3, seeded)
from . import sfh_azimuthal  # noqa: F401  (the sfh slot's second implementation: the azimuthal model, S27)
from . import supernovae  # noqa: F401  (checkpoint 4: supernova rates, S30)
from . import dust  # noqa: F401  (checkpoint 4: dust that scatters, heats and radiates, S31)
from . import systems  # noqa: F401  (checkpoint 5)
from . import clouds  # noqa: F401  (checkpoint 5: the molecular-cloud census, an object class beside stars, S32)
from . import clusters  # noqa: F401  (checkpoint 5: the young star clusters the clouds make, S33)
from . import nebular  # noqa: F401  (checkpoint 5: the clusters' HII regions and the diffuse ionized gas, S35)
from . import stellar_halo  # noqa: F401  (checkpoint 4: the accreted satellites' debris, S34)
from . import globular_clusters  # noqa: F401  (checkpoint 5: the survivors of the bound clusters, S34)
from . import planets  # noqa: F401  (checkpoint 6, seeded)
from . import habitable_zone  # noqa: F401  (checkpoint 6: built and deliberately unjudged, S30)
