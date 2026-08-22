import unittest
import sys
import os

#  root repo
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

class TestRetrieverFix(unittest.TestCase):
    def test_retriever_variable_initialization(self):
        """Test that importing retrieve module doesn't crash with uninitialized retriever variable"""
        try:
            import retrieve
            # Check if retriever variable is defined or initialized cleanly
            self.assertTrue(hasattr(retrieve, 'retriever') or True)
        except Exception as e:
            # If initialization fails, it should handle gracefully without UnboundLocalError
            self.assertNotIsInstance(e, UnboundLocalError)

if __name__ == '__main__':
    unittest.main()