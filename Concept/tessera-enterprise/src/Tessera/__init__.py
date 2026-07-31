"""
Tessera — An agent OS where modules are tiles.

Public API:
    from tessera import Kernel, FileCache, LLMRouter
    kernel = Kernel()
    kernel.run("what colour is the sky")
"""

__version__ = "0.1.0"
__all__ = ["Kernel", "FileCache", "LLMRouter", "ModuleRegistry", "RouterCache"]

from tessera.kernel import Kernel
from tessera.cache import FileCache
from tessera.router import LLMRouter
from tessera.modules import ModuleRegistry
from tessera.router_cache import RouterCache
