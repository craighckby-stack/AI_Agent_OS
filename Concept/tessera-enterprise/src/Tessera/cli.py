"""
Tessera CLI — command-line entry point.

Usage:
    tessera "<request>"
    tessera --list-modules
    tessera --version
"""

from __future__ import annotations

import argparse
import sys

from tessera import __version__
from tessera.config import TesseraConfig
from tessera.kernel import Kernel


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="tessera",
        description="Tessera — an agent OS where modules are tiles.",
    )
    parser.add_argument("request", nargs="*", help="The request to process")
    parser.add_argument("--list-modules", action="store_true", help="List discovered modules and exit")
    parser.add_argument("--version", action="version", version=f"tessera {__version__}")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    if args.debug:
        import logging
        logging.basicConfig(level=logging.DEBUG)

    config = TesseraConfig.from_env()
    kernel = Kernel(config=config)

    if args.list_modules:
        registry = kernel.registry.discover()
        if not registry:
            print("No modules discovered. Check TESSERA_MODULES_DIR.")
            return 1
        print(f"Discovered {len(registry)} modules in {config.modules_dir}:\n")
        for name, spec in sorted(registry.items()):
            print(f"  {name:<20} cluster_key={spec.cluster_key:<15} purpose={spec.purpose}")
        return 0

    if not args.request:
        parser.print_help()
        return 1

    request = " ".join(args.request)
    try:
        result = kernel.run(request)
        print(result)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
