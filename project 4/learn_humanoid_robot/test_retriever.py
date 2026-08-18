#!/usr/bin/env python3
"""
Unit tests to verify the retrieve.py fix for the undefined 'retriever'
variable in the finally block.
"""

import unittest
from unittest.mock import patch, MagicMock


class TestRetrieveFinallyBlock(unittest.TestCase):
    """Tests that the finally block in retrieve.py handles a None retriever."""

    @patch("retrieve.RAGRetriever")
    @patch("retrieve.Config")
    def test_finally_does_not_crash_when_retriever_init_fails(self, mock_config, mock_retriever_cls):
        """If RAGRetriever() raises, retriever stays None and finally must not crash."""
        mock_config.validate.return_value = False
        mock_config.validate_config_values.return_value = []

        # We must catch SystemExit because sys.exit(1) is called on validation failure
        with self.assertRaises(SystemExit):
            from retrieve import main
            main()

        # RAGRetriever() should never have been instantiated
        mock_retriever_cls.assert_not_called()

    @patch("retrieve.RAGRetriever")
    @patch("retrieve.Config")
    def test_finally_calls_close_when_retriever_is_initialized(self, mock_config, mock_retriever_cls):
        """When retriever is successfully created, finally must call close()."""
        mock_config.validate.return_value = True
        mock_config.validate_config_values.return_value = []

        mock_retriever = MagicMock()
        mock_retriever.validate_embedding_compatibility.return_value = True
        mock_retriever.retrieve_chunks.return_value = []
        mock_retriever_cls.return_value = mock_retriever

        # Run main with no query and no --validate to hit the default usage branch
        with patch("retrieve.sys.argv", ["retrieve.py"]):
            from retrieve import main
            main()

        mock_retriever.close.assert_called_once()

    def test_retriever_variable_initialized_before_try(self):
        """Verify the source has 'retriever = None' before the try block."""
        with open("retrieve.py", "r", encoding="utf-8") as f:
            lines = f.readlines()
        try_idx = None
        init_idx = None
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped == "try:" and try_idx is None:
                try_idx = i
            if "retriever = None" in line and init_idx is None:
                init_idx = i
        self.assertIsNotNone(try_idx, "try block not found")
        self.assertIsNotNone(init_idx, "'retriever = None' not found before try")
        self.assertLess(init_idx, try_idx,
                        "'retriever = None' must appear before the try block")


if __name__ == "__main__":
    unittest.main()
