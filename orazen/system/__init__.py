"""system specific and performance tuning"""

from orazen.system.asyncio_config import asyncio_setup
from orazen.system.gc_setup import gc_set_threshold
from orazen.system.set_mp_start_method import set_mp_start_method
from orazen.system.version_info import print_version_info


__all__ = ["asyncio_setup", "gc_set_threshold", "print_version_info", "set_mp_start_method"]
