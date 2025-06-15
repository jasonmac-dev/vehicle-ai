from .background_clutter import BackgroundClutterRule
from .overlays import OverlaysRule
from .staging_rule import StagingRule

ALL_RULES = [
    BackgroundClutterRule(),
    OverlaysRule(),
    StagingRule(),
] 