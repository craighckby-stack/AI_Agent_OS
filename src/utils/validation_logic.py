"""
VALIDATION LOGIC ENGINE
Role: Core logic for type-checking and format validation of environment variables.
Delegated from: env_validation_schema.py
"""

from typing import Any, Dict
# Note: ValidationResult is imported locally to avoid circularity if needed, 
# but here we return raw data or a compatible structure.

class ValidationLogic:
    @staticmethod
    def execute_spec_validation(key: str, value: Any, spec: Dict[str, Any]) -> Any:
        from env_validation_schema import ValidationResult
        
        val_type = spec.get("type")
        
        if val_type == "enum":
            options = spec.get("options", [])
            if value in options:
                return ValidationResult(True, f"{key} matches enum", {"key": key, "value": value})
            return ValidationResult(False, f"Invalid {key}: {value}. Expected one of {options}", {"key": key}, remediation=f"Set {key} to one of {options}")

        if val_type == "int":
            try:
                int_val = int(value)
                min_val = spec.get("min", float('-inf'))
                max_val = spec.get("max", float('inf'))
                if min_val <= int_val <= max_val:
                    return ValidationResult(True, f"{key} is valid integer", {"key": key, "value": int_val})
                return ValidationResult(False, f"{key} out of range [{min_val}, {max_val}]", {"key": key})
            except (ValueError, TypeError):
                return ValidationResult(False, f"{key} must be an integer", {"key": key})

        # Default string validation
        is_valid = isinstance(value, str) and len(str(value)) > 0
        return ValidationResult(
            passed=is_valid,
            message=f"Key {key} is valid" if is_valid else f"Key {key} is empty or invalid",
            metadata={"key": key}
        )