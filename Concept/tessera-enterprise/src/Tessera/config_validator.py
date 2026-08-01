"""
CONFIG VALIDATOR
Role: Validates Tessera configuration integrity before runtime.
Integration: Called by TesseraConfig.from_env when diagnostic_mode is enabled.
"""

import os
import logging
from pathlib import Path

logger = logging.getLogger("TesseraConfigValidator")

def validate_tessera_environment(config) -> None:
    """Performs pre-flight checks on configuration paths."""
    paths_to_check = [config.cache_dir, config.modules_dir]
    
    for path_str in paths_to_check:
        path = Path(path_str)
        if not path.exists():
            try:
                path.mkdir(parents=True, exist_ok=True)
                logger.info(f"[DIAGNOSTIC] Created missing directory: {path_str}")
            except Exception as e:
                logger.error(f"[DIAGNOSTIC] Failed to create directory {path_str}: {e}")
        
        if not os.access(path, os.W_OK):
            logger.warning(f"[DIAGNOSTIC] Directory {path_str} is not writable.")