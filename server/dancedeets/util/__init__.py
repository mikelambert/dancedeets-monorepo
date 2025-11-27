"""
Util package compatibility layer.
Re-exports modules that were moved but still need to be importable from this location.
"""

# Re-export memcache from services for backward compatibility
from dancedeets.services import memcache  # noqa: F401
