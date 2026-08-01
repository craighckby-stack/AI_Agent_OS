"""
VARIABLE EXPANSION ENGINE
Role: Handles recursive variable expansion with cycle detection for .env files.
Siphoned from: High-scale configuration patterns (Microsoft/Vercel).
"""

import re
from typing import Dict, Optional

class VariableExpander:
    VAR_PATTERN = re.compile(r'\$\{([A-Za-z0-9_]+)\}|\$([A-Za-z0-9_]+)')
    MAX_RECURSION = 10

    @classmethod
    def expand(cls, env_dict: Dict[str, str], os_env: Dict[str, str]) -> Dict[str, str]:
        expanded: Dict[str, str] = {}
        
        def _resolve(value: str, depth: int) -> str:
            if depth > cls.MAX_RECURSION:
                return value  # Stop expansion to prevent infinite loops
            
            def replace_match(match: re.Match) -> str:
                var_name = match.group(1) or match.group(2)
                # Priority: OS Env -> Current Expanded -> Original Dict
                res = os_env.get(var_name, expanded.get(var_name, env_dict.get(var_name, "")))
                return _resolve(res, depth + 1) if '$' in res else res

            return cls.VAR_PATTERN.sub(replace_match, value)

        for key, val in env_dict.items():
            expanded[key] = _resolve(val, 0)
            
        return expanded