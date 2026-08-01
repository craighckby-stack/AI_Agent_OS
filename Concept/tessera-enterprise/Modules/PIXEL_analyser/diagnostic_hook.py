import sys
import logging
from pathlib import Path

logger = logging.getLogger("PixelAnalyzerDiagnostic")

def run_diagnostic() -> bool:
    """Validates environment for pixel analysis."""
    try:
        import PIL
        import numpy
        # Check for cache directory
        cache_dir = Path("./cache/pixel_analysis")
        if not cache_dir.exists():
            cache_dir.mkdir(parents=True, exist_ok=True)
        return True
    except ImportError as e:
        logger.error(f"Dependency missing: {e}")
        return False
    except Exception as e:
        logger.error(f"Diagnostic failed: {e}")
        return False

if __name__ == "__main__":
    sys.exit(0 if run_diagnostic() else 1)