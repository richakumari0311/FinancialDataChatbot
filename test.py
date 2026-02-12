"""
Unit tests for Financial Data Chatbot
Run with: python tests.py
"""

import unittest
import pandas as pd
import os
import sys
import tempfile
from io import StringIO

# Import the chatbot
from chatbot import FinancialDataChatbot


class TestFinancialDataChatbot(unittest.TestCase):
    """Test suite for FinancialDataChatbot class."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures that will be used across all tests."""
        # Create temporary directory for test files
        cls.test_dir = tempfile.mkdtemp()
        cls.holdings_path = os.path.join(cls.test_dir, 'test_holdings.csv')
        cls.trades_path = os.path.join(cls.test_dir, 'test_trades.csv')
        
        # Create sample data for testing
        cls.create_sample_data()
        
        # Initialize chatbot with test data
        cls.chatbot = FinancialDataChatbot(cls.holdings_path, cls.trades_path)
    
    @classmethod
    def create_sample_data(cls):
        """Create sample CSV files for testing."""
        # Sample holdings data
        holdings_data = {
            'AsOfDate': ['2023-01-01', '2023-01-01', '2023-01-01'],
            'PortfolioName': ['Fund A', 'Fund A', 'Fund B'],
            'PL_YTD': [10000, 15000, -5000],
            'SecurityId': ['SEC1', 'SEC2', 'SEC3'],
            'Qty': [100, 200, 150]
        }
        
        holdings_df = pd.DataFrame(holdings_data)
        holdings_df.to_csv(cls.holdings_path, index=False)
        
        # Sample trades data
        trades_data = {
            'TradeDate': ['2023-01-01', '2023-01-02', '2023-01-03'],
            'PortfolioName': ['Fund A', 'Fund A', 'Fund B'],
            'SecurityId': ['SEC1', 'SEC2', 'SEC3'],
            'Quantity': [100, 200, 150],
            'Price': [50, 75, 60]
        }
        
        trades_df = pd.DataFrame(trades_data)
        trades_df.to_csv(cls.trades_path, index=False)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test data files."""
        if os.path.exists(cls.holdings_path):
            os.remove(cls.holdings_path)
        if os.path.exists(cls.trades_path):
            os.remove(cls.trades_path)
        if os.path.exists(cls.test_dir):
            os.rmdir(cls.test_dir)
    
    def test_data_loading(self):
        """Test that data loads correctly."""
        self.assertIsNotNone(self.chatbot.holdings_df)
        self.assertIsNotNone(self.chatbot.trades_df)
        self.assertEqual(len(self.chatbot.holdings_df), 3)
        self.assertEqual(len(self.chatbot.trades_df), 3)
    
    def test_total_holdings(self):
        """Test getting total holdings count."""
        count = self.chatbot.get_total_holdings()
        self.assertEqual(count, 3)
    
    def test_total_trades(self):
        """Test getting total trades count."""
        count = self.chatbot.get_total_trades()
        self.assertEqual(count, 3)
    
    def test_holdings_for_specific_fund(self):
        """Test getting holdings count for specific fund."""
        count = self.chatbot.get_total_holdings('Fund A')
        self.assertEqual(count, 2)
        
        count = self.chatbot.get_total_holdings('Fund B')
        self.assertEqual(count, 1)
    
    def test_trades_for_specific_fund(self):
        """Test getting trades count for specific fund."""
        count = self.chatbot.get_total_trades('Fund A')
        self.assertEqual(count, 2)
        
        count = self.chatbot.get_total_trades('Fund B')
        self.assertEqual(count, 1)
    
    def test_nonexistent_fund(self):
        """Test that nonexistent fund returns None."""
        count = self.chatbot.get_total_holdings('Nonexistent Fund')
        self.assertIsNone(count)
        
        count = self.chatbot.get_total_trades('Nonexistent Fund')
        self.assertIsNone(count)
    
    def test_fund_performance(self):
        """Test fund performance calculation."""
        performance = self.chatbot.get_best_performing_funds()
        self.assertIsNotNone(performance)
        
        # Fund A should have higher performance (10000 + 15000 = 25000)
        # Fund B should have -5000
        self.assertEqual(performance['Fund A'], 25000)
        self.assertEqual(performance['Fund B'], -5000)
        
        # Check that Fund A is ranked higher
        self.assertEqual(performance.idxmax(), 'Fund A')
        self.assertEqual(performance.idxmin(), 'Fund B')
    
    def test_total_holdings_question(self):
        """Test answering total holdings questions."""
        answer = self.chatbot.answer_question("What is the total number of holdings?")
        self.assertIn("3", answer)
        
        answer = self.chatbot.answer_question("How many holdings?")
        self.assertIn("3", answer)
    
    def test_total_trades_question(self):
        """Test answering total trades questions."""
        answer = self.chatbot.answer_question("How many trades are there?")
        self.assertIn("3", answer)
        
        answer = self.chatbot.answer_question("Total number of trades")
        self.assertIn("3", answer)
    
    def test_fund_specific_holdings_question(self):
        """Test answering fund-specific holdings questions."""
        answer = self.chatbot.answer_question("Total holdings for Fund A")
        self.assertIn("Fund A", answer)
        self.assertIn("2", answer)
    
    def test_fund_specific_trades_question(self):
        """Test answering fund-specific trades questions."""
        answer = self.chatbot.answer_question("How many trades for Fund B?")
        self.assertIn("Fund B", answer)
        self.assertIn("1", answer)
    
    def test_performance_question(self):
        """Test answering performance comparison questions."""
        answer = self.chatbot.answer_question("Which funds performed better?")
        self.assertIn("Fund A", answer)
        self.assertIn("Fund B", answer)
        self.assertIn("Best performing", answer)
    
    def test_invalid_question(self):
        """Test that invalid questions return appropriate message."""
        answer = self.chatbot.answer_question("What is the weather?")
        self.assertEqual(answer, "Sorry can not find the answer")
        
        answer = self.chatbot.answer_question("Tell me a joke")
        self.assertEqual(answer, "Sorry can not find the answer")
    
    def test_nonexistent_fund_question(self):
        """Test questions about nonexistent funds."""
        answer = self.chatbot.answer_question("Holdings for XYZ Fund")
        self.assertEqual(answer, "Sorry can not find the answer")
    
    def test_case_insensitive_matching(self):
        """Test that fund name matching is case-insensitive."""
        answer = self.chatbot.answer_question("Holdings for fund a")
        self.assertIn("Fund A", answer)
        self.assertIn("2", answer)
        
        answer = self.chatbot.answer_question("Holdings for FUND A")
        self.assertIn("Fund A", answer)
        self.assertIn("2", answer)
    
    def test_extract_fund_name(self):
        """Test fund name extraction from questions."""
        fund = self.chatbot._extract_fund_name("How many holdings for Fund A?")
        self.assertEqual(fund, "Fund A")
        
        fund = self.chatbot._extract_fund_name("Total trades for Fund B")
        self.assertEqual(fund, "Fund B")
        
        fund = self.chatbot._extract_fund_name("What is the weather?")
        self.assertIsNone(fund)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""
    
    def test_missing_files(self):
        """Test handling of missing CSV files."""
        with self.assertRaises(FileNotFoundError):
            FinancialDataChatbot('nonexistent.csv', 'nonexistent.csv')
    
    def test_empty_question(self):
        """Test handling of empty questions."""
        # Create temporary directory and files
        test_dir = tempfile.mkdtemp()
        holdings_path = os.path.join(test_dir, 'temp_holdings.csv')
        trades_path = os.path.join(test_dir, 'temp_trades.csv')
        
        # Create minimal test data
        holdings_data = pd.DataFrame({'PortfolioName': ['Test'], 'PL_YTD': [1000]})
        trades_data = pd.DataFrame({'PortfolioName': ['Test'], 'Quantity': [100]})
        
        holdings_data.to_csv(holdings_path, index=False)
        trades_data.to_csv(trades_path, index=False)
        
        chatbot = FinancialDataChatbot(holdings_path, trades_path)
        
        answer = chatbot.answer_question("")
        self.assertEqual(answer, "Sorry can not find the answer")
        
        # Cleanup
        os.remove(holdings_path)
        os.remove(trades_path)
        os.rmdir(test_dir)


def run_tests():
    """Run all tests and print results."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(TestFinancialDataChatbot))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\nAll tests passed!")
        return 0
    else:
        print("\nSome tests failed.")
        return 1


if __name__ == '__main__':
    sys.exit(run_tests())