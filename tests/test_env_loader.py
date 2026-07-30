"""
ARCHITECTURAL TEST SUITE: env_loader.py
Role: Validates environment variable parsing, expansion, and type-casting logic.
Integration: Connects to diagnostic_engine.py for system health reporting during test execution.
"""

import os
import unittest
from pathlib import Path
from env_loader import parse_env_text, expand_variables, get_bool, get_int, get_list
from tests.test_diagnostic_utils import run_test_diagnostics

class TestEnvLoader(unittest.TestCase):
    def setUp(self):
        """Diagnostic Integrity Hook: Ensure environment is stable before testing."""
        self.diag_report = run_test_diagnostics("env_loader_test")
        if self.diag_report['status'] != 'HEALTHY':
            print(f"[DIAGNOSTIC WARNING] Environment unstable: {self.diag_report}")

    def test_parse_env_text(self):
        sample = """
        # This is a comment
        SIMPLE_KEY=simple_value
        QUOTED_KEY="quoted_value"
        SINGLE_QUOTED_KEY='single_quoted_value'
        INLINE_COMMENT_KEY=value_with_comment # this is a comment
        QUOTED_WITH_HASH="value # with hash"
        """
        parsed = parse_env_text(sample)
        self.assertEqual(parsed.get("SIMPLE_KEY"), "simple_value")
        self.assertEqual(parsed.get("QUOTED_KEY"), "quoted_value")
        self.assertEqual(parsed.get("SINGLE_QUOTED_KEY"), "single_quoted_value")
        self.assertEqual(parsed.get("INLINE_COMMENT_KEY"), "value_with_comment")
        self.assertEqual(parsed.get("QUOTED_WITH_HASH"), "value # with hash")

    def test_variable_expansion(self):
        env_dict = {
            "BASE_URL": "http://localhost:3000",
            "API_URL": "${BASE_URL}/api/v1",
            "NESTED_URL": "$API_URL/users"
        }
        expanded = expand_variables(env_dict)
        self.assertEqual(expanded.get("API_URL"), "http://localhost:3000/api/v1")
        self.assertEqual(expanded.get("NESTED_URL"), "http://localhost:3000/api/v1/users")

    def test_getters(self):
        os.environ["TEST_BOOL_TRUE"] = "true"
        os.environ["TEST_BOOL_FALSE"] = "0"
        os.environ["TEST_INT"] = "42"
        os.environ["TEST_LIST"] = "apple, banana, cherry"

        self.assertTrue(get_bool("TEST_BOOL_TRUE"))
        self.assertFalse(get_bool("TEST_BOOL_FALSE"))
        self.assertEqual(get_int("TEST_INT"), 42)
        self.assertEqual(get_list("TEST_LIST"), ["apple", "banana", "cherry"])

if __name__ == "__main__":
    unittest.main()